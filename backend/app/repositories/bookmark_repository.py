from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from shared.models.bookmark import Bookmark


class BookmarkRepository:
    """Repository for bookmark database operations."""

    async def get_user_bookmarks(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Bookmark]:
        """Get paginated bookmarks for a user with article data."""
        result = await db.execute(
            select(Bookmark)
            .options(joinedload(Bookmark.article))
            .where(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def count_user_bookmarks(self, db: AsyncSession, user_id: UUID) -> int:
        """Count total bookmarks for a user."""
        result = await db.execute(
            select(func.count()).select_from(Bookmark).where(Bookmark.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> Optional[Bookmark]:
        """Get a specific bookmark."""
        result = await db.execute(
            select(Bookmark)
            .options(joinedload(Bookmark.article))
            .where(Bookmark.user_id == user_id, Bookmark.article_id == article_id)
        )
        return result.scalar_one_or_none()

    async def create_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> Bookmark:
        """Create a new bookmark."""
        bookmark = Bookmark(user_id=user_id, article_id=article_id)
        db.add(bookmark)
        await db.commit()
        await db.refresh(bookmark, ["article"])
        return bookmark

    async def delete_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> bool:
        """Delete a bookmark. Returns True if deleted."""
        result = await db.execute(
            delete(Bookmark).where(
                Bookmark.user_id == user_id,
                Bookmark.article_id == article_id
            )
        )
        await db.commit()
        return result.rowcount > 0

    async def is_bookmarked(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> bool:
        """Check if an article is bookmarked by a user."""
        result = await db.execute(
            select(func.count()).select_from(Bookmark).where(
                Bookmark.user_id == user_id,
                Bookmark.article_id == article_id
            )
        )
        return (result.scalar() or 0) > 0


def get_bookmark_repository() -> BookmarkRepository:
    """Dependency injection for BookmarkRepository."""
    return BookmarkRepository()
