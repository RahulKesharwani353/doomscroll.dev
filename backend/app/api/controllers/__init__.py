from fastapi import APIRouter

from .health_controller import router as health_router
from .article_controller import router as article_router
from .source_controller import router as source_router
from .sync_controller import router as sync_router
from .migration_controller import router as migration_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(article_router)
api_router.include_router(source_router)
api_router.include_router(sync_router)
api_router.include_router(migration_router)
