from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from shared.schemas.article import ArticleResponse


class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark."""
    article_id: str


class BookmarkResponse(BaseModel):
    """Schema for bookmark API response (without article)."""
    id: UUID
    article_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkWithArticle(BaseModel):
    """Schema for bookmark with full article data."""
    id: UUID
    article: ArticleResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkCheckResponse(BaseModel):
    """Schema for bookmark check response."""
    bookmarked: bool
