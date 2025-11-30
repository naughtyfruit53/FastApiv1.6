# app/services/org_cache_service.py
"""
Organization Cache Service
Provides in-memory caching for organization data to reduce database queries.
Uses a simple TTL-based cache with configurable expiration.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)

# In-memory cache storage
_org_cache: Dict[str, Dict[str, Any]] = {}

# Cache configuration
DEFAULT_TTL_SECONDS = 60  # 60 seconds default TTL


def _get_cache_key(org_id: int, user_id: int) -> str:
    """Generate a cache key for organization data."""
    return f"org:{org_id}:user:{user_id}"


def _get_etag(data: Dict[str, Any]) -> str:
    """Generate an ETag for the organization data."""
    # Use updated_at and enabled_modules to generate ETag
    updated_at = data.get('updated_at', '')
    enabled_modules = str(data.get('enabled_modules', {}))
    content = f"{updated_at}:{enabled_modules}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_organization(org_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get cached organization data if available and not expired.
    
    Args:
        org_id: Organization ID
        user_id: User ID (for user-specific caching)
        
    Returns:
        Cached organization data or None if not cached/expired
    """
    cache_key = _get_cache_key(org_id, user_id)
    
    if cache_key not in _org_cache:
        return None
    
    cached = _org_cache[cache_key]
    
    # Check if cache has expired
    if datetime.utcnow() > cached.get('expires_at', datetime.utcnow()):
        # Cache expired, remove it
        del _org_cache[cache_key]
        logger.debug(f"Organization cache expired for org_id={org_id}, user_id={user_id}")
        return None
    
    logger.debug(f"Organization cache hit for org_id={org_id}, user_id={user_id}")
    return cached.get('data')


def set_cached_organization(org_id: int, user_id: int, data: Dict[str, Any], ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
    """
    Cache organization data with TTL.
    
    Args:
        org_id: Organization ID
        user_id: User ID (for user-specific caching)
        data: Organization data to cache
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        ETag for the cached data
    """
    cache_key = _get_cache_key(org_id, user_id)
    etag = _get_etag(data)
    
    _org_cache[cache_key] = {
        'data': data,
        'etag': etag,
        'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds),
        'cached_at': datetime.utcnow()
    }
    
    logger.debug(f"Organization cached for org_id={org_id}, user_id={user_id}, ttl={ttl_seconds}s")
    return etag


def get_cached_etag(org_id: int, user_id: int) -> Optional[str]:
    """
    Get the ETag for cached organization data.
    
    Args:
        org_id: Organization ID
        user_id: User ID
        
    Returns:
        ETag string or None if not cached
    """
    cache_key = _get_cache_key(org_id, user_id)
    
    if cache_key not in _org_cache:
        return None
    
    cached = _org_cache[cache_key]
    
    # Check if cache has expired
    if datetime.utcnow() > cached.get('expires_at', datetime.utcnow()):
        return None
    
    return cached.get('etag')


def invalidate_organization_cache(org_id: int, user_id: Optional[int] = None) -> int:
    """
    Invalidate cached organization data.
    
    Args:
        org_id: Organization ID
        user_id: Optional user ID. If None, invalidates all caches for the org.
        
    Returns:
        Number of cache entries invalidated
    """
    invalidated = 0
    keys_to_remove = []
    
    if user_id is not None:
        # Invalidate specific user cache
        cache_key = _get_cache_key(org_id, user_id)
        if cache_key in _org_cache:
            keys_to_remove.append(cache_key)
    else:
        # Invalidate all caches for this organization
        # Create a snapshot of keys to avoid modification during iteration
        prefix = f"org:{org_id}:"
        for key in list(_org_cache.keys()):
            if key.startswith(prefix):
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        if key in _org_cache:  # Double-check key exists before deleting
            del _org_cache[key]
            invalidated += 1
    
    if invalidated > 0:
        logger.info(f"Invalidated {invalidated} organization cache entries for org_id={org_id}")
    
    return invalidated


def clear_all_org_cache() -> int:
    """
    Clear all organization caches.
    
    Returns:
        Number of cache entries cleared
    """
    count = len(_org_cache)
    _org_cache.clear()
    logger.info(f"Cleared all {count} organization cache entries")
    return count


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    now = datetime.utcnow()
    active_entries = sum(1 for v in _org_cache.values() if v.get('expires_at', now) > now)
    expired_entries = len(_org_cache) - active_entries
    
    return {
        'total_entries': len(_org_cache),
        'active_entries': active_entries,
        'expired_entries': expired_entries,
        'default_ttl_seconds': DEFAULT_TTL_SECONDS
    }


# Entitlement-specific caching with longer TTL
ENTITLEMENT_TTL_SECONDS = 300  # 5 minutes for entitlements

_entitlement_cache: Dict[str, Dict[str, Any]] = {}


def _get_entitlement_cache_key(org_id: int) -> str:
    """Generate a cache key for organization entitlements."""
    return f"entitlement:org:{org_id}"


def get_cached_entitlements(org_id: int) -> Optional[Dict[str, Any]]:
    """
    Get cached entitlements for an organization.
    
    Args:
        org_id: Organization ID
        
    Returns:
        Cached entitlements data or None if not cached/expired
    """
    cache_key = _get_entitlement_cache_key(org_id)
    
    if cache_key not in _entitlement_cache:
        return None
    
    cached = _entitlement_cache[cache_key]
    
    # Check if cache has expired
    if datetime.utcnow() > cached.get('expires_at', datetime.utcnow()):
        del _entitlement_cache[cache_key]
        logger.debug(f"Entitlement cache expired for org_id={org_id}")
        return None
    
    logger.debug(f"Entitlement cache hit for org_id={org_id}")
    return cached.get('data')


def set_cached_entitlements(org_id: int, data: Dict[str, Any], ttl_seconds: int = ENTITLEMENT_TTL_SECONDS) -> None:
    """
    Cache entitlements data for an organization.
    
    Args:
        org_id: Organization ID
        data: Entitlements data to cache
        ttl_seconds: Time-to-live in seconds (default 5 minutes)
    """
    cache_key = _get_entitlement_cache_key(org_id)
    
    _entitlement_cache[cache_key] = {
        'data': data,
        'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds),
        'cached_at': datetime.utcnow()
    }
    
    logger.debug(f"Entitlements cached for org_id={org_id}, ttl={ttl_seconds}s")


def invalidate_entitlement_cache(org_id: int) -> bool:
    """
    Invalidate cached entitlements for an organization.
    
    Args:
        org_id: Organization ID
        
    Returns:
        True if cache was invalidated, False if no cache existed
    """
    cache_key = _get_entitlement_cache_key(org_id)
    
    if cache_key in _entitlement_cache:
        del _entitlement_cache[cache_key]
        logger.info(f"Invalidated entitlement cache for org_id={org_id}")
        return True
    
    return False


def clear_all_entitlement_cache() -> int:
    """
    Clear all entitlement caches.
    
    Returns:
        Number of cache entries cleared
    """
    count = len(_entitlement_cache)
    _entitlement_cache.clear()
    logger.info(f"Cleared all {count} entitlement cache entries")
    return count


def get_entitlement_cache_stats() -> Dict[str, Any]:
    """
    Get entitlement cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    now = datetime.utcnow()
    active_entries = sum(1 for v in _entitlement_cache.values() if v.get('expires_at', now) > now)
    expired_entries = len(_entitlement_cache) - active_entries
    
    return {
        'total_entries': len(_entitlement_cache),
        'active_entries': active_entries,
        'expired_entries': expired_entries,
        'default_ttl_seconds': ENTITLEMENT_TTL_SECONDS
    }
