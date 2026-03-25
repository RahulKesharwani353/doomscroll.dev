"""Cache service with key generation and serialization."""
import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, TypeVar

from app.cache.backends import CacheBackend, get_cache_backend
from app.config import settings
from shared.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheService:
    """Cache service with automatic serialization and thundering herd prevention."""

    def __init__(self, backend: CacheBackend):
        self._backend = backend
        self._key_locks: Dict[str, asyncio.Lock] = {}
        self._locks_lock = asyncio.Lock()

    @staticmethod
    def _build_key(*parts: Any) -> str:
        """Build a cache key from parts."""
        return ":".join(str(p) for p in parts if p is not None)

    def articles_key(
        self,
        page: int,
        limit: int,
        source: Optional[str] = None
    ) -> str:
        """Generate cache key for article list."""
        return self._build_key("articles", "list", f"p{page}", f"l{limit}", source or "all")

    def search_key(
        self,
        query: str,
        page: int,
        limit: int,
        source: Optional[str] = None
    ) -> str:
        """Generate cache key for search results."""
        normalized_query = query.lower().strip()
        return self._build_key("articles", "search", normalized_query, f"p{page}", f"l{limit}", source or "all")

    def sources_key(self) -> str:
        """Generate cache key for sources list."""
        return "sources:list"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache, deserializing JSON if needed."""
        value = await self._backend.get(key)
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set value in cache, serializing to JSON if needed."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        await self._backend.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete a specific key."""
        return await self._backend.delete(key)

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return await self._backend.get_stats()

    async def _get_key_lock(self, key: str) -> asyncio.Lock:
        """Get or create a lock for a specific cache key."""
        async with self._locks_lock:
            if key not in self._key_locks:
                self._key_locks[key] = asyncio.Lock()
            return self._key_locks[key]

    async def _cleanup_key_lock(self, key: str):
        """Clean up a key lock if no longer needed."""
        async with self._locks_lock:
            if key in self._key_locks and not self._key_locks[key].locked():
                del self._key_locks[key]

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get value from cache or compute and store it with per-key locking."""
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit: {key}")
            return cached

        key_lock = await self._get_key_lock(key)
        async with key_lock:
            cached = await self.get(key)
            if cached is not None:
                logger.debug(f"Cache hit (after lock): {key}")
                return cached

            logger.debug(f"Cache miss: {key}")
            value = await factory()
            await self.set(key, value, ttl)
            return value


_cache_service: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """Get singleton CacheService instance."""
    global _cache_service
    if _cache_service is None:
        backend = await get_cache_backend()
        _cache_service = CacheService(backend)
        logger.info("CacheService initialized")
    return _cache_service


def get_cache_service_sync() -> CacheService:
    """Synchronous getter for dependency injection (must be called after async init)."""
    if _cache_service is None:
        raise RuntimeError("CacheService not initialized. Call get_cache_service() first.")
    return _cache_service
