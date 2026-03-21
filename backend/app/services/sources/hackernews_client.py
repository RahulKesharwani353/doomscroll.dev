from typing import List
from datetime import datetime, timezone
import asyncio

from app.schemas.article import ArticleCreate
from app.services.sources.base_client import BaseSourceClient, logger


class HackerNewsClient(BaseSourceClient):
    """Client for Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    @property
    def source_name(self) -> str:
        return "hackernews"

    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch top stories from Hacker News."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()[:limit]

            tasks = [self._fetch_story(story_id) for story_id in story_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            articles = []
            for result in results:
                if isinstance(result, ArticleCreate):
                    articles.append(result)

            logger.info(f"Fetched {len(articles)} articles from Hacker News")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from Hacker News: {e}")
            return []

    async def _fetch_story(self, story_id: int) -> ArticleCreate | None:
        """Fetch a single story by ID."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/item/{story_id}.json")
            response.raise_for_status()
            data = response.json()

            if not data or data.get("type") != "story" or not data.get("url"):
                return None

            return ArticleCreate(
                id=self.generate_id(str(story_id)),
                title=data.get("title", ""),
                url=data.get("url", ""),
                author=data.get("by"),
                source=self.source_name,
                published_at=datetime.fromtimestamp(data.get("time", 0), tz=timezone.utc),
                fetched_at=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Error fetching HN story {story_id}: {e}")
            return None
