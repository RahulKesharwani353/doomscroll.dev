from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func

from shared.core.database import Base


class Article(Base):
    """Article model representing a normalized article from any source."""

    __tablename__ = "articles"

    id = Column(String(100), primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False)
    author = Column(String(200), nullable=True)
    source = Column(String(50), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_articles_source", "source"),
        Index("idx_articles_published_at", published_at.desc()),
        Index("idx_articles_source_published", "source", published_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title={self.title[:30]}..., source={self.source})>"
