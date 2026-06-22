"""
标签管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Annotated, List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.models import Tag, MaterialTag, Material
from app.schemas.schemas import TagResponse, MessageResponse
from app.routers.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/api/tags", tags=["标签"])


class TagCreate(BaseModel):
    name: str
    type: str  # 'creator' or 'topic'
    color: str = '#5c6ef5'
    display_order: int = 0


class TagUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    display_order: Optional[int] = None


@router.get("", response_model=List[TagResponse])
async def get_tags(
    type: Optional[str] = Query(None, description="标签类型: creator/topic"),
    db: AsyncSession = Depends(get_db)
):
    """获取标签列表（公开接口）"""
    query = select(Tag)
    if type:
        query = query.where(Tag.type == type)
    query = query.order_by(Tag.display_order, Tag.name)

    result = await db.execute(query)
    tags = result.scalars().all()
    return tags


# ==================== 管理员接口 ====================

@router.post("", response_model=TagResponse)
async def create_tag(
    data: TagCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """创建标签（管理员）"""
    if current_user.role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")

    # 检查重名
    result = await db.execute(select(Tag).where(Tag.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签名称已存在")

    tag = Tag(
        name=data.name,
        type=data.type,
        color=data.color,
        display_order=data.display_order
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """更新标签（管理员）"""
    if current_user.role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")

    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")

    if data.name is not None:
        tag.name = data.name
    if data.type is not None:
        tag.type = data.type
    if data.color is not None:
        tag.color = data.color
    if data.display_order is not None:
        tag.display_order = data.display_order

    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=MessageResponse)
async def delete_tag(
    tag_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """删除标签（管理员）"""
    if current_user.role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")

    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
    return MessageResponse(message="标签已删除", success=True)
