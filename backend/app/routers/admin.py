"""
管理后台路由
用于语料管理、批量操作等
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from typing import Annotated, Optional, List
from pathlib import Path
import os

from app.database import get_db
from app.models.models import Material, Subtitle, User, Tag, MaterialTag, ActivationCode, Announcement
from app.schemas.schemas import (
    MaterialResponse,
    MaterialListResponse,
    MessageResponse,
    AnnouncementCreate,
    AnnouncementUpdate
)
from app.config import settings
from app.services.storage import get_storage_service, generate_object_key
from app.services.subtitle_parser import parse_srt_file
from app.routers.auth import get_current_admin
from pydantic import BaseModel
import tempfile

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


# ==================== 语料管理 ====================

@router.get("/materials", response_model=MaterialListResponse)
async def admin_get_materials(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取语料列表（管理后台）"""
    query = select(Material)

    # 筛选条件
    if category:
        query = query.where(Material.category == category)
    if is_active is not None:
        query = query.where(Material.is_active == is_active)
    if keyword:
        query = query.where(Material.title.ilike(f"%{keyword}%"))

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(Material.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    materials = result.scalars().all()

    # 构建响应
    items = []
    for m in materials:
        items.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "video_path": m.video_path,
            "subtitle_path": m.subtitle_path,
            "cover_path": m.cover_path,
            "category": m.category,
            "difficulty": m.difficulty,
            "duration": m.duration,
            "view_count": m.view_count,
            "storage_type": m.storage_type,
            "is_active": m.is_active,
            "created_at": m.created_at
        })

    return MaterialListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/materials/{material_id}/status")
