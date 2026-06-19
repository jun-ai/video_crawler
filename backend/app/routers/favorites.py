"""
收藏功能路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Annotated, List
from datetime import datetime

from app.database import get_db
from app.models.models import User, Material, Favorite
from app.schemas.schemas import MessageResponse
from app.routers.auth import get_current_user
from app.routers.materials import get_file_url

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


@router.post("/{material_id}", response_model=MessageResponse)
async def add_favorite(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """添加收藏"""
    # 检查语料是否存在
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语料不存在"
        )

    # 检查是否已收藏
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.material_id == material_id
        )
    )
    if result.scalar_one_or_none():
        return MessageResponse(message="已收藏", success=True)

    # 添加收藏
    favorite = Favorite(
        user_id=current_user.id,
        material_id=material_id
    )
    db.add(favorite)
    await db.commit()

    return MessageResponse(message="收藏成功", success=True)


@router.delete("/{material_id}", response_model=MessageResponse)
async def remove_favorite(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """取消收藏"""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.material_id == material_id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏该语料"
        )

    await db.delete(favorite)
    await db.commit()

    return MessageResponse(message="已取消收藏", success=True)


@router.get("/check/{material_id}")
async def check_favorite(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """检查是否已收藏"""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.material_id == material_id
        )
    )
    is_favorited = result.scalar_one_or_none() is not None

    return {"is_favorited": is_favorited}


@router.get("")
async def get_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取收藏列表（按时间倒序）"""
    # P2-9: 用 func.count 替代 len(result.scalars().all()) 避免 O(n) 内存
    from sqlalchemy import func
    count_query = select(func.count(Favorite.id)).where(Favorite.user_id == current_user.id)
    total = (await db.execute(count_query)).scalar_one()

    # 分页查询收藏列表
    offset = (page - 1) * page_size
    query = (
        select(Favorite, Material)
        .join(Material, Favorite.material_id == Material.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()

    items = []
    for favorite, material in rows:
        items.append({
            "id": material.id,
            "title": material.title,
            "description": material.description,
            "cover_path": get_file_url(material.cover_path),
            "video_path": get_file_url(material.video_path),
            "category": material.category,
            "difficulty": material.difficulty,
            "duration": material.duration,
            "view_count": material.view_count,
            "favorited_at": favorite.created_at.isoformat() if favorite.created_at else None
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
