"""add vocabulary starred field

Revision ID: a3bb785_starred
Revises: 72a92f8f71a8
Create Date: 2026-06-19 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3bb785_starred'
down_revision: Union[str, None] = '72a92f8f71a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 5-P2-5: 生词本加 starred 字段 (用户重点词标记, 与 mastered 是两个维度)
    op.add_column('vocabularies', sa.Column('starred', sa.Boolean(), nullable=True))
    op.create_index('ix_vocabularies_starred', 'vocabularies', ['starred'])


def downgrade() -> None:
    op.drop_index('ix_vocabularies_starred', table_name='vocabularies')
    op.drop_column('vocabularies', 'starred')