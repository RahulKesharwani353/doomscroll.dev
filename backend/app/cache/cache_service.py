"""
High-level cache service for business logic.
Provides typed caching methods with key generation and serialization.
"""
import json
from typing import Any, Callable, Dict, List, Optional, TypeVar

from app.cache.backends import CacheBackend, get_cache_backend
from app.config import settings
from shared.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheService:
    """
    High-level cache service that wraps a cache backend.
    Provides business-friendly caching methods with automatic serialization.
    """

    def __init__(self, backend: CacheBackend):
        self._backend = backend

    @staticmethod
    def _build_key(*parts: Any) -> str:
        """Build a cache key from parts."""
        return ":".join(str(p) for p in parts if p is not None)

    # Article cache methods
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
        # Normalize query for consistent caching
        normalized_query = query.lower().strip()
        return self._build_key("articles", "search", normalized_query, f"p{page}", f"l{limit}", source or "all")

    def sources_key(self) -> str:
        """Generate cache key for sources list."""
        return "sources:list"

    # Generic cache operations with serialization
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache, deserializing JSON if needed."""
        value = await self._backend.get(key)
        if value is None:
            return None

        # If it's a string that looks like JSON, try to deserialize
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
        # Serialize complex objects to JSON
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        await self._backend.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete a specific key."""
        return await self._backend.delete(key)

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return await self._backend.get_stats()

    # Convenience method for cache-aside pattern
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or compute and store it.

        Args:
            key: Cache key
            factory: Async function to compute value if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or computed value
        """
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit: {key}")
            return cached

        logger.debug(f"Cache miss: {key}")
        value = await factory()
        await self.set(key, value, ttl)
        return value


# Singleton instance
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
    """
    Synchronous getter for dependency injection.
    Note: Must be called after async initialization.
    """
    if _cache_service is None:
        raise RuntimeError("CacheService not initialized. Call get_cache_service() first.")
    return _cache_service
