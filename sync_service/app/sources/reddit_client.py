from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from shared.schemas.article import ArticleCreate
from shared.core.config import settings
from sync_service.app.sources.base_client import BaseSourceClient, logger


class RedditClient(BaseSourceClient):
    """Client for Reddit API (r/programming and r/webdev)."""

    BASE_URL = "https://www.reddit.com"
    SUBREDDITS = ["programming", "webdev"]

    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        # Reddit requires specific User-Agent format: platform:app_id:version (by /u/username)
        user_agent = getattr(settings, "REDDIT_USER_AGENT", "windows:doomscroll:1.0 (by /u/doomscroll_bot)")
        self.client.headers.update({
            "User-Agent": user_agent
        })

    @property
    def source_name(self) -> str:
        return "reddit"

    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch raw posts from programming subreddits."""
        raw_items = []
        per_subreddit = limit // len(self.SUBREDDITS)

        for subreddit in self.SUBREDDITS:
            try:
                subreddit_items = await self._fetch_subreddit_raw(subreddit, per_subreddit)
                raw_items.extend(subreddit_items)
            except Exception as e:
                logger.error(f"Error fetching raw from r/{subreddit}: {e}")
                continue

        return raw_items

    async def _fetch_subreddit_raw(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch raw posts from a single subreddit."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/r/{subreddit}/hot.json",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()

            # Extract post data from Reddit's response structure
            posts = data.get("data", {}).get("children", [])
            return [post.get("data", {}) for post in posts]

        except Exception as e:
            logger.error(f"Error fetching raw from subreddit {subreddit}: {e}")
            return []

    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        """Transform a raw Reddit post into an ArticleCreate."""
        if not raw_item:
            return None

        # Skip stickied posts and self posts without external links
        if raw_item.get("stickied"):
            return None
        if raw_item.get("is_self"):
            return None

        # Skip if no URL
        url = raw_item.get("url", "")
        if not url:
            return None

        return ArticleCreate(
            id=self.generate_id(raw_item["id"]),
            title=raw_item.get("title", ""),
            url=url,
            author=raw_item.get("author"),
            source=self.source_name,
            published_at=datetime.fromtimestamp(
                raw_item.get("created_utc", 0), tz=timezone.utc
            ),
            fetched_at=self.get_current_time(),
        )
