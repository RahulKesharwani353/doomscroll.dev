from typing import Dict, Any

from fastapi import APIRouter

from app.core.database import check_db_connection
from app.core.scheduler import get_scheduler_status
from app.schemas.common import HealthResponse
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    db_connected = await check_db_connection()
    return HealthResponse(
        status="ok" if db_connected else "degraded",
        database="connected" if db_connected else "disconnected",
        version=settings.APP_VERSION,
    )


@router.get("/scheduler", response_model=Dict[str, Any])
async def scheduler_status() -> Dict[str, Any]:
    """Get scheduler status and job information."""
    return get_scheduler_status()
