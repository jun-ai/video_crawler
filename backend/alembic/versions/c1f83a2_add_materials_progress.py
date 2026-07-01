"""add materials.progress for live regen tracking

Revision ID: c1f83a2_progress
Revises: d7a8e2f_bookmarkfolders
Create Date: 2026-06-30 10:30:00.000000

当 admin 替换字幕或重新解读时,后台任务每个阶段 (parse / translate
/ words / phrases / grammar / idioms) 写一个 JSON 进去,
前端 GET /api/materials/{id}/progress 轮询展示进度 + 错误。

JSON 样例 (写入 materials.progress):
{
  "stages": [
    {"key": "parse",      "label": "解析新字幕",     "status": "done",   "started_at": "...", "finished_at": "..."},
    {"key": "translate",  "label": "字幕 EN→CN 翻译", "status": "running", "progress": "15/40", "started_at": "..."},
    {"key": "words",      "label": "AI 生成单词",     "status": "pending"},
    ...
  ],
  "updated_at": "...",
  "error": null
}
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1f83a2_progress'
down_revision: Union[str, None] = 'd7a8e2f_bookmarkfolders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'materials',
        sa.Column('progress', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('materials', 'progress')
