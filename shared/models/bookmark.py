import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared.core.database import Base


class Bookmark(Base):
    """Bookmark model for saving articles."""

    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(String(100), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_user_article"),
        Index("idx_bookmarks_user_id", "user_id"),
        Index("idx_bookmarks_article_id", "article_id"),
    )

    def __repr__(self) -> str:
        return f"<Bookmark(id={self.id}, user_id={self.user_id}, article_id={self.article_id})>"
