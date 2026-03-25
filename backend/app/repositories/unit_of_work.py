"""Unit of Work pattern for database transaction management."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import AsyncSessionLocal
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class UnitOfWork:
    """Context manager for database transactions with automatic rollback on failure."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._owns_session = session is None

    @property
    def session(self) -> AsyncSession:
        """Get the database session."""
        if self._session is None:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        return self._session

    async def __aenter__(self) -> "UnitOfWork":
        """Enter the context manager."""
        if self._owns_session:
            self._session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        try:
            if exc_type is not None:
                await self.rollback()
                logger.debug("Transaction rolled back due to exception")
        finally:
            if self._owns_session and self._session:
                await self._session.close()
                self._session = None

    async def commit(self):
        """Commit the current transaction."""
        if self._session:
            await self._session.commit()
            logger.debug("Transaction committed")

    async def rollback(self):
        """Rollback the current transaction."""
        if self._session:
            await self._session.rollback()
            logger.debug("Transaction rolled back")

    async def refresh(self, obj):
        """Refresh an object from the database."""
        if self._session:
            await self._session.refresh(obj)


async def get_unit_of_work() -> UnitOfWork:
    """FastAPI dependency that provides a Unit of Work with automatic rollback."""
    async with UnitOfWork() as uow:
        yield uow
