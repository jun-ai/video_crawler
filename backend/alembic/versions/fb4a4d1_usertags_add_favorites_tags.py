"""add user tags for favorites

Revision ID: fb4a4d1_usertags
Revises: a3bb785_starred
Create Date: 2026-06-20 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb4a4d1_usertags'
down_revision: Union[str, None] = 'a3bb785_starred'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 5-P1-2: 用户自有标签 (与全局 Tag 区分)
    op.create_table(
        'user_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=20), server_default='#5c6ef5', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_tags_id', 'user_tags', ['id'])
    op.create_index('ix_user_tags_user_id', 'user_tags', ['user_id'])
    # (user_id, name) 唯一索引: 同一用户不能有同名标签
    op.create_index('ix_user_tags_user_name', 'user_tags', ['user_id', 'name'], unique=True)

    # 5-P1-2: bookmark-tag 关联表 (多对多)
    op.create_table(
        'bookmark_tags',
        sa.Column('bookmark_id', sa.Integer(), nullable=False),
        sa.Column('user_tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['bookmark_id'], ['subtitle_bookmarks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_tag_id'], ['user_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('bookmark_id', 'user_tag_id')
    )


def downgrade() -> None:
    op.drop_table('bookmark_tags')
    op.drop_index('ix_user_tags_user_name', table_name='user_tags')
    op.drop_index('ix_user_tags_user_id', table_name='user_tags')
    op.drop_index('ix_user_tags_id', table_name='user_tags')
    op.drop_table('user_tags')