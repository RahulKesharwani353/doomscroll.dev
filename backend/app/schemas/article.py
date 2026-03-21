from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional


class ArticleBase(BaseModel):
    """Base schema for article data."""

    title: str
    url: str
    author: Optional[str] = None
    source: str
    published_at: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """Schema for creating an article (internal use)."""

    id: str
    fetched_at: datetime = None

    def __init__(self, **data):
        if data.get("fetched_at") is None:
            data["fetched_at"] = datetime.utcnow()
        super().__init__(**data)


class ArticleResponse(ArticleBase):
    """Schema for article API responses."""

    id: str
    fetched_at: datetime
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
