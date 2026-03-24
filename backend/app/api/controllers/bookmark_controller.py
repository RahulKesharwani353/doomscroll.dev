from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import get_db
from shared.core.logging_config import get_logger
from shared.schemas.bookmark import (
    BookmarkCreate,
    BookmarkWithArticle,
    BookmarkCheckResponse,
)
from shared.schemas.common import DataResponse, PaginatedResponse
from shared.models.user import User
from app.services.bookmark_service import BookmarkService, get_bookmark_service
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])
logger = get_logger(__name__)


@router.get("", response_model=PaginatedResponse[BookmarkWithArticle])
async def get_bookmarks(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
) -> PaginatedResponse[BookmarkWithArticle]:
    """Get user's bookmarked articles (paginated)."""
    try:
        return await bookmark_service.get_bookmarks(
            db=db,
            user_id=current_user.id,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching bookmarks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookmarks"
        )


@router.post("", response_model=DataResponse[BookmarkWithArticle], status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
) -> DataResponse[BookmarkWithArticle]:
    """Bookmark an article."""
    try:
        bookmark = await bookmark_service.add_bookmark(
            db=db,
            user_id=current_user.id,
            article_id=bookmark_data.article_id
        )
        return DataResponse(data=bookmark)
    except Exception as e:
        logger.error(f"Error adding bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add bookmark"
        )


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    article_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
):
    """Remove a bookmark."""
    try:
        deleted = await bookmark_service.remove_bookmark(
            db=db,
            user_id=current_user.id,
            article_id=article_id
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove bookmark"
        )


@router.get("/check/{article_id}", response_model=DataResponse[BookmarkCheckResponse])
async def check_bookmark(
    article_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    bookmark_service: BookmarkService = Depends(get_bookmark_service)
) -> DataResponse[BookmarkCheckResponse]:
    """Check if an article is bookmarked."""
    try:
        is_bookmarked = await bookmark_service.is_bookmarked(
            db=db,
            user_id=current_user.id,
            article_id=article_id
        )
        return DataResponse(data=BookmarkCheckResponse(bookmarked=is_bookmarked))
    except Exception as e:
        logger.error(f"Error checking bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check bookmark status"
        )
