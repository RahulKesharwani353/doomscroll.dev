from typing import Optional, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.source import Source
from shared.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from shared.schemas.common import ListResponse
from app.repositories.source_repository import SourceRepository, get_source_repository
from app.cache.cache_service import CacheService, get_cache_service
from app.config import settings
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class SourceService:
    """Service layer for source business logic."""

    def __init__(
        self,
        source_repository: SourceRepository,
        cache_service: Optional[CacheService] = None
    ):
        self.repository = source_repository
        self._cache = cache_service

    async def get_sources(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> ListResponse[SourceResponse]:
        """Get all sources."""
        # Check cache first
        if self._cache:
            cache_key = self._cache.sources_key()
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for sources")
                return ListResponse[SourceResponse](**cached)

        # Fetch from database
        sources = await self.repository.get_all_ordered(db, skip=skip, limit=limit)
        source_dtos = [SourceResponse.model_validate(source) for source in sources]
        logger.info(f"Fetched {len(source_dtos)} sources")

        response = ListResponse(data=source_dtos)

        # Store in cache
        if self._cache:
            await self._cache.set(
                cache_key,
                response.model_dump(),
                ttl=settings.CACHE_TTL_LONG
            )

        return response

    async def get_enabled_sources(
        self,
        db: AsyncSession
    ) -> List[SourceResponse]:
        """Get all enabled sources."""
        sources = await self.repository.get_enabled_sources(db)
        return [SourceResponse.model_validate(source) for source in sources]

    async def get_source_by_id(
        self,
        db: AsyncSession,
        source_id: int
    ) -> Optional[SourceResponse]:
        """Get a source by ID."""
        source = await self.repository.get(db, source_id)
        if source:
            logger.info(f"Source with ID {source_id} retrieved successfully")
            return SourceResponse.model_validate(source)
        logger.warning(f"Source with ID {source_id} not found")
        return None

    async def get_source_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> Optional[SourceResponse]:
        """Get a source by slug."""
        source = await self.repository.get_by_slug(db, slug)
        if source:
            return SourceResponse.model_validate(source)
        return None

    async def create_source(
        self,
        db: AsyncSession,
        source_data: SourceCreate
    ) -> SourceResponse:
        """Create a new source."""
        # Check if slug already exists
        existing = await self.repository.get_by_slug(db, source_data.slug)
        if existing:
            logger.error(f"Source creation failed: slug '{source_data.slug}' already exists")
            raise ValueError(f"Source with slug '{source_data.slug}' already exists")

        source = Source(**source_data.model_dump())
        created = await self.repository.create(db, source)
        logger.info(f"Source '{source_data.slug}' created successfully")
        return SourceResponse.model_validate(created)

    async def update_source(
        self,
        db: AsyncSession,
        source_id: int,
        source_data: SourceUpdate
    ) -> Optional[SourceResponse]:
        """Update an existing source."""
        source = await self.repository.get(db, source_id)
        if not source:
            logger.warning(f"Source with ID {source_id} not found for update")
            return None

        # Update only provided fields
        update_data = source_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(source, field, value)

        updated = await self.repository.update(db, source)
        logger.info(f"Source with ID {source_id} updated successfully")
        return SourceResponse.model_validate(updated)

    async def delete_source(
        self,
        db: AsyncSession,
        source_id: int
    ) -> bool:
        """Delete a source."""
        source = await self.repository.get(db, source_id)
        if not source:
            logger.warning(f"Source with ID {source_id} not found for deletion")
            return False

        slug = source.slug
        success = await self.repository.delete(db, source_id)
        if success:
            logger.info(f"Source '{slug}' deleted successfully")
        return success

    async def toggle_source(
        self,
        db: AsyncSession,
        source_id: int,
        is_enabled: bool
    ) -> Optional[SourceResponse]:
        """Enable or disable a source."""
        source = await self.repository.toggle_enabled(db, source_id, is_enabled)
        if source:
            action = "enabled" if is_enabled else "disabled"
            logger.info(f"Source '{source.slug}' {action}")
            return SourceResponse.model_validate(source)
        return None

    async def get_source_count(
        self,
        db: AsyncSession,
        enabled_only: bool = False
    ) -> int:
        """Get count of sources."""
        if enabled_only:
            sources = await self.repository.get_enabled_sources(db)
            return len(sources)
        return await self.repository.count(db)


async def get_source_service(
    source_repository: SourceRepository = Depends(get_source_repository)
) -> SourceService:
    """Dependency injection for SourceService."""
    cache_service = await get_cache_service()
    return SourceService(source_repository=source_repository, cache_service=cache_service)
