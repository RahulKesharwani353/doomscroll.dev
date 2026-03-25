"""Cache backend implementations."""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache by key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL in seconds."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from cache. Returns True if key existed."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class InMemoryCache(CacheBackend):
    """In-memory cache with TTL support."""

    _instance: Optional["InMemoryCache"] = None
    _lock_instance = asyncio.Lock()

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    @classmethod
    async def get_instance(cls) -> "InMemoryCache":
        """Get singleton instance of InMemoryCache."""
        async with cls._lock_instance:
            if cls._instance is None:
                cls._instance = cls()
                logger.info("InMemoryCache instance created")
            return cls._instance

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache. Returns None if key doesn't exist or is expired."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry == 0 or expiry > time.time():
                    self._hits += 1
                    return value
                del self._cache[key]
            self._misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache. ttl=None means no expiration."""
        async with self._lock:
            expiry = time.time() + ttl if ttl else 0
            self._cache[key] = (value, expiry)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"Cache cleared: {count} entries removed")

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            if key in self._cache:
                _, expiry = self._cache[key]
                if expiry == 0 or expiry > time.time():
                    return True
                del self._cache[key]
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry > 0 and expiry <= current_time
            ]
            for key in expired_keys:
                del self._cache[key]

            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "backend": "memory",
                "entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
            }

    async def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry > 0 and expiry <= current_time
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)


_cache_backend: Optional[CacheBackend] = None


async def get_cache_backend() -> CacheBackend:
    """Get cache backend singleton based on configuration."""
    global _cache_backend

    if _cache_backend is not None:
        return _cache_backend

    from app.config import settings

    if settings.CACHE_BACKEND == "memory":
        _cache_backend = await InMemoryCache.get_instance()
        logger.info("Using InMemoryCache backend")
    elif settings.CACHE_BACKEND == "redis":
        raise NotImplementedError("Redis cache backend not implemented yet")
    else:
        raise ValueError(f"Unknown cache backend: {settings.CACHE_BACKEND}")

    return _cache_backend
