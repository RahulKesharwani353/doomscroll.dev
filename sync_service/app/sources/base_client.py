from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

import httpx
from pydantic import ValidationError

from shared.schemas.article import ArticleCreate
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class BaseSourceClient(ABC):
    """Abstract base class for content source clients.

    Implements the fetch_raw/transform pattern for better separation of concerns:
    - fetch_raw(): Fetches raw data from the external API
    - transform(): Transforms raw data into normalized ArticleCreate objects
    - fetch_articles(): Combines fetch_raw and transform with error handling
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source identifier (e.g., 'hackernews', 'devto')."""
        pass

    @abstractmethod
    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch raw data from the external API.

        Returns:
            List of raw dictionaries from the API response.
            Each dict represents one article/story in the source's native format.
        """
        pass

    @abstractmethod
    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        """
        Transform a single raw item into a normalized ArticleCreate.

        Args:
            raw_item: A single item from the raw API response

        Returns:
            ArticleCreate if transformation succeeds, None if item should be skipped
        """
        pass

    def transform(self, raw_items: List[Dict[str, Any]]) -> List[ArticleCreate]:
        """
        Transform raw items into normalized ArticleCreate objects.

        Args:
            raw_items: List of raw dictionaries from fetch_raw()

        Returns:
            List of validated ArticleCreate objects
        """
        articles = []
        for item in raw_items:
            try:
                article = self.transform_item(item)
                if article is not None:
                    articles.append(article)
            except ValidationError as e:
                logger.warning(f"Validation error transforming {self.source_name} item: {e}")
            except Exception as e:
                logger.error(f"Error transforming {self.source_name} item: {e}")
        return articles

    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """
        Fetch and transform articles from the source.

        This is the main entry point that combines fetch_raw and transform.
        """
        try:
            raw_items = await self.fetch_raw(limit)
            articles = self.transform(raw_items)
            logger.info(f"Fetched {len(articles)} articles from {self.source_name}")
            return articles
        except Exception as e:
            logger.error(f"Error fetching from {self.source_name}: {e}")
            return []

    def generate_id(self, external_id: str) -> str:
        """Generate a unique article ID with source prefix."""
        return f"{self.source_name}-{external_id}"

    def get_current_time(self) -> datetime:
        """Get current UTC time."""
        return datetime.now(timezone.utc)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
