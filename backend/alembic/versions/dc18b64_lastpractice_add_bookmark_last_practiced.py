"""add last_practiced_at to subtitle_bookmarks

Revision ID: dc18b64_lastpractice
Revises: fb4a4d1_usertags
Create Date: 2026-06-20 01:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc18b64_lastpractice'
down_revision = 'fb4a4d1_usertags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subtitle_bookmarks', sa.Column('last_practiced_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('subtitle_bookmarks', 'last_practiced_at')
