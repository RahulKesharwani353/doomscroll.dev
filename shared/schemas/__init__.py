from .article import ArticleBase, ArticleCreate, ArticleResponse
from .common import (
    # Core types
    SourceType,
    # Base response
    BaseResponse,
    ErrorResponse,
    # Response wrappers
    DataResponse,
    ListResponse,
    PaginatedResponse,
    # Pagination
    PaginationParams,
    PaginationMeta,
    # Health
    HealthStatus,
    # Legacy aliases (for backwards compatibility)
    ApiResponseDTO,
    ErrorResponseDTO,
    ListResponseDTO,
    PaginatedResponseDTO,
)
from .source import (
    SourceBase,
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceToggleRequest,
)
from .sync_job import (
    SyncJobStatus,
    SyncJobCreate,
    SyncJobUpdate,
    SyncJobResponse,
    SyncStatusResponse,
    SyncTriggerRequest,
    SyncTriggerResponse,
)

__all__ = [
    # Article
    "ArticleBase",
    "ArticleCreate",
    "ArticleResponse",
    # Common - Core
    "SourceType",
    "BaseResponse",
    "ErrorResponse",
    # Common - Response wrappers
    "DataResponse",
    "ListResponse",
    "PaginatedResponse",
    # Common - Pagination
    "PaginationParams",
    "PaginationMeta",
    # Common - Health
    "HealthStatus",
    # Common - Legacy aliases
    "ApiResponseDTO",
    "ErrorResponseDTO",
    "ListResponseDTO",
    "PaginatedResponseDTO",
    # Source
    "SourceBase",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "SourceToggleRequest",
    # Sync Job
    "SyncJobStatus",
    "SyncJobCreate",
    "SyncJobUpdate",
    "SyncJobResponse",
    "SyncStatusResponse",
    "SyncTriggerRequest",
    "SyncTriggerResponse",
]
