from typing import List
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.article import Article
from sync_service.app.repositories.base_repository import BaseRepository
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class ArticleRepository(BaseRepository[Article]):
    """Repository for Article database operations in sync service."""

    def __init__(self):
        super().__init__(Article)

    async def upsert_many(
        self,
        db: AsyncSession,
        articles: List[dict]
    ) -> int:
        """Bulk upsert articles (insert or update on conflict)."""
        if not articles:
            return 0

        try:
            stmt = insert(self.model).values(articles)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": stmt.excluded.title,
                    "url": stmt.excluded.url,
                    "author": stmt.excluded.author,
                    "published_at": stmt.excluded.published_at,
                    "fetched_at": stmt.excluded.fetched_at,
                    "updated_at": func.now()
                }
            )
            await db.execute(stmt)
            await db.commit()
            return len(articles)
        except Exception as e:
            logger.error(f"Error upserting articles: {e}")
            await db.rollback()
            raise
