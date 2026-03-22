from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.sync_job import SyncJob, SyncJobStatus
from sync_service.app.repositories.base_repository import BaseRepository


class SyncJobRepository(BaseRepository[SyncJob]):
    """Repository for SyncJob model operations."""

    def __init__(self):
        super().__init__(SyncJob)

    async def get_latest(
        self,
        db: AsyncSession,
        source_slug: Optional[str] = None
    ) -> Optional[SyncJob]:
        """Get the most recent sync job."""
        query = select(SyncJob).order_by(desc(SyncJob.created_at)).limit(1)
        if source_slug:
            query = query.where(SyncJob.source_slug == source_slug)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_running_jobs(self, db: AsyncSession) -> List[SyncJob]:
        """Get all currently running sync jobs."""
        result = await db.execute(
            select(SyncJob)
            .where(SyncJob.status == SyncJobStatus.RUNNING.value)
            .order_by(desc(SyncJob.created_at))
        )
        return list(result.scalars().all())

    async def create_job(
        self,
        db: AsyncSession,
        source_id: Optional[int] = None,
        source_slug: Optional[str] = None
    ) -> SyncJob:
        """Create a new sync job."""
        job = SyncJob(
            source_id=source_id,
            source_slug=source_slug or "all",  # "all" when syncing all sources
            status=SyncJobStatus.PENDING.value,
            articles_fetched=0,
            articles_created=0,
            articles_updated=0,
            articles_failed=0,
        )
        return await self.create(db, job)

    async def start_job(self, db: AsyncSession, job_id: int) -> Optional[SyncJob]:
        """Mark a job as running."""
        job = await self.get(db, job_id)
        if job:
            job.status = SyncJobStatus.RUNNING.value
            job.started_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(job)
        return job

    async def complete_job(
        self,
        db: AsyncSession,
        job_id: int,
        articles_fetched: int = 0,
        articles_created: int = 0,
        articles_updated: int = 0,
        articles_failed: int = 0,
        error_message: Optional[str] = None,
    ) -> Optional[SyncJob]:
        """Mark a job as completed with metrics."""
        job = await self.get(db, job_id)
        if job:
            job.status = SyncJobStatus.COMPLETED.value
            job.completed_at = datetime.now(timezone.utc)
            job.articles_fetched = articles_fetched
            job.articles_created = articles_created
            job.articles_updated = articles_updated
            job.articles_failed = articles_failed
            job.error_message = error_message  # Store partial errors
            await db.commit()
            await db.refresh(job)
        return job

    async def fail_job(
        self,
        db: AsyncSession,
        job_id: int,
        error_message: str,
        articles_fetched: int = 0,
        articles_failed: int = 0,
    ) -> Optional[SyncJob]:
        """Mark a job as failed."""
        job = await self.get(db, job_id)
        if job:
            job.status = SyncJobStatus.FAILED.value
            job.completed_at = datetime.now(timezone.utc)
            job.error_message = error_message
            job.articles_fetched = articles_fetched
            job.articles_failed = articles_failed
            await db.commit()
            await db.refresh(job)
        return job
