from fastapi import APIRouter

from app.core.database import check_db_connection
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the status of the API and database connection.
    """
    db_connected = await check_db_connection()

    return HealthResponse(
        status="ok" if db_connected else "degraded",
        database="connected" if db_connected else "disconnected",
        version="1.0.0",
    )
