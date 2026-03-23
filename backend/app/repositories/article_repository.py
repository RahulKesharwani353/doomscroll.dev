from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.article import Article
from app.repositories.base_repository import BaseRepository
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class ArticleRepository(BaseRepository[Article]):
    """Repository for Article database operations."""

    def __init__(self):
        super().__init__(Article)

    async def get_articles(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        source: Optional[str] = None
    ) -> Tuple[List[Article], int]:
        """Get articles with pagination and optional source filter."""
        query = select(self.model).order_by(desc(self.model.published_at))

        if source:
            query = query.where(self.model.source == source)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        articles = list(result.scalars().all())

        return articles, len(articles)

    async def count_articles(
        self,
        db: AsyncSession,
        source: Optional[str] = None
    ) -> int:
        """Count articles with optional source filter."""
        query = select(func.count()).select_from(self.model)

        if source:
            query = query.where(self.model.source == source)

        result = await db.execute(query)
        return result.scalar() or 0

    async def get_by_source(
        self,
        db: AsyncSession,
        source: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Article]:
        """Get articles filtered by source."""
        result = await db.execute(
            select(self.model)
            .where(self.model.source == source)
            .order_by(desc(self.model.published_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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

    async def get_latest_by_source(
        self,
        db: AsyncSession,
        source: str,
        limit: int = 10
    ) -> List[Article]:
        """Get latest articles from a specific source."""
        result = await db.execute(
            select(self.model)
            .where(self.model.source == source)
            .order_by(desc(self.model.published_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_title(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 20,
        source: Optional[str] = None
    ) -> List[Article]:
        """Search articles by title (case-insensitive), optionally filtered by source."""
        query = select(self.model).where(self.model.title.ilike(f"%{search_term}%"))
        if source:
            query = query.where(self.model.source == source)
        query = query.order_by(desc(self.model.published_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_search_results(
        self,
        db: AsyncSession,
        search_term: str,
        source: Optional[str] = None
    ) -> int:
        """Count total search results for pagination."""
        query = select(func.count()).select_from(self.model).where(self.model.title.ilike(f"%{search_term}%"))
        if source:
            query = query.where(self.model.source == source)
        result = await db.execute(query)
        return result.scalar() or 0

    async def delete_old_articles(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> int:
        """Delete articles older than specified days."""
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.published_at < cutoff_date)
        )
        count = result.scalar() or 0

        if count > 0:
            await db.execute(
                self.model.__table__.delete()
                .where(self.model.published_at < cutoff_date)
            )
            await db.commit()

        return count


def get_article_repository() -> ArticleRepository:
    """Dependency injection for ArticleRepository."""
    return ArticleRepository()
