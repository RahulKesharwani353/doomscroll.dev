import asyncio
from typing import Any, Dict, Optional

import alembic.command
import alembic.config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.config import settings
from shared.core.logging_config import get_logger

router = APIRouter(prefix="/admin/migrations", tags=["Admin - Migrations"])
logger = get_logger(__name__)


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != settings.MIGRATION_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key


def get_alembic_config() -> alembic.config.Config:
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_cfg.attributes['configure_logger'] = False
    return alembic_cfg


@router.get("/current", response_model=Dict[str, Any])
async def get_current_revision(api_key: str = Depends(verify_api_key)):
    """Get the current database migration revision."""
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)

        # Get current revision from database
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))

        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        engine.dispose()

        # Get head revision
        head_rev = script.get_current_head()

        return {
            "current_revision": current_rev or "None (no migrations applied)",
            "head_revision": head_rev or "None",
            "is_up_to_date": current_rev == head_rev
        }
    except Exception as e:
        logger.error(f"Failed to get current revision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current revision: {str(e)}"
        )


@router.post("/upgrade", response_model=Dict[str, str])
async def run_migrations(api_key: str = Depends(verify_api_key)):
    """Run database migrations to the latest version."""
    try:
        alembic_cfg = get_alembic_config()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: alembic.command.upgrade(alembic_cfg, "head"))
        return {"status": "success", "message": "Database migrations completed successfully"}
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Migration failed: {str(e)}")


@router.post("/upgrade/{revision_id}", response_model=Dict[str, str])
async def run_migration_by_id(revision_id: str, api_key: str = Depends(verify_api_key)):
    """Run database migration to a specific revision ID."""
    try:
        alembic_cfg = get_alembic_config()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: alembic.command.upgrade(alembic_cfg, revision_id))
        return {"status": "success", "message": f"Database migrated to revision {revision_id} successfully"}
    except Exception as e:
        logger.error(f"Migration to revision {revision_id} failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Migration failed: {str(e)}")


@router.post("/downgrade", response_model=Dict[str, str])
async def downgrade_migrations(
    revisions: Optional[int] = Query(1, ge=1),
    api_key: str = Depends(verify_api_key)
):
    """Downgrade database migrations by a specified number of revisions."""
    try:
        alembic_cfg = get_alembic_config()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: alembic.command.downgrade(alembic_cfg, f"-{revisions}"))
        return {"status": "success", "message": f"Database downgraded by {revisions} revision(s) successfully"}
    except Exception as e:
        logger.error(f"Downgrade failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Downgrade failed: {str(e)}")


@router.get("/history", response_model=Dict[str, list])
async def get_migration_history(api_key: str = Depends(verify_api_key)):
    """Get the list of all available migrations."""
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)

        revisions = []
        for revision in script.walk_revisions():
            revisions.append({
                "revision": revision.revision,
                "down_revision": revision.down_revision,
                "description": revision.doc or "No description"
            })

        return {"migrations": revisions}
    except Exception as e:
        logger.error(f"Failed to get migration history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get migration history: {str(e)}"
        )
