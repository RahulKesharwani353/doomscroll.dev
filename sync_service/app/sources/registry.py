from typing import Dict, Optional, Type, List

from sync_service.app.sources.base_client import BaseSourceClient
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class SourceRegistry:
    """Registry for source client classes.

    Maps source slugs to their client classes for dynamic instantiation.
    This allows the sync service to look up which client to use based on
    the source configuration in the database.
    """

    _clients: Dict[str, Type[BaseSourceClient]] = {}

    @classmethod
    def register(cls, slug: str, client_class: Type[BaseSourceClient]) -> None:
        """Register a source client class."""
        cls._clients[slug] = client_class
        logger.debug(f"Registered source client: {slug}")

    @classmethod
    def get_client_class(cls, slug: str) -> Optional[Type[BaseSourceClient]]:
        """Get the client class for a source slug."""
        return cls._clients.get(slug)

    @classmethod
    def get_client(cls, slug: str) -> Optional[BaseSourceClient]:
        """Get an instantiated client for a source slug."""
        client_class = cls.get_client_class(slug)
        if client_class:
            return client_class()
        return None

    @classmethod
    def get_registered_slugs(cls) -> List[str]:
        """Get list of all registered source slugs."""
        return list(cls._clients.keys())

    @classmethod
    def is_registered(cls, slug: str) -> bool:
        """Check if a source slug is registered."""
        return slug in cls._clients


def register_all_sources() -> None:
    """Register all available source clients."""
    from sync_service.app.sources.hackernews_client import HackerNewsClient
    from sync_service.app.sources.devto_client import DevToClient
    from sync_service.app.sources.reddit_client import RedditClient
    from sync_service.app.sources.lobsters_client import LobstersClient

    SourceRegistry.register("hackernews", HackerNewsClient)
    SourceRegistry.register("devto", DevToClient)
    SourceRegistry.register("reddit", RedditClient)
    SourceRegistry.register("lobsters", LobstersClient)

    logger.info(f"Registered {len(SourceRegistry.get_registered_slugs())} source clients")


# Auto-register sources on module import
register_all_sources()
