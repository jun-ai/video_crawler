"""
公告公开路由（无需认证）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.models import Announcement

router = APIRouter(prefix="/api/announcements", tags=["公告"])


@router.get("")
async def get_announcements(
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """获取公告列表（公开，按优先级+时间排序）"""
    query = (
        select(Announcement)
        .where(Announcement.is_active == True)
        .order_by(Announcement.priority.desc(), Announcement.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    announcements = result.scalars().all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "type": a.type,
            "priority": a.priority,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in announcements
    ]
