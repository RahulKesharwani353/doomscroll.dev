from typing import List
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.bookmark import BookmarkWithArticle
from shared.schemas.common import PaginatedResponse
from shared.core.logging_config import get_logger
from app.repositories.bookmark_repository import BookmarkRepository, get_bookmark_repository

logger = get_logger(__name__)


class BookmarkService:
    """Service layer for bookmark business logic."""

    def __init__(self, bookmark_repository: BookmarkRepository):
        self.repository = bookmark_repository

    async def get_bookmarks(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[BookmarkWithArticle]:
        """Get paginated bookmarks with article data."""
        skip = (page - 1) * limit
        bookmarks = await self.repository.get_user_bookmarks(db, user_id, skip, limit)
        total = await self.repository.count_user_bookmarks(db, user_id)

        bookmark_dtos = [BookmarkWithArticle.model_validate(b) for b in bookmarks]

        return PaginatedResponse.create(
            data=bookmark_dtos,
            page=page,
            limit=limit,
            total=total
        )

    async def add_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> BookmarkWithArticle:
        """Add a bookmark. Idempotent - returns existing if already bookmarked."""
        existing = await self.repository.get_bookmark(db, user_id, article_id)
        if existing:
            return BookmarkWithArticle.model_validate(existing)

        bookmark = await self.repository.create_bookmark(db, user_id, article_id)
        logger.info(f"Bookmark created: user={user_id}, article={article_id}")
        return BookmarkWithArticle.model_validate(bookmark)

    async def remove_bookmark(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> bool:
        """Remove a bookmark. Returns True if removed."""
        deleted = await self.repository.delete_bookmark(db, user_id, article_id)
        if deleted:
            logger.info(f"Bookmark removed: user={user_id}, article={article_id}")
        return deleted

    async def is_bookmarked(
        self,
        db: AsyncSession,
        user_id: UUID,
        article_id: str
    ) -> bool:
        """Check if an article is bookmarked."""
        return await self.repository.is_bookmarked(db, user_id, article_id)


async def get_bookmark_service(
    bookmark_repository: BookmarkRepository = Depends(get_bookmark_repository)
) -> BookmarkService:
    """Dependency injection for BookmarkService."""
    return BookmarkService(bookmark_repository=bookmark_repository)
