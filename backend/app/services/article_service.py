from typing import Optional, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.article import Article
from shared.schemas.article import ArticleResponse, ArticleCreate
from shared.schemas.common import PaginatedResponse
from shared.core.logging_config import get_logger
from app.repositories.article_repository import ArticleRepository, get_article_repository
from app.cache.cache_service import CacheService, get_cache_service
from app.config import settings

logger = get_logger(__name__)


class ArticleService:
    """Service layer for article business logic."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        cache_service: Optional[CacheService] = None
    ):
        self.repository = article_repository
        self._cache = cache_service

    async def get_articles(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None
    ) -> PaginatedResponse[ArticleResponse]:
        """Get paginated list of articles with optional source filter."""
        # Check cache first
        if self._cache:
            cache_key = self._cache.articles_key(page, limit, source)
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for articles: {cache_key}")
                return PaginatedResponse[ArticleResponse](**cached)

        # Fetch from database
        skip = (page - 1) * limit
        articles, _ = await self.repository.get_articles(
            db=db,
            skip=skip,
            limit=limit,
            source=source
        )

        total_count = await self.repository.count_articles(db=db, source=source)
        article_dtos = [ArticleResponse.model_validate(article) for article in articles]

        response = PaginatedResponse.create(
            data=article_dtos,
            page=page,
            limit=limit,
            total=total_count
        )

        # Store in cache
        if self._cache:
            await self._cache.set(
                cache_key,
                response.model_dump(),
                ttl=settings.CACHE_TTL_SHORT
            )

        return response

    async def get_article_by_id(
        self,
        db: AsyncSession,
        article_id: str
    ) -> Optional[ArticleResponse]:
        """Get a single article by ID."""
        article = await self.repository.get(db=db, id=article_id)
        if article:
            return ArticleResponse.model_validate(article)
        return None

    async def upsert_articles(
        self,
        db: AsyncSession,
        articles: List[ArticleCreate]
    ) -> int:
        """Bulk upsert articles (insert new, update existing)."""
        if not articles:
            return 0

        article_dicts = [article.model_dump() for article in articles]
        return await self.repository.upsert_many(db=db, articles=article_dicts)

    async def search_articles(
        self,
        db: AsyncSession,
        query: str,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None
    ) -> PaginatedResponse[ArticleResponse]:
        """Search articles by title with pagination, optionally filtered by source."""
        # Check cache first
        if self._cache:
            cache_key = self._cache.search_key(query, page, limit, source)
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for search: {cache_key}")
                return PaginatedResponse[ArticleResponse](**cached)

        # Fetch from database
        skip = (page - 1) * limit
        articles = await self.repository.search_by_title(
            db=db,
            search_term=query,
            skip=skip,
            limit=limit,
            source=source
        )
        total_count = await self.repository.count_search_results(db=db, search_term=query, source=source)
        article_dtos = [ArticleResponse.model_validate(article) for article in articles]

        response = PaginatedResponse.create(
            data=article_dtos,
            page=page,
            limit=limit,
            total=total_count
        )

        # Store in cache
        if self._cache:
            await self._cache.set(
                cache_key,
                response.model_dump(),
                ttl=settings.CACHE_TTL_SHORT
            )

        return response

    async def get_articles_by_source(
        self,
        db: AsyncSession,
        source: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[ArticleResponse]:
        """Get articles from a specific source."""
        articles = await self.repository.get_by_source(
            db=db,
            source=source,
            skip=skip,
            limit=limit
        )
        return [ArticleResponse.model_validate(article) for article in articles]

    async def cleanup_old_articles(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> int:
        """Delete articles older than specified days."""
        return await self.repository.delete_old_articles(db=db, days=days)


async def get_article_service(
    article_repository: ArticleRepository = Depends(get_article_repository)
) -> ArticleService:
    """Dependency injection for ArticleService."""
    cache_service = await get_cache_service()
    return ArticleService(article_repository=article_repository, cache_service=cache_service)
