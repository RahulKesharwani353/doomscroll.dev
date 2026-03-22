"""add sources and sync_jobs tables

Revision ID: add_sources_sync_jobs
Revises: 3fa4ae11e277
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_sources_sync_jobs'
down_revision: Union[str, None] = '3fa4ae11e277'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sources table
    op.create_table('sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('fetch_limit', sa.Integer(), nullable=False, default=30),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_sources_slug', 'sources', ['slug'], unique=False)
    op.create_index('idx_sources_is_enabled', 'sources', ['is_enabled'], unique=False)

    # Create sync_jobs table
    op.create_table('sync_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('source_slug', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('articles_fetched', sa.Integer(), nullable=True, default=0),
        sa.Column('articles_created', sa.Integer(), nullable=True, default=0),
        sa.Column('articles_updated', sa.Integer(), nullable=True, default=0),
        sa.Column('articles_failed', sa.Integer(), nullable=True, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_jobs_status', 'sync_jobs', ['status'], unique=False)
    op.create_index('idx_sync_jobs_source_id', 'sync_jobs', ['source_id'], unique=False)
    op.create_index('idx_sync_jobs_created_at', 'sync_jobs', [sa.text('created_at DESC')], unique=False)

    # Insert default sources
    op.execute("""
        INSERT INTO sources (slug, name, url, description, is_enabled, fetch_limit)
        VALUES
            ('hackernews', 'Hacker News', 'https://news.ycombinator.com', 'Tech news from Y Combinator', true, 30),
            ('devto', 'Dev.to', 'https://dev.to', 'Developer articles and tutorials', true, 30),
            ('reddit', 'Reddit', 'https://reddit.com', 'r/programming and r/webdev', true, 30),
            ('lobsters', 'Lobste.rs', 'https://lobste.rs', 'Curated tech content', true, 30)
    """)


def downgrade() -> None:
    op.drop_index('idx_sync_jobs_created_at', table_name='sync_jobs')
    op.drop_index('idx_sync_jobs_source_id', table_name='sync_jobs')
    op.drop_index('idx_sync_jobs_status', table_name='sync_jobs')
    op.drop_table('sync_jobs')

    op.drop_index('idx_sources_is_enabled', table_name='sources')
    op.drop_index('idx_sources_slug', table_name='sources')
    op.drop_table('sources')
