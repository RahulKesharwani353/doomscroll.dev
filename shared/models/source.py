from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index, JSON
from sqlalchemy.sql import func

from shared.core.database import Base


class Source(Base):
    """Source model representing a content source configuration."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    ui_config = Column(JSON, nullable=True, default=dict)
    is_enabled = Column(Boolean, default=True, nullable=False)
    fetch_limit = Column(Integer, default=30, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_sources_slug", "slug"),
        Index("idx_sources_is_enabled", "is_enabled"),
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, slug={self.slug}, is_enabled={self.is_enabled})>"
