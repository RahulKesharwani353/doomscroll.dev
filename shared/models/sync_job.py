from sqlalchemy import Column, String, Integer, DateTime, Index, Text, ForeignKey
from sqlalchemy.sql import func
from enum import Enum

from shared.core.database import Base


class SyncJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncJob(Base):
    """SyncJob model representing a sync job execution history."""

    __tablename__ = "sync_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    source_slug = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default=SyncJobStatus.PENDING.value)
    articles_fetched = Column(Integer, default=0)
    articles_created = Column(Integer, default=0)
    articles_updated = Column(Integer, default=0)
    articles_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_sync_jobs_status", "status"),
        Index("idx_sync_jobs_source_id", "source_id"),
        Index("idx_sync_jobs_created_at", created_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<SyncJob(id={self.id}, source_slug={self.source_slug}, status={self.status})>"

    @property
    def duration_seconds(self) -> float | None:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
