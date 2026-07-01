"""widen subtitle_annotations.color from 20 to 50 (前端发 CSS var 字符串超 20)

Revision ID: a8f3b1_widen_annotation_color
Revises: c1f83a2_progress
Create Date: 2026-06-30 14:30:00.000000

前端的 annotationColors 存的是 'var(--color-annotation-vocabulary)' 这种 CSS 变量字符串 (28 字符),
原 schema 是 String(20) 装不下,导致 POST /api/learning/annotations 返回 500。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f3b1_widen_annotation_color'
down_revision: Union[str, None] = 'c1f83a2_progress'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE subtitle_annotations MODIFY COLUMN color VARCHAR(50) NOT NULL DEFAULT '#ff0000'")


def downgrade() -> None:
    # 警告: 如果已有 > 20 字符的 color 数据,降级会失败
    op.execute("ALTER TABLE subtitle_annotations MODIFY COLUMN color VARCHAR(20) NOT NULL DEFAULT '#ff0000'")
