"""
Redis Client — connection + cache helper functions with in-memory fallback.
All external API calls use Redis cache with TTL fallback (RULE-05).
When Redis is unavailable, an in-memory dict cache is used as fallback.
"""

import json
import logging
import time
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Global Redis instance
_redis = None
_redis_available = None  # None = not yet checked, True/False = checked

# In-memory fallback cache: key -> (value, expire_timestamp)
_memory_cache: dict[str, tuple[str, float]] = {}


class MemoryCache:
    """Simple in-memory cache that mimics Redis async interface for fallback."""

    async def get(self, key: str) -> Optional[str]:
        if key in _memory_cache:
            value, expires = _memory_cache[key]
            if expires == 0 or time.time() < expires:
                return value
            else:
                del _memory_cache[key]
        return None

    async def set(self, key: str, value: str, ex: int = 1800):
        expire_at = time.time() + ex if ex > 0 else 0
        _memory_cache[key] = (value, expire_at)

    async def ping(self):
        return True

    async def close(self):
        _memory_cache.clear()


_memory_fallback = MemoryCache()


async def get_redis():
    """Get or create the Redis connection. Falls back to in-memory cache."""
    global _redis, _redis_available

    if _redis_available is False:
        return _memory_fallback

    if _redis is None:
        try:
            from redis.asyncio import Redis
            from backend.config.settings import settings
            _redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=3,
            )
            await _redis.ping()
            _redis_available = True
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}), using in-memory cache fallback")
            _redis_available = False
            _redis = None
            return _memory_fallback

    return _redis


async def close_redis():
    """Close Redis connection on shutdown."""
    global _redis, _redis_available
    if _redis and _redis_available:
        try:
            await _redis.close()
        except Exception:
            pass
    _redis = None
    _redis_available = None
    _memory_cache.clear()


async def cache_get(key: str) -> Optional[str]:
    """Get a value from cache. Returns None on miss or error."""
    try:
        client = await get_redis()
        return await client.get(key)
    except Exception as e:
        logger.warning(f"Cache GET failed for key={key}: {e}")
        return None


async def cache_set(key: str, value: str, ttl: int = 1800):
    """Set a value in cache with TTL in seconds."""
    try:
        client = await get_redis()
        await client.set(key, value, ex=ttl)
    except Exception as e:
        logger.warning(f"Cache SET failed for key={key}: {e}")


async def cache_get_json(key: str) -> Optional[dict]:
    """Get a JSON value from cache."""
    raw = await cache_get(key)
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


async def cache_set_json(key: str, value: dict, ttl: int = 1800):
    """Set a JSON value in cache."""
    await cache_set(key, json.dumps(value), ttl)


async def cache_get_stale(key: str) -> Optional[str]:
    """
    Get value from cache ignoring TTL (stale cache).
    Used as resilience fallback when API + fresh cache both fail.
    We store a parallel key with no TTL for this purpose.
    """
    return await cache_get(f"stale:{key}")


async def cache_set_with_stale(key: str, value: str, ttl: int = 1800):
    """Set both TTL'd and stale copies of a cache value."""
    await cache_set(key, value, ttl)
    await cache_set(f"stale:{key}", value, ttl=86400 * 7)  # stale copy lasts 7 days
