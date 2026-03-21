from datetime import datetime
from typing import Dict, Any, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.core.logging_config import get_logger
from app.core.database import AsyncSessionLocal
from app.services.sources import SourceAggregator

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()
_last_run: Optional[datetime] = None
_last_result: Optional[Dict[str, int]] = None


async def fetch_articles_job():
    """Background job to fetch articles from all sources."""
    global _last_run, _last_result

    logger.info("Starting scheduled article fetch...")
    _last_run = datetime.utcnow()

    try:
        async with AsyncSessionLocal() as db:
            async with SourceAggregator() as aggregator:
                stats = await aggregator.fetch_and_save(
                    db, limit_per_source=settings.FETCH_LIMIT_PER_SOURCE
                )

        _last_result = stats
        total = sum(stats.values())
        logger.info(f"Scheduled fetch complete: {total} articles saved")
        for source, count in stats.items():
            logger.info(f"  - {source}: {count}")

    except Exception as e:
        logger.error(f"Scheduled fetch failed: {e}")
        _last_result = {"error": str(e)}


def start_scheduler():
    """Start the background scheduler."""
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled via SCHEDULER_ENABLED=False")
        return

    if settings.REFRESH_INTERVAL_MINUTES > 0:
        scheduler.add_job(
            fetch_articles_job,
            trigger=IntervalTrigger(minutes=settings.REFRESH_INTERVAL_MINUTES),
            id="fetch_articles",
            name="Fetch articles from all sources",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Scheduler started (interval: {settings.REFRESH_INTERVAL_MINUTES} minutes)")
    else:
        logger.info("Scheduler disabled (REFRESH_INTERVAL_MINUTES=0)")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status."""
    jobs = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            })

    return {
        "running": scheduler.running,
        "enabled": settings.SCHEDULER_ENABLED,
        "interval_minutes": settings.REFRESH_INTERVAL_MINUTES,
        "jobs": jobs,
        "last_run": _last_run.isoformat() if _last_run else None,
        "last_result": _last_result,
    }