async def toggle_material_status(
    material_id: int,
    is_active: bool = Query(..., description="是否启用"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """启用/禁用语料"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语料不存在"
        )

    material.is_active = is_active
    await db.commit()

    return {"message": "状态已更新", "is_active": is_active}


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    delete_files: bool = Query(False, description="是否同时删除云存储文件"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除语料"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语料不存在"
        )

    # 可选：删除云存储文件
    if delete_files and material.storage_type != 'local':
        storage = get_storage_service()
        try:
            # 从URL中提取object key
            if material.video_path:
                key = material.video_path.split('/')[-1]
                await storage.delete_file(f"videos/{key}")
            if material.cover_path:
                key = material.cover_path.split('/')[-1]
                await storage.delete_file(f"covers/{key}")
        except Exception as e:
            print(f"删除云存储文件失败: {e}")

    # 删除数据库记录（级联删除字幕等）
    await db.delete(material)
    await db.commit()

    return {"message": "语料已删除", "success": True}


# ==================== 批量操作 ====================

@router.post("/materials/batch-upload")
async def batch_upload_materials(
    files: List[UploadFile] = File(...),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    批量上传语料

    文件命名规则：
    - 视频: title.mp4
    - 字幕: title.srt
    - 封面: title.jpg

    会自动按文件名分组
    """
    # 按文件名前缀分组
    file_groups = {}
    for file in files:
        name_without_ext = Path(file.filename).stem
        ext = Path(file.filename).suffix.lower()

        if name_without_ext not in file_groups:
            file_groups[name_without_ext] = {}

        if ext in ['.mp4', '.webm', '.mov']:
            file_groups[name_without_ext]['video'] = file
        elif ext in ['.srt', '.vtt']:
            file_groups[name_without_ext]['subtitle'] = file
        elif ext in ['.jpg', '.jpeg', '.png']:
            file_groups[name_without_ext]['cover'] = file

    storage = get_storage_service()
    results = []
    errors = []
    pending_interp_materials = []

    for title, group in file_groups.items():
        try:
            if 'video' not in group or 'subtitle' not in group:
                errors.append(f"{title}: 缺少必要文件")
                continue

            # 读取文件
            video_data = await group['video'].read()
            subtitle_data = await group['subtitle'].read()
            cover_data = await group.get('cover').read() if group.get('cover') else None

            # 上传文件
            video_key = generate_object_key('video', group['video'].filename)
            subtitle_key = generate_object_key('subtitle', group['subtitle'].filename)

            video_url = await storage.upload_file(video_data, video_key, 'video/mp4')
            subtitle_url = await storage.upload_file(subtitle_data, subtitle_key, 'text/plain')

            cover_url = None
            if cover_data:
                cover_key = generate_object_key('cover', group['cover'].filename)
                cover_url = await storage.upload_file(cover_data, cover_key, 'image/jpeg')

            # 创建语料记录
            material = Material(
                title=title,
                video_path=video_url,
                subtitle_path=subtitle_url,
                cover_path=cover_url or '',
                storage_type=settings.storage_type,
                video_size=len(video_data)
            )

            db.add(material)
            await db.flush()

            # 解析字幕
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.srt', delete=False) as tmp:
                tmp.write(subtitle_data)
                tmp_path = tmp.name

            try:
                subtitles = await parse_srt_file(tmp_path, material.id)
                for sub in subtitles:
                    db.add(Subtitle(**sub.model_dump()))
            finally:
                os.unlink(tmp_path)

            results.append({"title": title, "id": material.id, "status": "success"})
            pending_interp_materials.append(material.id)

        except Exception as e:
            errors.append(f"{title}: {str(e)}")

    await db.commit()

    # 提交后再触发解读生成（避免后台任务读不到未提交的数据）
    for mat_id in pending_interp_materials:
        try:
            from app.services.interpretation_tasks import generate_interpretations_for_material
            asyncio.create_task(generate_interpretations_for_material(mat_id))
        except Exception as e:
            print(f"[WARN] 触发解读生成失败(material_id={mat_id}): {e}")

    return {
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }


# ==================== 统计信息 ====================

@router.get("/stats")
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取管理后台统计数据（并行查询优化）"""
    # 并行执行所有查询
    total_task = db.execute(select(func.count(Material.id)))
    active_task = db.execute(select(func.count(Material.id)).where(Material.is_active == True))
    category_task = db.execute(
        select(Material.category, func.count(Material.id))
        .where(Material.category.isnot(None))
        .group_by(Material.category)
    )
    storage_task = db.execute(
        select(Material.storage_type, func.count(Material.id))
        .group_by(Material.storage_type)
    )
    views_task = db.execute(select(func.sum(Material.view_count)))

    # 等待所有查询完成
    total_materials, active_materials, category_stats, storage_stats, total_views = await asyncio.gather(
        total_task, active_task, category_task, storage_task, views_task
    )

    return {
        "materials": {
            "total": total_materials.scalar() or 0,
            "active": active_materials.scalar() or 0
        },
        "categories": [
            {"name": row[0], "count": row[1]}
            for row in category_stats.all()
        ],
        "storage": {
            row[0]: row[1]
            for row in storage_stats.all()
        },
        "total_views": total_views.scalar() or 0
    }


# ==================== 存储管理 ====================

@router.get("/storage/info")
async def get_storage_info(
    current_admin: User = Depends(get_current_admin)
):
    """获取存储配置信息"""
    return {
        "storage_type": settings.storage_type,
        "is_cloud": settings.storage_type != 'local',
        "cdn_enabled": bool(settings.cdn_domain),
        "config": {
            "endpoint": getattr(settings, 'aliyun_oss_endpoint', None) if settings.storage_type == 'aliyun_oss' else None,
            "bucket": getattr(settings, 'aliyun_oss_bucket_name', None) if settings.storage_type == 'aliyun_oss' else None,
            "region": getattr(settings, 'tencent_cos_region', None) if settings.storage_type == 'tencent_cos' else None,
        }
    }


@router.post("/storage/test")
async def test_storage_connection(
    current_admin: User = Depends(get_current_admin)
):
    """测试存储连接"""
    try:
        storage = get_storage_service()

        # 测试上传
        test_data = b"test connection"
        test_key = "test/connection.txt"

        await storage.upload_file(test_data, test_key, 'text/plain')

        # 测试获取URL
        url = await storage.get_file_url(test_key)

        # 测试删除
        await storage.delete_file(test_key)

        return {
            "success": True,
            "message": "存储连接正常",
            "test_url": url
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"存储连接失败: {str(e)}"
        }


# ==================== 标签管理 ====================

class AssignTagsRequest(BaseModel):
    tag_ids: List[int]


@router.post("/materials/{material_id}/tags", response_model=MessageResponse)
async def assign_tags_to_material(
    material_id: int,
    data: AssignTagsRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """为材料分配标签"""
    # 检查材料存在
    result = await db.execute(select(Material).where(Material.id == material_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="材料不存在")

    # 删除现有关联
    await db.execute(
        delete(MaterialTag).where(MaterialTag.material_id == material_id)
    )

    # 创建新关联
    for tag_id in data.tag_ids:
        mt = MaterialTag(material_id=material_id, tag_id=tag_id)
        db.add(mt)

    await db.commit()
    return MessageResponse(message="标签已更新", success=True)


# ==================== 激活码管理 ====================

class GenerateCodesRequest(BaseModel):
    count: int = 1
    max_uses: int = 1
    expires_days: Optional[int] = None


@router.post("/activation-codes")
async def generate_activation_codes(
    data: GenerateCodesRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量生成激活码"""
    import uuid
    from datetime import datetime, timezone, timedelta

    codes = []
    for _ in range(data.count):
        code_str = uuid.uuid4().hex[:8].upper()
        record = ActivationCode(
            code=code_str,
            max_uses=data.max_uses,
            created_by=current_admin.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=data.expires_days) if data.expires_days else None
        )
        db.add(record)
        codes.append(code_str)

    await db.commit()
    return {"codes": codes, "count": len(codes)}


@router.get("/activation-codes")
async def get_activation_codes(
    page: int = 1,
    page_size: int = 20,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取激活码列表"""
    query = select(ActivationCode).order_by(ActivationCode.created_at.desc())
    count_query = select(func.count()).select_from(ActivationCode)

    total = (await db.execute(count_query)).scalar()
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    codes = result.scalars().all()

    return {
        "items": [
            {
                "id": c.id,
                "code": c.code,
                "is_used": c.use_count >= c.max_uses,
                "used_by": c.used_by,
                "used_at": c.used_at.isoformat() if c.used_at else None,
                "max_uses": c.max_uses,
                "use_count": c.use_count,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in codes
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.delete("/activation-codes/{code_id}")
async def delete_activation_code(
    code_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除激活码"""
    result = await db.execute(select(ActivationCode).where(ActivationCode.id == code_id))
    code = result.scalar_one_or_none()
    if not code:
        raise HTTPException(status_code=404, detail="激活码不存在")

    await db.delete(code)
    await db.commit()
    return MessageResponse(message="激活码已删除", success=True)


# ==================== 公告管理 ====================

@router.post("/announcements")
async def create_announcement(
    data: AnnouncementCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建公告"""
    announcement = Announcement(
        title=data.title,
        content=data.content,
        type=data.type,
        priority=data.priority,
        created_by=current_admin.id
    )
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return {"id": announcement.id, "message": "公告创建成功"}


@router.get("/announcements")
async def get_admin_announcements(
    page: int = 1,
    page_size: int = 20,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取公告列表（管理端）"""
    query = select(Announcement).order_by(Announcement.created_at.desc())
    count_query = select(func.count()).select_from(Announcement)

    total = (await db.execute(count_query)).scalar()
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    announcements = result.scalars().all()

    return {
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "type": a.type,
                "priority": a.priority,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in announcements
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新公告"""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    if data.title is not None:
        announcement.title = data.title
    if data.content is not None:
        announcement.content = data.content
    if data.type is not None:
        announcement.type = data.type
    if data.priority is not None:
        announcement.priority = data.priority
    if data.is_active is not None:
        announcement.is_active = data.is_active

    await db.commit()
    return MessageResponse(message="公告已更新", success=True)


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除公告"""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    await db.delete(announcement)
    await db.commit()
    return MessageResponse(message="公告已删除", success=True)
