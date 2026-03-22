from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from shared.schemas.article import ArticleCreate
from sync_service.app.sources.base_client import BaseSourceClient, logger


class DevToClient(BaseSourceClient):
    """Client for Dev.to API."""

    BASE_URL = "https://dev.to/api"

    @property
    def source_name(self) -> str:
        return "devto"

    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch raw article data from Dev.to."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/articles",
                params={"per_page": limit, "top": 1}
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching raw from Dev.to: {e}")
            raise

    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        """Transform a raw Dev.to article into an ArticleCreate."""
        if not raw_item:
            return None

        # Parse published_at
        published_at = None
        if raw_item.get("published_at"):
            try:
                published_at = datetime.fromisoformat(
                    raw_item["published_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        return ArticleCreate(
            id=self.generate_id(str(raw_item["id"])),
            title=raw_item.get("title", ""),
            url=raw_item.get("url", ""),
            author=raw_item.get("user", {}).get("username"),
            source=self.source_name,
            published_at=published_at,
            fetched_at=self.get_current_time(),
        )
