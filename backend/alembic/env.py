import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core.database import Base

# Import all models for autogenerate support
# This ensures Alembic can detect all model changes
from app.models import *  # noqa: F401, F403

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
# Skip logging configuration when running programmatically to avoid
# overriding the application's logging configuration
if config.config_file_name is not None and not config.attributes.get('configure_logger', True):
    pass
elif config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate support
target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from settings."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations with sync connection in async context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations_impl() -> None:
    """Async implementation of migrations."""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_async_migrations() -> None:
    """Run migrations in async mode."""
    asyncio.run(run_async_migrations_impl())


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Creates an async Engine and runs migrations.
    """
    run_async_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
