from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class SyncJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncJobCreate(BaseModel):
    """Schema for creating a sync job."""

    source_id: Optional[int] = None
    source_slug: Optional[str] = None


class SyncJobUpdate(BaseModel):
    """Schema for updating a sync job."""

    status: Optional[SyncJobStatus] = None
    articles_fetched: Optional[int] = None
    articles_created: Optional[int] = None
    articles_updated: Optional[int] = None
    articles_failed: Optional[int] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SyncJobResponse(BaseModel):
    """Schema for sync job API responses."""

    id: int
    source_id: Optional[int] = None
    source_slug: Optional[str] = None
    status: str
    articles_fetched: int
    articles_created: int
    articles_updated: int
    articles_failed: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SyncStatusResponse(BaseModel):
    """Schema for overall sync status."""

    is_running: bool
    last_sync: Optional[SyncJobResponse] = None
    enabled_sources: int
    total_sources: int


class SyncTriggerRequest(BaseModel):
    """Schema for manually triggering a sync."""

    source_slug: Optional[str] = None  # None = sync all enabled sources


class SyncTriggerResponse(BaseModel):
    """Schema for sync trigger response."""

    job_id: int
    message: str
