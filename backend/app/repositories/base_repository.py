from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single entity by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get all entities with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        obj: ModelType,
        auto_commit: bool = True
    ) -> ModelType:
        """Create a new entity."""
        db.add(obj)
        if auto_commit:
            await db.commit()
            await db.refresh(obj)
        else:
            await db.flush()
        return obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        auto_commit: bool = True
    ) -> ModelType:
        """Update an existing entity."""
        if auto_commit:
            await db.commit()
            await db.refresh(db_obj)
        else:
            await db.flush()
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: Any,
        auto_commit: bool = True
    ) -> bool:
        """Delete an entity by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            if auto_commit:
                await db.commit()
            return True
        return False

    async def count(self, db: AsyncSession) -> int:
        """Count all entities."""
        result = await db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
