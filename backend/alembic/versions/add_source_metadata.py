"""add ui_config column to sources

Revision ID: add_source_ui_config
Revises: add_sources_sync_jobs
Create Date: 2026-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_source_ui_config'
down_revision: Union[str, None] = 'add_sources_sync_jobs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ui_config column to sources table
    op.add_column('sources', sa.Column('ui_config', sa.JSON(), nullable=True))

    # Update existing sources with default ui_config
    op.execute("""
        UPDATE sources SET ui_config = '{"color": "#ff6600", "short_label": "HN"}'::jsonb WHERE slug = 'hackernews';
    """)
    op.execute("""
        UPDATE sources SET ui_config = '{"color": "#3b82f6", "short_label": "DEV"}'::jsonb WHERE slug = 'devto';
    """)
    op.execute("""
        UPDATE sources SET ui_config = '{"color": "#ff4500", "short_label": "R"}'::jsonb WHERE slug = 'reddit';
    """)
    op.execute("""
        UPDATE sources SET ui_config = '{"color": "#dc2626", "short_label": "L"}'::jsonb WHERE slug = 'lobsters';
    """)


def downgrade() -> None:
    op.drop_column('sources', 'ui_config')
