from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.services.sources import SourceAggregator

router = APIRouter(prefix="/admin/fetch", tags=["Admin - Fetch"])
logger = get_logger(__name__)


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != settings.MIGRATION_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key


@router.post("", response_model=Dict[str, int])
async def fetch_all_sources(
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, int]:
    """Fetch articles from all sources and save to database."""
    try:
        async with SourceAggregator() as aggregator:
            stats = await aggregator.fetch_and_save(db, limit_per_source=limit)

        return stats
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{source}", response_model=Dict[str, int])
async def fetch_single_source(
    source: str,
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, int]:
    """Fetch articles from a specific source."""
    from app.services.sources import HackerNewsClient, DevToClient, RedditClient, LobstersClient
    from app.services.article_service import ArticleService
    from app.repositories.article_repository import ArticleRepository

    clients = {
        "hackernews": HackerNewsClient,
        "devto": DevToClient,
        "reddit": RedditClient,
        "lobsters": LobstersClient,
    }

    if source not in clients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source. Valid sources: {', '.join(clients.keys())}"
        )

    try:
        async with clients[source]() as client:
            articles = await client.fetch_articles(limit)

        article_service = ArticleService(ArticleRepository())
        count = await article_service.upsert_articles(db, articles)

        return {source: count}
    except Exception as e:
        logger.error(f"Error fetching from {source}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
