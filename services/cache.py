"""
Simple File-Based Cache for GitHub Activity

Provides caching to reduce GitHub API calls.
"""

import json
import time
import os
from typing import Optional, Any, Dict
from pathlib import Path
import hashlib


class FileCache:
    """
    Simple file-based cache with TTL support.
    """
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        # Hash the key to create a valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() > data.get('expires_at', 0):
                self.delete(key)
                return None
            
            return data.get('value')
        except (json.JSONDecodeError, IOError):
            self.delete(key)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)
        ttl = ttl if ttl is not None else self.default_ttl
        
        try:
            data = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time(),
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            
            return True
        except (IOError, TypeError):
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(key)
        
        try:
            if cache_path.exists():
                cache_path.unlink()
                return True
        except IOError:
            pass
        
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
        except IOError:
            pass
        
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if time.time() > data.get('expires_at', 0):
                        cache_file.unlink()
                        count += 1
                except (json.JSONDecodeError, IOError):
                    cache_file.unlink()
                    count += 1
        except IOError:
            pass
        
        return count


# Global cache instance for GitHub activity
github_cache = FileCache(cache_dir=".cache/github", default_ttl=300)  # 5 minute cache


def cache_github_activity(username: str, activities: list, ttl: int = 300) -> bool:
    """
    Cache GitHub activity for a user.
    
    Args:
        username: GitHub username
        activities: List of activity data
        ttl: Cache TTL in seconds
        
    Returns:
        True if cached successfully
    """
    key = f"github_activity_{username}"
    return github_cache.set(key, activities, ttl)


def get_cached_github_activity(username: str) -> Optional[list]:
    """
    Get cached GitHub activity for a user.
    
    Args:
        username: GitHub username
        
    Returns:
        Cached activities or None
    """
    key = f"github_activity_{username}"
    return github_cache.get(key)


def invalidate_github_cache(username: str) -> bool:
    """
    Invalidate GitHub activity cache for a user.
    
    Args:
        username: GitHub username
        
    Returns:
        True if invalidated
    """
    key = f"github_activity_{username}"
    return github_cache.delete(key)
