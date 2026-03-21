from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    source: Optional[str] = Field(default=None, description="Filter by source")


class PaginationMeta(BaseModel):
    """Pagination metadata in responses."""

    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    success: bool = True
    data: List[T]
    pagination: PaginationMeta


class SourceInfo(BaseModel):
    """Information about a content source."""

    id: str
    name: str
    url: str
    description: Optional[str] = None


class SourcesResponse(BaseModel):
    """Response for listing available sources."""

    success: bool = True
    sources: List[SourceInfo]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    database: str
    version: str = "1.0.0"
