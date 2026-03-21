from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

import httpx

from app.schemas.article import ArticleCreate
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BaseSourceClient(ABC):
    """Abstract base class for content source clients."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source identifier (e.g., 'hackernews', 'devto')."""
        pass

    @abstractmethod
    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch articles from the source."""
        pass

    def generate_id(self, external_id: str) -> str:
        """Generate a unique article ID with source prefix."""
        return f"{self.source_name}-{external_id}"

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
