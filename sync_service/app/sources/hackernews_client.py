from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import asyncio

from shared.schemas.article import ArticleCreate
from sync_service.app.sources.base_client import BaseSourceClient, logger


class HackerNewsClient(BaseSourceClient):
    """Client for Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    @property
    def source_name(self) -> str:
        return "hackernews"

    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch raw story data from Hacker News."""
        try:
            # First get top story IDs
            response = await self.client.get(f"{self.BASE_URL}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()[:limit]

            # Fetch each story's details concurrently
            tasks = [self._fetch_story_raw(story_id) for story_id in story_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            raw_items = []
            for result in results:
                if isinstance(result, dict) and result:
                    raw_items.append(result)

            return raw_items

        except Exception as e:
            logger.error(f"Error fetching raw from Hacker News: {e}")
            raise

    async def _fetch_story_raw(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single story's raw data by ID."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/item/{story_id}.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching HN story {story_id}: {e}")
            return None

    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        """Transform a raw HN story into an ArticleCreate."""
        # Skip non-stories and stories without URLs
        if not raw_item:
            return None
        if raw_item.get("type") != "story":
            return None
        if not raw_item.get("url"):
            return None

        return ArticleCreate(
            id=self.generate_id(str(raw_item["id"])),
            title=raw_item.get("title", ""),
            url=raw_item.get("url", ""),
            author=raw_item.get("by"),
            source=self.source_name,
            published_at=datetime.fromtimestamp(raw_item.get("time", 0), tz=timezone.utc),
            fetched_at=self.get_current_time(),
        )
