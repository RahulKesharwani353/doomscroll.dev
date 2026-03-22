from fastapi import APIRouter

from shared.core.database import check_db_connection
from shared.schemas.common import DataResponse, HealthStatus
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=DataResponse[HealthStatus])
async def health_check() -> DataResponse[HealthStatus]:
    """Health check endpoint."""
    db_connected = await check_db_connection()
    status_data = HealthStatus(
        status="ok" if db_connected else "degraded",
        database="connected" if db_connected else "disconnected",
        version=settings.APP_VERSION,
    )
    return DataResponse(data=status_data)
