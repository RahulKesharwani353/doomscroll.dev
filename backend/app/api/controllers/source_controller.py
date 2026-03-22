from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceToggleRequest,
)
from shared.schemas.common import DataResponse, ListResponse
from app.services.source_service import SourceService, get_source_service
from shared.core.database import get_db
from shared.core.logging_config import get_logger

router = APIRouter(prefix="/sources", tags=["Sources"])
logger = get_logger(__name__)


@router.get("", response_model=ListResponse[SourceResponse])
async def get_sources(
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
) -> ListResponse[SourceResponse]:
    """Get all content sources."""
    try:
        return await source_service.get_sources(db)
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{source_id}", response_model=DataResponse[SourceResponse])
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
) -> DataResponse[SourceResponse]:
    """Get a specific source by ID."""
    try:
        source = await source_service.get_source_by_id(db, source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source with ID {source_id} not found"
            )
        return DataResponse(data=source)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving source with ID {source_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("", response_model=DataResponse[SourceResponse], status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: SourceCreate,
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
) -> DataResponse[SourceResponse]:
    """Create a new content source."""
    try:
        source = await source_service.create_source(db, source_data)
        return DataResponse(data=source, message="Source created successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{source_id}", response_model=DataResponse[SourceResponse])
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
) -> DataResponse[SourceResponse]:
    """Update an existing source."""
    try:
        source = await source_service.update_source(db, source_id, source_data)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source with ID {source_id} not found"
            )
        return DataResponse(data=source, message="Source updated successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source with ID {source_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
):
    """Delete a source."""
    try:
        success = await source_service.delete_source(db, source_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source with ID {source_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting source with ID {source_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/{source_id}/toggle", response_model=DataResponse[SourceResponse])
async def toggle_source(
    source_id: int,
    toggle_data: SourceToggleRequest,
    db: AsyncSession = Depends(get_db),
    source_service: SourceService = Depends(get_source_service)
) -> DataResponse[SourceResponse]:
    """Enable or disable a source."""
    try:
        source = await source_service.toggle_source(db, source_id, toggle_data.is_enabled)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source with ID {source_id} not found"
            )
        action = "enabled" if toggle_data.is_enabled else "disabled"
        return DataResponse(
            data=source,
            message=f"Source '{source.slug}' {action}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling source with ID {source_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
