#!/usr/bin/env python
"""
Sync script for fetching articles from all enabled sources.

This script is designed to be run as a cron job or scheduled task.
It fetches articles from all enabled sources in the database and saves them.

Usage:
    python sync_service/run_sync.py [--source SOURCE_SLUG]

Options:
    --source    Sync only a specific source (by slug)

Example cron entry (every 15 minutes):
    */15 * * * * cd /path/to/project && python sync_service/run_sync.py

Windows Task Scheduler:
    Program: python
    Arguments: sync_service/run_sync.py
    Start in: C:\\path\\to\\project
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from shared.core.logging_config import setup_logging, get_logger
from shared.core.database import AsyncSessionLocal
from sync_service.app.sources.aggregator import SourceAggregator
from sync_service.app.repositories.sync_job_repository import SyncJobRepository
from sync_service.app.repositories.source_repository import SourceRepository

setup_logging()
logger = get_logger(__name__)


async def run_sync(source_slug: str = None) -> int:
    """
    Run the sync process.

    Args:
        source_slug: If provided, sync only this source. Otherwise, sync all enabled.

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    logger.info("=" * 60)
    logger.info("Starting sync job...")
    logger.info(f"Source: {source_slug or 'all enabled sources'}")
    logger.info("=" * 60)

    sync_job_repo = SyncJobRepository()
    source_repo = SourceRepository()

    async with AsyncSessionLocal() as db:
        try:
            # Validate source if specified
            source_id = None
            if source_slug:
                source = await source_repo.get_by_slug(db, source_slug)
                if not source:
                    logger.error(f"Source '{source_slug}' not found")
                    return 1
                if not source.is_enabled:
                    logger.error(f"Source '{source_slug}' is disabled")
                    return 1
                source_id = source.id

            # Create sync job record
            job = await sync_job_repo.create_job(
                db,
                source_id=source_id,
                source_slug=source_slug
            )
            job = await sync_job_repo.start_job(db, job.id)
            logger.info(f"Created sync job #{job.id}")

            # Initialize aggregator
            aggregator = SourceAggregator()
            await aggregator.init_from_db(db, source_slug=source_slug)

            if not aggregator.clients:
                logger.warning("No sources to sync")
                await sync_job_repo.complete_job(db, job.id)
                return 0

            # Fetch and save articles
            try:
                result = await aggregator.fetch_and_save(db)
            finally:
                await aggregator.close()

            # Calculate totals
            total_fetched = sum(result.stats.values())
            total_failed = len([s for s, c in result.stats.items() if c == 0])

            # Log per-source stats
            for source_name, count in result.stats.items():
                logger.info(f"  - {source_name}: {count} articles")

            # Build error message if there were any errors
            error_message = None
            if result.errors:
                error_message = "; ".join(result.errors)
                logger.warning(f"Sync completed with errors: {error_message}")

            # Mark job as completed (with errors if any)
            await sync_job_repo.complete_job(
                db,
                job.id,
                articles_fetched=total_fetched,
                articles_created=total_fetched,  # upsert returns affected count
                articles_updated=0,
                articles_failed=total_failed,
                error_message=error_message,
            )

            logger.info("=" * 60)
            logger.info(f"Sync completed successfully")
            logger.info(f"Total articles: {total_fetched}")
            logger.info(f"Job ID: #{job.id}")
            logger.info("=" * 60)

            return 0

        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)

            # Try to mark job as failed if we have a job
            try:
                if 'job' in locals():
                    await sync_job_repo.fail_job(
                        db,
                        job.id,
                        error_message=str(e)
                    )
            except Exception as job_error:
                logger.error(f"Failed to update job status: {job_error}")

            return 1


def main():
    parser = argparse.ArgumentParser(
        description="Sync articles from content sources"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Sync only a specific source (by slug)"
    )
    args = parser.parse_args()

    try:
        exit_code = asyncio.run(run_sync(source_slug=args.source))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Sync interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
