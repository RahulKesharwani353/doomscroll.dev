from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.article import ArticleCreate
from shared.models.source import Source
from sync_service.app.sources.registry import SourceRegistry
from sync_service.app.sources.base_client import BaseSourceClient
from sync_service.app.repositories.article_repository import ArticleRepository
from sync_service.app.repositories.source_repository import SourceRepository
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SyncResult:
    """Result of a sync operation."""
    stats: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class SourceAggregator:
    """Aggregates articles from content sources.

    Can work with:
    1. All registered sources (legacy mode, for backwards compatibility)
    2. Only enabled sources from the database
    3. A specific source by slug
    """

    def __init__(self):
        self.clients: List[BaseSourceClient] = []
        self._initialized = False

    async def init_from_db(self, db: AsyncSession, source_slug: Optional[str] = None) -> None:
        """Initialize clients from database sources.

        Args:
            db: Database session
            source_slug: If provided, only initialize this specific source
        """
        source_repo = SourceRepository()

        if source_slug:
            # Single source
            source = await source_repo.get_by_slug(db, source_slug)
            if source and source.is_enabled:
                client = SourceRegistry.get_client(source.slug)
                if client:
                    self.clients.append(client)
        else:
            # All enabled sources
            sources = await source_repo.get_enabled_sources(db)
            for source in sources:
                client = SourceRegistry.get_client(source.slug)
                if client:
                    self.clients.append(client)

        self._initialized = True
        logger.info(f"Initialized aggregator with {len(self.clients)} source(s)")

    def init_all_registered(self) -> None:
        """Initialize all registered source clients (legacy mode)."""
        for slug in SourceRegistry.get_registered_slugs():
            client = SourceRegistry.get_client(slug)
            if client:
                self.clients.append(client)
        self._initialized = True
        logger.info(f"Initialized aggregator with all {len(self.clients)} registered sources")

    async def fetch_all(self, limit_per_source: int = 30) -> Tuple[Dict[str, List[ArticleCreate]], List[str]]:
        """Fetch articles from all initialized sources concurrently.

        Returns:
            Tuple of (results dict, errors list)
        """
        if not self._initialized:
            self.init_all_registered()

        results = {}
        errors = []

        tasks = [client.fetch_articles(limit_per_source) for client in self.clients]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for client, response in zip(self.clients, responses):
            if isinstance(response, Exception):
                error_msg = f"{client.source_name}: {str(response)}"
                logger.error(f"Error fetching from {client.source_name}: {response}")
                errors.append(error_msg)
                results[client.source_name] = []
            else:
                results[client.source_name] = response
                # Track sources that returned 0 articles as potential issues
                if len(response) == 0:
                    errors.append(f"{client.source_name}: returned 0 articles")

        return results, errors

    async def fetch_and_save(
        self,
        db: AsyncSession,
        limit_per_source: int = 30
    ) -> SyncResult:
        """Fetch articles from all sources and save to database.

        Returns:
            SyncResult with stats and errors
        """
        results, errors = await self.fetch_all(limit_per_source)

        article_repo = ArticleRepository()
        stats = {}

        for source_name, articles in results.items():
            if articles:
                # Convert ArticleCreate to dict for upsert
                article_dicts = [article.model_dump() for article in articles]
                count = await article_repo.upsert_many(db, article_dicts)
                stats[source_name] = count
            else:
                stats[source_name] = 0

        total = sum(stats.values())
        logger.info(f"Total articles saved: {total}")

        return SyncResult(stats=stats, errors=errors)

    async def close(self):
        """Close all HTTP clients."""
        for client in self.clients:
            await client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
