from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from enum import Enum

T = TypeVar("T")


class SourceType(str, Enum):
    HACKERNEWS = "hackernews"
    DEVTO = "devto"
    REDDIT = "reddit"
    LOBSTERS = "lobsters"


# =============================================================================
# Base Response Classes
# =============================================================================

class BaseResponse(BaseModel):
    """Base class for all API responses."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# =============================================================================
# Single Item Response
# =============================================================================

class DataResponse(BaseResponse, Generic[T]):
    """
    Response for single item endpoints.

    Usage:
        GET /articles/{id} -> DataResponse[ArticleResponse]
        GET /sources/{id} -> DataResponse[SourceResponse]
    """
    data: T


# =============================================================================
# List Response (Non-paginated)
# =============================================================================

class ListResponse(BaseResponse, Generic[T]):
    """
    Response for list endpoints without pagination.

    Usage:
        GET /sources -> ListResponse[SourceResponse]
        GET /sync/jobs -> ListResponse[SyncJobResponse]
    """
    data: List[T]
    count: int = 0

    def __init__(self, **kwargs):
        if "count" not in kwargs and "data" in kwargs:
            kwargs["count"] = len(kwargs["data"])
        super().__init__(**kwargs)


# =============================================================================
# Paginated Response
# =============================================================================

class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMeta":
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    Response for paginated list endpoints.

    Usage:
        GET /articles -> PaginatedResponse[ArticleResponse]
        GET /articles/search -> PaginatedResponse[ArticleResponse]
    """
    data: List[T]
    pagination: PaginationMeta

    @classmethod
    def create(
        cls,
        data: List[T],
        page: int,
        limit: int,
        total: int,
        message: Optional[str] = None
    ) -> "PaginatedResponse[T]":
        return cls(
            data=data,
            pagination=PaginationMeta.create(page, limit, total),
            message=message
        )


# =============================================================================
# Legacy Aliases (for backwards compatibility during migration)
# =============================================================================

# TODO: Remove these after all controllers are updated
ApiResponseDTO = DataResponse
ListResponseDTO = ListResponse
PaginatedResponseDTO = PaginatedResponse
ErrorResponseDTO = ErrorResponse


# =============================================================================
# Utility Classes
# =============================================================================

class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = 1
    limit: int = 20
    source: Optional[str] = None

    def get_skip(self) -> int:
        return (self.page - 1) * self.limit


# =============================================================================
# Special Response Types
# =============================================================================

class HealthStatus(BaseModel):
    """Health check data."""
    status: str
    database: str
    version: str = "1.0.0"


class HealthResponse(DataResponse[HealthStatus]):
    """Health check response - follows standard pattern."""
    pass
