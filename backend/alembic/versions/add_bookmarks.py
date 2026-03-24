"""add bookmarks table

Revision ID: add_bookmarks
Revises: add_users_table
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'add_bookmarks'
down_revision: Union[str, None] = 'add_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bookmarks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('article_id', sa.String(100), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'article_id', name='uq_user_article'),
    )
    op.create_index('idx_bookmarks_user_id', 'bookmarks', ['user_id'])
    op.create_index('idx_bookmarks_article_id', 'bookmarks', ['article_id'])


def downgrade() -> None:
    op.drop_index('idx_bookmarks_article_id', table_name='bookmarks')
    op.drop_index('idx_bookmarks_user_id', table_name='bookmarks')
    op.drop_table('bookmarks')
