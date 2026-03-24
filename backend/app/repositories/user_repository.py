from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user database operations."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email address."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, email: str, hashed_password: str) -> User:
        """Create a new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def email_exists(self, db: AsyncSession, email: str) -> bool:
        """Check if email is already registered."""
        user = await self.get_by_email(db, email)
        return user is not None


def get_user_repository() -> UserRepository:
    """Dependency injection for UserRepository."""
    return UserRepository()
