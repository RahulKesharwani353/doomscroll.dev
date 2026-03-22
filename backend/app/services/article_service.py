from typing import Optional, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.article import Article
from shared.schemas.article import ArticleResponse, ArticleCreate
from shared.schemas.common import PaginatedResponse
from app.repositories.article_repository import ArticleRepository, get_article_repository


class ArticleService:
    """Service layer for article business logic."""

    def __init__(self, article_repository: ArticleRepository):
        self.repository = article_repository

    async def get_articles(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None
    ) -> PaginatedResponse[ArticleResponse]:
        """Get paginated list of articles with optional source filter."""
        skip = (page - 1) * limit
        articles, _ = await self.repository.get_articles(
            db=db,
            skip=skip,
            limit=limit,
            source=source
        )

        total_count = await self.repository.count_articles(db=db, source=source)
        article_dtos = [ArticleResponse.model_validate(article) for article in articles]

        return PaginatedResponse.create(
            data=article_dtos,
            page=page,
            limit=limit,
            total=total_count
        )

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
        limit: int = 20
    ) -> PaginatedResponse[ArticleResponse]:
        """Search articles by title with pagination."""
        skip = (page - 1) * limit
        articles = await self.repository.search_by_title(
            db=db,
            search_term=query,
            skip=skip,
            limit=limit
        )
        total_count = await self.repository.count_search_results(db=db, search_term=query)
        article_dtos = [ArticleResponse.model_validate(article) for article in articles]

        return PaginatedResponse.create(
            data=article_dtos,
            page=page,
            limit=limit,
            total=total_count
        )

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


def get_article_service(
    article_repository: ArticleRepository = Depends(get_article_repository)
) -> ArticleService:
    """Dependency injection for ArticleService."""
    return ArticleService(article_repository=article_repository)
