from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from enum import Enum

T = TypeVar("T")


class SourceType(str, Enum):
    HACKERNEWS = "hackernews"
    DEVTO = "devto"
    REDDIT = "reddit"
    LOBSTERS = "lobsters"


class ApiResponseDTO(BaseModel):
    success: bool = True
    data: dict | None = None
    message: Optional[str] = None


class ErrorResponseDTO(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


class ListResponseDTO(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    count: int = 0

    def __init__(self, **kwargs):
        if "count" not in kwargs and "data" in kwargs:
            kwargs["count"] = len(kwargs["data"])
        super().__init__(**kwargs)


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
    source: Optional[str] = None

    def get_skip(self) -> int:
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMeta":
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponseDTO(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    current_count: int
    total_count: int
    page: int
    max_items_per_page: int

    @property
    def total_pages(self) -> int:
        if self.max_items_per_page <= 0:
            return 0
        return (self.total_count + self.max_items_per_page - 1) // self.max_items_per_page

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


class SourceInfo(BaseModel):
    id: str
    name: str
    url: str
    description: Optional[str] = None


class SourcesResponse(BaseModel):
    success: bool = True
    sources: List[SourceInfo]


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str = "1.0.0"
