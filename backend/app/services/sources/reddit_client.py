from typing import List
from datetime import datetime, timezone

from app.schemas.article import ArticleCreate
from app.services.sources.base_client import BaseSourceClient, logger
from app.config import settings


class RedditClient(BaseSourceClient):
    """Client for Reddit API (r/programming and r/webdev)."""

    BASE_URL = "https://www.reddit.com"
    SUBREDDITS = ["programming", "webdev"]

    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.client.headers.update({
            "User-Agent": settings.REDDIT_USER_AGENT
        })

    @property
    def source_name(self) -> str:
        return "reddit"

    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch hot posts from programming subreddits."""
        articles = []
        per_subreddit = limit // len(self.SUBREDDITS)

        for subreddit in self.SUBREDDITS:
            try:
                subreddit_articles = await self._fetch_subreddit(subreddit, per_subreddit)
                articles.extend(subreddit_articles)
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit}: {e}")
                continue

        logger.info(f"Fetched {len(articles)} articles from Reddit")
        return articles

    async def _fetch_subreddit(self, subreddit: str, limit: int) -> List[ArticleCreate]:
        """Fetch posts from a single subreddit."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/r/{subreddit}/hot.json",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()

            articles = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})

                # Skip stickied posts and self posts without external links
                if post_data.get("stickied") or post_data.get("is_self"):
                    continue

                try:
                    article = ArticleCreate(
                        id=self.generate_id(post_data["id"]),
                        title=post_data.get("title", ""),
                        url=post_data.get("url", ""),
                        author=post_data.get("author"),
                        source=self.source_name,
                        published_at=datetime.fromtimestamp(
                            post_data.get("created_utc", 0), tz=timezone.utc
                        ),
                        fetched_at=datetime.now(timezone.utc),
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing Reddit post: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Error fetching subreddit {subreddit}: {e}")
            return []
