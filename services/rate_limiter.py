"""
Rate Limiter Service - Per-User Request Throttling

Implements Redis-backed rate limiting for production use with an
in-memory fallback for local development.

CONFIGURATION:
    - Default: 60 requests per minute per user
    - Configurable via environment variables
    - REDIS_URL: Redis connection for cross-worker rate limiting

DESIGN:
    - Redis-backed sliding window (production)
    - In-memory fallback (development / Redis unavailable)
    - Keyed by user_id for multi-tenant isolation
"""
import time
import os
from collections import defaultdict
from threading import Lock
import logging

logger = logging.getLogger(__name__)

# Configuration
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '60'))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Per-endpoint rate limit configuration
POST_GENERATION_RATE_LIMIT = int(os.getenv('POST_GENERATION_RATE_LIMIT', '10'))
POST_GENERATION_RATE_WINDOW = int(os.getenv('POST_GENERATION_RATE_WINDOW', '3600'))
PUBLISH_RATE_LIMIT = int(os.getenv('PUBLISH_RATE_LIMIT', '5'))
PUBLISH_RATE_WINDOW = int(os.getenv('PUBLISH_RATE_WINDOW', '3600'))

# Try to connect to Redis
_redis_client = None
try:
    import redis
    _redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _redis_client.ping()
    logger.info("Rate limiter using Redis backend")
except Exception as e:
    _redis_client = None
    logger.warning("Redis unavailable for rate limiter, using in-memory fallback: %s", e)


class RateLimiter:
    """
    Per-user rate limiter using sliding window.

    Uses Redis sorted sets in production for cross-worker consistency.
    Falls back to in-memory storage when Redis is unavailable.

    MULTI-TENANT ISOLATION:
        - Each user has their own request counter
        - No cross-user rate limit sharing
    """

    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS,
                 window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory fallback structures
        self._mem_requests = defaultdict(list)
        self._lock = Lock()

    def _redis_is_allowed(self, user_id: str) -> tuple[bool, dict]:
        """Redis-backed sliding window check using sorted sets."""
        key = f"ratelimit:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds
        pipe = _redis_client.pipeline(True)
        try:
            # Remove expired entries, count remaining, add new entry
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window_seconds + 1)
            results = pipe.execute()
            request_count = results[1]  # zcard result

            remaining = max(0, self.max_requests - request_count)

            if request_count >= self.max_requests:
                # Over limit — remove the entry we just added
                _redis_client.zrem(key, str(now))
                return False, {
                    "allowed": False,
                    "remaining": 0,
                    "limit": self.max_requests,
                    "reset_at": int(now + self.window_seconds),
                    "retry_after": self.window_seconds,
                }

            return True, {
                "allowed": True,
                "remaining": remaining - 1,
                "limit": self.max_requests,
                "reset_at": int(now + self.window_seconds),
            }
        except Exception as e:
            logger.warning("Redis rate-limit error, allowing request: %s", e)
            return True, {"allowed": True, "remaining": -1, "limit": self.max_requests, "reset_at": 0}

    def _mem_is_allowed(self, user_id: str) -> tuple[bool, dict]:
        """In-memory sliding window fallback."""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            self._mem_requests[user_id] = [
                ts for ts in self._mem_requests[user_id]
                if ts > window_start
            ]

            request_count = len(self._mem_requests[user_id])
            remaining = max(0, self.max_requests - request_count)

            if request_count >= self.max_requests:
                oldest = self._mem_requests[user_id][0] if self._mem_requests[user_id] else current_time
                reset_at = oldest + self.window_seconds
                return False, {
                    "allowed": False,
                    "remaining": 0,
                    "limit": self.max_requests,
                    "reset_at": int(reset_at),
                    "retry_after": int(reset_at - current_time),
                }

            self._mem_requests[user_id].append(current_time)
            return True, {
                "allowed": True,
                "remaining": remaining - 1,
                "limit": self.max_requests,
                "reset_at": int(current_time + self.window_seconds),
            }

    def is_allowed(self, user_id: str) -> tuple[bool, dict]:
        """
        Check if a request is allowed for a user.

        Args:
            user_id: Clerk user ID (tenant isolation key)

        Returns:
            (allowed: bool, info: dict with remaining, reset_at, etc.)
        """
        if not user_id:
            user_id = "anonymous"

        if _redis_client is not None:
            return self._redis_is_allowed(user_id)
        return self._mem_is_allowed(user_id)

    def get_status(self, user_id: str) -> dict:
        """Get current rate limit status for a user without consuming quota."""
        if _redis_client is not None:
            try:
                key = f"ratelimit:{user_id}"
                now = time.time()
                window_start = now - self.window_seconds
                _redis_client.zremrangebyscore(key, 0, window_start)
                count = _redis_client.zcard(key)
                remaining = max(0, self.max_requests - count)
                return {
                    "remaining": remaining,
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "used": count,
                }
            except Exception:
                pass

        # Fallback
        current_time = time.time()
        window_start = current_time - self.window_seconds
        with self._lock:
            requests = [ts for ts in self._mem_requests.get(user_id, []) if ts > window_start]
            remaining = max(0, self.max_requests - len(requests))
            return {
                "remaining": remaining,
                "limit": self.max_requests,
                "window_seconds": self.window_seconds,
                "used": len(requests),
            }


# Global rate limiter instance
rate_limiter = RateLimiter()

# Per-endpoint limiters (used by backend routes)
post_generation_limiter = RateLimiter(
    max_requests=POST_GENERATION_RATE_LIMIT,
    window_seconds=POST_GENERATION_RATE_WINDOW,
)
publish_limiter = RateLimiter(
    max_requests=PUBLISH_RATE_LIMIT,
    window_seconds=PUBLISH_RATE_WINDOW,
)


def check_rate_limit(user_id: str) -> tuple[bool, dict]:
    """
    Convenience function to check rate limit.

    Returns:
        (allowed: bool, info: dict)
    """
    return rate_limiter.is_allowed(user_id)


def get_rate_limit_status(user_id: str) -> dict:
    """Get rate limit status without consuming quota."""
    return rate_limiter.get_status(user_id)
