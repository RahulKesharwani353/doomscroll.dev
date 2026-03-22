from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from shared.schemas.article import ArticleCreate
from sync_service.app.sources.base_client import BaseSourceClient, logger


class LobstersClient(BaseSourceClient):
    """Client for Lobste.rs API."""

    BASE_URL = "https://lobste.rs"

    @property
    def source_name(self) -> str:
        return "lobsters"

    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch raw story data from Lobste.rs."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/hottest.json")
            response.raise_for_status()
            data = response.json()
            return data[:limit]

        except Exception as e:
            logger.error(f"Error fetching raw from Lobsters: {e}")
            raise

    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        """Transform a raw Lobste.rs story into an ArticleCreate."""
        if not raw_item:
            return None

        # Get URL (prefer external URL, fall back to comments URL)
        url = raw_item.get("url") or raw_item.get("comments_url")
        if not url:
            return None

        # Parse published_at
        published_at = None
        if raw_item.get("created_at"):
            try:
                published_at = datetime.fromisoformat(
                    raw_item["created_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        return ArticleCreate(
            id=self.generate_id(raw_item["short_id"]),
            title=raw_item.get("title", ""),
            url=url,
            author=raw_item.get("submitter_user"),
            source=self.source_name,
            published_at=published_at,
            fetched_at=self.get_current_time(),
        )
