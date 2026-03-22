from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.source import Source
from sync_service.app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """Repository for Source model operations in sync service."""

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
