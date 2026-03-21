from typing import List
from datetime import datetime, timezone

from app.schemas.article import ArticleCreate
from app.services.sources.base_client import BaseSourceClient, logger


class LobstersClient(BaseSourceClient):
    """Client for Lobste.rs API."""

    BASE_URL = "https://lobste.rs"

    @property
    def source_name(self) -> str:
        return "lobsters"

    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch hottest stories from Lobste.rs."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/hottest.json")
            response.raise_for_status()
            data = response.json()[:limit]

            articles = []
            for item in data:
                try:
                    # Skip stories without external URLs
                    url = item.get("url") or item.get("comments_url")
                    if not url:
                        continue

                    published_at = None
                    if item.get("created_at"):
                        published_at = datetime.fromisoformat(
                            item["created_at"].replace("Z", "+00:00")
                        )

                    article = ArticleCreate(
                        id=self.generate_id(item["short_id"]),
                        title=item.get("title", ""),
                        url=url,
                        author=item.get("submitter_user", {}).get("username"),
                        source=self.source_name,
                        published_at=published_at,
                        fetched_at=datetime.now(timezone.utc),
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing Lobsters article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from Lobsters")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from Lobsters: {e}")
            return []
