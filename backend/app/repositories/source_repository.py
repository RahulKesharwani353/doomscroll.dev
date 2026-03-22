from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.source import Source
from app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """Repository for Source model operations."""

    def __init__(self):
        super().__init__(Source)

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Source]:
        """Get a source by its slug."""
        result = await db.execute(
            select(Source).where(Source.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_enabled_sources(self, db: AsyncSession) -> List[Source]:
        """Get all enabled sources."""
        result = await db.execute(
            select(Source).where(Source.is_enabled == True).order_by(Source.slug)
        )
        return list(result.scalars().all())

    async def get_all_ordered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Source]:
        """Get all sources ordered by slug."""
        result = await db.execute(
            select(Source).order_by(Source.slug).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def toggle_enabled(
        self,
        db: AsyncSession,
        source_id: int,
        is_enabled: bool
    ) -> Optional[Source]:
        """Toggle the enabled status of a source."""
        source = await self.get(db, source_id)
        if source:
            source.is_enabled = is_enabled
            await db.commit()
            await db.refresh(source)
        return source


def get_source_repository() -> SourceRepository:
    """Dependency injection for SourceRepository."""
    return SourceRepository()
