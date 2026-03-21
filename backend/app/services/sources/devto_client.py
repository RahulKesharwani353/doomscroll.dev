from typing import List
from datetime import datetime, timezone

from app.schemas.article import ArticleCreate
from app.services.sources.base_client import BaseSourceClient, logger


class DevToClient(BaseSourceClient):
    """Client for Dev.to API."""

    BASE_URL = "https://dev.to/api"

    @property
    def source_name(self) -> str:
        return "devto"

    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch latest articles from Dev.to."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/articles",
                params={"per_page": limit, "top": 1}
            )
            response.raise_for_status()
            data = response.json()

            articles = []
            for item in data:
                try:
                    published_at = None
                    if item.get("published_at"):
                        published_at = datetime.fromisoformat(
                            item["published_at"].replace("Z", "+00:00")
                        )

                    article = ArticleCreate(
                        id=self.generate_id(str(item["id"])),
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        author=item.get("user", {}).get("username"),
                        source=self.source_name,
                        published_at=published_at,
                        fetched_at=datetime.now(timezone.utc),
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing Dev.to article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from Dev.to")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from Dev.to: {e}")
            return []
