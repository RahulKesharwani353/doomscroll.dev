from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from enum import Enum

T = TypeVar("T")


class SourceType(str, Enum):
    HACKERNEWS = "hackernews"
    DEVTO = "devto"
    REDDIT = "reddit"
    LOBSTERS = "lobsters"


class BaseResponse(BaseModel):
    """Base class for all API responses."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


class DataResponse(BaseResponse, Generic[T]):
    """Response wrapper for single item endpoints."""
    data: T


class ListResponse(BaseResponse, Generic[T]):
    """Response wrapper for non-paginated list endpoints."""
    data: List[T]
    count: int = 0

    def __init__(self, **kwargs):
        if "count" not in kwargs and "data" in kwargs:
            kwargs["count"] = len(kwargs["data"])
        super().__init__(**kwargs)


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
    """Response wrapper for paginated list endpoints."""
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


ApiResponseDTO = DataResponse
ListResponseDTO = ListResponse
PaginatedResponseDTO = PaginatedResponse
ErrorResponseDTO = ErrorResponse


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = 1
    limit: int = 20
    source: Optional[str] = None

    def get_skip(self) -> int:
        return (self.page - 1) * self.limit


class HealthStatus(BaseModel):
    """Health check data."""
    status: str
    database: str
    version: str = "1.0.0"


class HealthResponse(DataResponse[HealthStatus]):
    """Health check response - follows standard pattern."""
    pass
