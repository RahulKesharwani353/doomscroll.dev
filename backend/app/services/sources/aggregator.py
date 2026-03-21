from typing import List, Dict
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.article import ArticleCreate
from app.services.sources.hackernews_client import HackerNewsClient
from app.services.sources.devto_client import DevToClient
from app.services.sources.reddit_client import RedditClient
from app.services.sources.lobsters_client import LobstersClient
from app.services.article_service import ArticleService
from app.repositories.article_repository import ArticleRepository
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SourceAggregator:
    """Aggregates articles from all content sources."""

    def __init__(self):
        self.clients = [
            HackerNewsClient(),
            DevToClient(),
            RedditClient(),
            LobstersClient(),
        ]

    async def fetch_all(self, limit_per_source: int = 30) -> Dict[str, List[ArticleCreate]]:
        """Fetch articles from all sources concurrently."""
        results = {}

        tasks = [client.fetch_articles(limit_per_source) for client in self.clients]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for client, response in zip(self.clients, responses):
            if isinstance(response, Exception):
                logger.error(f"Error fetching from {client.source_name}: {response}")
                results[client.source_name] = []
            else:
                results[client.source_name] = response

        return results

    async def fetch_and_save(self, db: AsyncSession, limit_per_source: int = 30) -> Dict[str, int]:
        """Fetch articles from all sources and save to database."""
        results = await self.fetch_all(limit_per_source)

        article_service = ArticleService(ArticleRepository())
        stats = {}

        for source_name, articles in results.items():
            if articles:
                count = await article_service.upsert_articles(db, articles)
                stats[source_name] = count
            else:
                stats[source_name] = 0

        total = sum(stats.values())
        logger.info(f"Total articles saved: {total}")

        return stats

    async def close(self):
        """Close all HTTP clients."""
        for client in self.clients:
            await client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
