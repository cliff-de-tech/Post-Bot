"""
Backend Middleware Module

Provides rate limiting, request validation, and CORS configuration for the LinkedIn Post Bot API.
"""

import time
import functools
from typing import Dict, Optional, Callable
from collections import defaultdict
import threading


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks requests per user/IP and enforces limits.
    """
    
    def __init__(self, max_requests: int = 50, window_seconds: int = 3600):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the identifier is allowed.
        
        Args:
            identifier: User ID or IP address
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            # Check limit
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Record new request
            self.requests[identifier].append(now)
            return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            current_requests = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            return max(0, self.max_requests - len(current_requests))
    
    def get_reset_time(self, identifier: str) -> Optional[float]:
        """Get time until rate limit resets."""
        with self._lock:
            if not self.requests[identifier]:
                return None
            
            oldest_request = min(self.requests[identifier])
            return oldest_request + self.window_seconds - time.time()


# Global rate limiters for different endpoints
post_generation_limiter = RateLimiter(max_requests=10, window_seconds=3600)  # 10/hour
publish_limiter = RateLimiter(max_requests=5, window_seconds=3600)  # 5/hour
api_limiter = RateLimiter(max_requests=100, window_seconds=3600)  # 100/hour general


def rate_limit(limiter: RateLimiter):
    """
    Decorator to apply rate limiting to a function.
    
    Usage:
        @rate_limit(post_generation_limiter)
        def generate_post(user_id: str, ...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get user_id from kwargs or first arg
            user_id = kwargs.get('user_id') or (args[0] if args else 'anonymous')
            
            if not limiter.is_allowed(str(user_id)):
                remaining = limiter.get_remaining(str(user_id))
                reset_time = limiter.get_reset_time(str(user_id))
                raise RateLimitExceededError(
                    f"Rate limit exceeded. Remaining: {remaining}. "
                    f"Reset in: {int(reset_time)} seconds" if reset_time else ""
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""
    pass


def validate_api_key(api_key: str, key_type: str = 'groq') -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: The API key to validate
        key_type: Type of API key ('groq', 'unsplash', 'linkedin')
        
    Returns:
        True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    api_key = api_key.strip()
    
    if key_type == 'groq':
        # Groq keys start with 'gsk_'
        return api_key.startswith('gsk_') and len(api_key) > 20
    elif key_type == 'unsplash':
        # Unsplash keys are typically 64 characters
        return len(api_key) >= 32
    elif key_type == 'linkedin':
        # LinkedIn client IDs are alphanumeric
        return len(api_key) >= 10 and api_key.isalnum()
    
    return True


def validate_github_username(username: str) -> bool:
    """
    Validate GitHub username format.
    
    Args:
        username: The GitHub username to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not username or not isinstance(username, str):
        return False
    
    username = username.strip()
    
    # GitHub usernames: 1-39 chars, alphanumeric or hyphens, can't start/end with hyphen
    if len(username) < 1 or len(username) > 39:
        return False
    
    if username.startswith('-') or username.endswith('-'):
        return False
    
    return all(c.isalnum() or c == '-' for c in username)


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '')
    
    return text.strip()


# CORS configuration
CORS_CONFIG = {
    'allowed_origins': [
        'http://localhost:3000',
        'http://localhost:8000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8000',
    ],
    'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allowed_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
    'allow_credentials': True,
    'max_age': 86400,  # 24 hours
}


def get_cors_headers(origin: Optional[str] = None) -> Dict[str, str]:
    """
    Get CORS headers for response.
    
    Args:
        origin: Request origin header
        
    Returns:
        Dictionary of CORS headers
    """
    headers = {}
    
    if origin and origin in CORS_CONFIG['allowed_origins']:
        headers['Access-Control-Allow-Origin'] = origin
    elif origin and origin.endswith('.vercel.app'):
        # Allow Vercel deployments
        headers['Access-Control-Allow-Origin'] = origin
    else:
        headers['Access-Control-Allow-Origin'] = CORS_CONFIG['allowed_origins'][0]
    
    headers['Access-Control-Allow-Methods'] = ', '.join(CORS_CONFIG['allowed_methods'])
    headers['Access-Control-Allow-Headers'] = ', '.join(CORS_CONFIG['allowed_headers'])
    
    if CORS_CONFIG['allow_credentials']:
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    headers['Access-Control-Max-Age'] = str(CORS_CONFIG['max_age'])
    
    return headers
