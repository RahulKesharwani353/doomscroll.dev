from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.sync_job import (
    SyncJobResponse,
    SyncStatusResponse,
    SyncTriggerRequest,
    SyncTriggerResponse,
)
from shared.schemas.common import DataResponse, PaginatedResponse
from app.repositories.sync_job_repository import SyncJobRepository, get_sync_job_repository
from app.repositories.source_repository import SourceRepository, get_source_repository
from app.services.source_service import SourceService, get_source_service
from shared.core.database import get_db
from shared.core.logging_config import get_logger

router = APIRouter(prefix="/sync", tags=["Sync"])
logger = get_logger(__name__)


@router.get("/status", response_model=DataResponse[SyncStatusResponse])
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
    sync_job_repo: SyncJobRepository = Depends(get_sync_job_repository),
    source_service: SourceService = Depends(get_source_service)
) -> DataResponse[SyncStatusResponse]:
    """Get current sync status."""
    try:
        running_jobs = await sync_job_repo.get_running_jobs(db)
        is_running = len(running_jobs) > 0

        last_job = await sync_job_repo.get_latest(db)
        last_sync = SyncJobResponse.model_validate(last_job) if last_job else None

        enabled_count = await source_service.get_source_count(db, enabled_only=True)
        total_count = await source_service.get_source_count(db, enabled_only=False)

        status_data = SyncStatusResponse(
            is_running=is_running,
            last_sync=last_sync,
            enabled_sources=enabled_count,
            total_sources=total_count
        )

        return DataResponse(data=status_data)
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/jobs", response_model=PaginatedResponse[SyncJobResponse])
async def get_sync_jobs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    source_slug: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    sync_job_repo: SyncJobRepository = Depends(get_sync_job_repository)
) -> PaginatedResponse[SyncJobResponse]:
    """Get paginated sync jobs."""
    try:
        skip = (page - 1) * limit
        jobs = await sync_job_repo.get_jobs_paginated(db, skip=skip, limit=limit, source_slug=source_slug)
        total = await sync_job_repo.count_jobs(db, source_slug=source_slug)
        job_dtos = [SyncJobResponse.model_validate(job) for job in jobs]
        return PaginatedResponse.create(
            data=job_dtos,
            page=page,
            limit=limit,
            total=total
        )
    except Exception as e:
        logger.error(f"Error retrieving sync jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/jobs/{job_id}", response_model=DataResponse[SyncJobResponse])
async def get_sync_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    sync_job_repo: SyncJobRepository = Depends(get_sync_job_repository)
) -> DataResponse[SyncJobResponse]:
    """Get a specific sync job by ID."""
    try:
        job = await sync_job_repo.get(db, job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sync job with ID {job_id} not found"
            )
        return DataResponse(data=SyncJobResponse.model_validate(job))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sync job with ID {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/trigger", response_model=DataResponse[SyncTriggerResponse], status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync(
    trigger_data: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    sync_job_repo: SyncJobRepository = Depends(get_sync_job_repository),
    source_repo: SourceRepository = Depends(get_source_repository)
) -> DataResponse[SyncTriggerResponse]:
    """Manually trigger a sync for one or all sources."""
    try:
        running_jobs = await sync_job_repo.get_running_jobs(db)
        if running_jobs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A sync is already in progress"
            )

        source_id = None
        if trigger_data.source_slug:
            source = await source_repo.get_by_slug(db, trigger_data.source_slug)
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Source '{trigger_data.source_slug}' not found"
                )
            if not source.is_enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Source '{trigger_data.source_slug}' is disabled"
                )
            source_id = source.id

        job = await sync_job_repo.create_job(
            db,
            source_id=source_id,
            source_slug=trigger_data.source_slug
        )

        message = f"Sync triggered for {'source: ' + trigger_data.source_slug if trigger_data.source_slug else 'all enabled sources'}"

        response_data = SyncTriggerResponse(
            job_id=job.id,
            message=message
        )

        logger.info(message)
        return DataResponse(data=response_data, message=message)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
