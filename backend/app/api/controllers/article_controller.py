from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.schemas.article import ArticleResponse
from app.schemas.common import ApiResponseDTO, PaginatedResponseDTO, ListResponseDTO
from app.services.article_service import ArticleService, get_article_service
from app.utils.validation import is_valid_source, is_valid_search_query, get_valid_sources, sanitize_input

router = APIRouter(prefix="/articles", tags=["Articles"])
logger = get_logger(__name__)


@router.get("", response_model=PaginatedResponseDTO[ArticleResponse])
async def get_articles(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    article_service: ArticleService = Depends(get_article_service)
) -> PaginatedResponseDTO[ArticleResponse]:
    """Get paginated list of articles."""
    try:
        if source and not is_valid_source(source):
            raise ValueError(f"Invalid source '{source}'. Valid: {', '.join(get_valid_sources())}")

        skip = (page - 1) * limit
        return await article_service.get_articles(db=db, skip=skip, limit=limit, source=source)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/search", response_model=ListResponseDTO[ArticleResponse])
async def search_articles(
    q: str = Query(..., min_length=2, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    article_service: ArticleService = Depends(get_article_service)
) -> ListResponseDTO[ArticleResponse]:
    """Search articles by title."""
    try:
        if not is_valid_search_query(q):
            raise ValueError("Invalid characters in search query")

        skip = (page - 1) * limit
        query = sanitize_input(q)
        articles = await article_service.search_articles(db=db, query=query, skip=skip, limit=limit)
        return ListResponseDTO(data=articles)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{article_id}", response_model=ApiResponseDTO)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    article_service: ArticleService = Depends(get_article_service)
) -> ApiResponseDTO:
    """Get a single article by ID."""
    try:
        article_id = sanitize_input(article_id)
        article = await article_service.get_article_by_id(db=db, article_id=article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article '{article_id}' not found")
        return ApiResponseDTO(data=article.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
