"""add bookmark folders for favorites

Revision ID: d7a8e2f_bookmarkfolders
Revises: dc18b64_lastpractice
Create Date: 2026-06-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7a8e2f_bookmarkfolders'
down_revision: Union[str, None] = 'dc18b64_lastpractice'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 5-P1-2 (后缀): 用户字幕收藏文件夹
    # 顶层分组容器 (与 UserTag 多对多区分, 一个 bookmark 只能属于一个 folder)
    op.create_table(
        'bookmark_folders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=20), server_default='#5c6ef5', nullable=True),
        sa.Column('icon', sa.String(length=30), server_default='folder', nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bookmark_folders_id', 'bookmark_folders', ['id'])
    op.create_index('ix_bookmark_folders_user_id', 'bookmark_folders', ['user_id'])
    # (user_id, name) 唯一索引: 同一用户不能有同名文件夹
    op.create_index('ix_bookmark_folders_user_name', 'bookmark_folders', ['user_id', 'name'], unique=True)

    # subtitle_bookmarks 加 folder_id 列 (nullable, 删文件夹时 SET NULL 保留 bookmark)
    op.add_column('subtitle_bookmarks', sa.Column('folder_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_subtitle_bookmarks_folder_id',
        'subtitle_bookmarks', 'bookmark_folders',
        ['folder_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_subtitle_bookmarks_folder_id', 'subtitle_bookmarks', ['folder_id'])


def downgrade() -> None:
    op.drop_index('ix_subtitle_bookmarks_folder_id', table_name='subtitle_bookmarks')
    op.drop_constraint('fk_subtitle_bookmarks_folder_id', 'subtitle_bookmarks', type_='foreignkey')
    op.drop_column('subtitle_bookmarks', 'folder_id')

    op.drop_index('ix_bookmark_folders_user_name', table_name='bookmark_folders')
    op.drop_index('ix_bookmark_folders_user_id', table_name='bookmark_folders')
    op.drop_index('ix_bookmark_folders_id', table_name='bookmark_folders')
    op.drop_table('bookmark_folders')
