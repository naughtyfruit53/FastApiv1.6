# app/core/cache.py

"""
Simple in-memory cache manager for entitlements and other data.
In production, this should be replaced with Redis or similar.
"""

from typing import Any, Optional
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            # Check expiry
            if key in self._expiry:
                if datetime.utcnow() < self._expiry[key]:
                    return self._cache[key]
                else:
                    # Expired, remove
                    del self._cache[key]
                    del self._expiry[key]
            else:
                return self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (in seconds)"""
        self._cache[key] = value
        if ttl:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
        logger.debug(f"Cached key: {key}, ttl: {ttl}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
        logger.debug(f"Deleted cache key: {key}")
    
    async def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        logger.debug("Cache cleared")
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, expiry in self._expiry.items()
            if now >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]
            del self._expiry[key]
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache manager instance
cache_manager = CacheManager()


async def start_cache_cleanup_task():
    """Background task to cleanup expired cache entries"""
    while True:
        await asyncio.sleep(60)  # Run every minute
        await cache_manager.cleanup_expired()
