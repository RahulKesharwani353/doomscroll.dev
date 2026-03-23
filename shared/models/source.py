from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index, JSON
from sqlalchemy.sql import func

from shared.core.database import Base


class Source(Base):
    """Source model representing a content source configuration."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Source identification
    slug = Column(String(50), unique=True, nullable=False)  # e.g., "hackernews"
    name = Column(String(100), nullable=False)  # e.g., "Hacker News"
    url = Column(String(500), nullable=False)  # e.g., "https://news.ycombinator.com"
    description = Column(String(500), nullable=True)

    # UI configuration for frontend styling
    # Structure: { "color": "#ff6600", "short_label": "HN" }
    ui_config = Column(JSON, nullable=True, default=dict)

    # Configuration
    is_enabled = Column(Boolean, default=True, nullable=False)
    fetch_limit = Column(Integer, default=30, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_sources_slug", "slug"),
        Index("idx_sources_is_enabled", "is_enabled"),
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, slug={self.slug}, is_enabled={self.is_enabled})>"
