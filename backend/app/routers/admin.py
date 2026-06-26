"""
管理后台路由
用于语料管理、批量操作等
"""
import asyncio
import uuid
import re
from typing import Annotated, Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from pathlib import Path
import os

from app.database import get_db
from app.models.models import Material, Subtitle, User, Tag, MaterialTag, ActivationCode, Announcement
from app.schemas.schemas import (
    MaterialResponse,
    MaterialListResponse,
    MaterialUpdate,
    MessageResponse,
    AnnouncementCreate,
    AnnouncementUpdate
)
from app.config import settings
from app.services.storage import get_storage_service, generate_object_key
from app.services.subtitle_parser import parse_srt_file, parse_srt
from app.routers.auth import get_current_admin
from pydantic import BaseModel
import tempfile
import subprocess


def _ffprobe_duration(video_path: str, timeout: int = 30) -> float:
    """用 ffprobe 取视频时长（秒），失败返 0.0"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return float(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired, FileNotFoundError):
        return 0.0


# Pydantic body schema: probe-duration 用
class ProbeDurationRequest(BaseModel):
    video_path: str  # OSS object key, e.g. "videos/2026/06/abc.mp4"

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


# ==================== URL 抓取任务存储(内存) ====================

class FetchTask(BaseModel):
    task_id: str
    url: str
    platform: str
    status: str = "pending"  # pending / fetching / parsing / done / failed
    progress: int = 0
    message: str = ""
    material_id: Optional[int] = None
    error: str = ""
    created_at: str = ""
    finished_at: str = ""

# 进程内任务表(单实例足够)
_FETCH_TASKS: Dict[str, FetchTask] = {}


# ==================== URL 抓取语料 ====================

class FetchURLRequest(BaseModel):
    url: str
    category: Optional[str] = None
    difficulty: Optional[int] = None
    subtitle_langs: Optional[List[str]] = None


@router.get("/ai-providers")
async def get_ai_providers_status(
    current_admin: User = Depends(get_current_admin),
):
    """查看 AI provider 状态(用于诊断熔断 / 配置)"""
    from app.services.deepseek import get_ai_providers_status
    return get_ai_providers_status()


@router.post("/materials/fetch-url")
async def fetch_material_from_url(
    req: FetchURLRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    通过视频URL自动抓取语料(YouTube/B站)
    后台异步执行,返回 task_id 用于轮询进度
    """
    from datetime import datetime
    from app.services.video_fetcher import detect_platform, fetch_from_url

    platform = detect_platform(req.url)
    if platform == "unknown":
        raise HTTPException(
            status_code=400,
            detail="不支持的URL,目前支持 YouTube / Bilibili"
        )

    task_id = uuid.uuid4().hex[:16]
    task = FetchTask(
        task_id=task_id,
        url=req.url,
        platform=platform,
        status="pending",
        message=f"已加入队列,等待执行...",
        created_at=datetime.now().isoformat(),
    )
    _FETCH_TASKS[task_id] = task

    async def _do_fetch():
        from app.services.interpretation_tasks import generate_interpretations_for_material
        from app.services.subtitle_parser import parse_srt_file, parse_srt

        try:
            task.status = "fetching"
            task.message = "正在下载视频、字幕、封面..."
            task.progress = 10

            # 存储目录 - 用配置里的 upload_dir
            output_dir = os.path.join(
                os.path.dirname(settings.upload_dir.rstrip("/")),
                "fetched"
            ) if settings.storage_type == "local" else "/tmp/fetched"
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)

            fetch_result = await fetch_from_url(
                req.url,
                output_dir=output_dir,
                prefer_subtitle_langs=req.subtitle_langs,
            )

            if not fetch_result.success:
                task.status = "failed"
                task.error = fetch_result.error
                task.finished_at = datetime.now().isoformat()
                return

            task.status = "parsing"
            task.message = f"已下载 {fetch_result.file_size//1024}KB,正在解析字幕..."
            task.progress = 60

            # 复制到正式存储目录
            storage = get_storage_service()
            final_video_path = ""
            final_subtitle_path = ""
            final_cover_path = ""

            if fetch_result.video_path and os.path.exists(fetch_result.video_path):
                with open(fetch_result.video_path, "rb") as f:
                    data = f.read()
                key = generate_object_key("video", os.path.basename(fetch_result.video_path))
                final_video_path = await storage.upload_file(data, key, "video/mp4")

            if fetch_result.subtitle_path and os.path.exists(fetch_result.subtitle_path):
                with open(fetch_result.subtitle_path, "rb") as f:
                    data = f.read()
                key = generate_object_key("subtitle", os.path.basename(fetch_result.subtitle_path))
                final_subtitle_path = await storage.upload_file(data, key, "text/plain")

            if fetch_result.cover_path and os.path.exists(fetch_result.cover_path):
                with open(fetch_result.cover_path, "rb") as f:
                    data = f.read()
                key = generate_object_key("cover", os.path.basename(fetch_result.cover_path))
                final_cover_path = await storage.upload_file(data, key, "image/jpeg")

            # 创建 Material 记录
            material = Material(
                title=fetch_result.title[:200],
                description=fetch_result.description[:1000] if fetch_result.description else None,
                video_path=final_video_path or fetch_result.video_url,
                subtitle_path=final_subtitle_path,
                cover_path=final_cover_path,
                storage_type=settings.storage_type,
                video_size=fetch_result.file_size,
                category=req.category,
                difficulty=req.difficulty or 2,
                duration=fetch_result.duration,
                interpretation_status="pending",
            )
            db.add(material)
            await db.flush()

            # 解析字幕
            subtitle_count = 0
            if fetch_result.subtitle_path and os.path.exists(fetch_result.subtitle_path):
                try:
                    subtitles = await parse_srt_file(fetch_result.subtitle_path, material.id)
                    for sub in subtitles:
                        db.add(Subtitle(**sub.model_dump()))
                        subtitle_count += 1
                except Exception as e:
                    print(f"[FetchURL] 字幕解析失败: {e}")

            await db.commit()
            await db.refresh(material)

            # 清理临时下载文件
            for fp in [fetch_result.video_path, fetch_result.subtitle_path, fetch_result.cover_path]:
                try:
                    if fp and os.path.exists(fp):
                        os.unlink(fp)
                except Exception:
                    pass

            task.material_id = material.id
            task.progress = 80
            task.message = f"已创建语料(id={material.id}, 字幕{subtitle_count}条),正在生成AI解读..."

            # 触发 AI 解读后台任务
            try:
                asyncio.create_task(generate_interpretations_for_material(material.id))
            except Exception as e:
                print(f"[FetchURL] 触发解读失败: {e}")

            task.status = "done"
            task.progress = 100
            task.message = f"完成!语料ID={material.id},字幕{subtitle_count}条"
            task.finished_at = datetime.now().isoformat()

        except Exception as e:
            import traceback
            traceback.print_exc()
            task.status = "failed"
            task.error = f"{type(e).__name__}: {str(e)[:300]}"
            task.finished_at = datetime.now().isoformat()

    asyncio.create_task(_do_fetch())

    return {"task_id": task_id, "status": "pending", "message": "抓取任务已启动"}


@router.get("/materials/fetch-status/{task_id}")
async def get_fetch_status(
    task_id: str,
    current_admin: User = Depends(get_current_admin)
):
    """轮询抓取任务状态"""
    task = _FETCH_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return task.model_dump()


@router.get("/materials/fetch-tasks")
async def list_fetch_tasks(
    current_admin: User = Depends(get_current_admin)
):
    """列出最近的抓取任务(最多 20 条)"""
    tasks = sorted(_FETCH_TASKS.values(), key=lambda t: t.created_at, reverse=True)[:20]
    return [t.model_dump() for t in tasks]


# ==================== 视频转字幕（faster-whisper） ====================

class TranscribeTask(BaseModel):
    task_id: str
    filename: str
    model_size: str = "base"
    language: Optional[str] = None
    status: str = "pending"  # pending / extracting / transcribing / done / failed
    progress: int = 0
    message: str = ""
    srt: Optional[str] = None
    language_detected: Optional[str] = None
    duration: Optional[float] = None
    segment_count: Optional[int] = None
    error: str = ""
    created_at: str = ""
    finished_at: str = ""


_TRANSCRIBE_TASKS: Dict[str, TranscribeTask] = {}

# 上传目录
_TRANSCRIBE_UPLOAD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(settings.upload_dir.rstrip("/")), "transcribe_tmp")
)
os.makedirs(_TRANSCRIBE_UPLOAD_DIR, exist_ok=True)

ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".flv", ".m4v"}
MAX_VIDEO_SIZE_MB = 500  # 超过 500MB 拒绝


@router.post("/transcribe")
async def transcribe_video(
    file: UploadFile = File(...),
    model_size: str = Form("base"),
    language: Optional[str] = Form(None),
    current_admin: User = Depends(get_current_admin),
):
    """
    上传视频文件 → 后台 faster-whisper 转录 → 返回 task_id 轮询

    表单字段:
      file: 视频文件 (mp4/mov/mkv/webm/avi/flv/m4v)
      model_size: tiny / base / small（默认 base）
      language: 强制语言 (en/zh)，留空自动检测
    """
    # 1) 校验扩展名
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_VIDEO_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的视频格式: {ext}，仅支持 {', '.join(sorted(ALLOWED_VIDEO_EXTS))}",
        )

    # 2) 校验大小（看 Content-Length）
    if file.size and file.size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"视频过大（{file.size // 1024 // 1024}MB），上限 {MAX_VIDEO_SIZE_MB}MB",
        )

    # 3) 校验 model_size
    if model_size not in ("tiny", "base", "small"):
        raise HTTPException(status_code=400, detail="model_size 必须为 tiny/base/small")

    # 4) 保存到磁盘
    task_id = uuid.uuid4().hex[:16]
    safe_name = re.sub(r"[^\w.\-]", "_", file.filename or f"video_{task_id}{ext}")
    save_path = os.path.join(_TRANSCRIBE_UPLOAD_DIR, f"{task_id}_{safe_name}")

    try:
        with open(save_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        if os.path.exists(save_path):
            os.unlink(save_path)
        raise HTTPException(status_code=500, detail=f"上传失败: {e}")

    actual_size = os.path.getsize(save_path)
    if actual_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        os.unlink(save_path)
        raise HTTPException(
            status_code=400,
            detail=f"视频过大（{actual_size // 1024 // 1024}MB），上限 {MAX_VIDEO_SIZE_MB}MB",
        )

    # 5) 创建任务
    task = TranscribeTask(
        task_id=task_id,
        filename=file.filename or safe_name,
        model_size=model_size,
        language=language or None,
        message="已加入队列...",
        created_at=datetime.now().isoformat(),
    )
    _TRANSCRIBE_TASKS[task_id] = task

    # 6) 后台执行
    async def _do_transcribe():
        try:
            from app.services.video_transcriber import transcribe_video, is_faster_whisper_available

            if not is_faster_whisper_available():
                raise RuntimeError("faster-whisper 未安装，请联系运维")

            task.status = "transcribing"

            def _on_progress(pct: int, msg: str):
                task.progress = pct
                task.message = msg

            result = await transcribe_video(
                video_path=save_path,
                model_size=task.model_size,
                language=task.language,
                progress_callback=_on_progress,
            )

            if not result.get("success"):
                task.status = "failed"
                task.error = result.get("error", "未知错误")[:500]
                task.finished_at = datetime.now().isoformat()
                return

            task.status = "done"
            task.progress = 100
            task.message = f"完成！共 {result['segment_count']} 条字幕"
            task.srt = result["srt"]
            task.language_detected = result["language"]
            task.duration = result["duration"]
            task.segment_count = result["segment_count"]
            task.finished_at = datetime.now().isoformat()

        except Exception as e:
            import traceback
            traceback.print_exc()
            task.status = "failed"
            task.error = f"{type(e).__name__}: {str(e)[:300]}"
            task.finished_at = datetime.now().isoformat()
        finally:
            # 清理临时文件
            try:
                if os.path.exists(save_path):
                    os.unlink(save_path)
            except Exception:
                pass

    asyncio.create_task(_do_transcribe())

    return {
        "task_id": task_id,
        "status": "pending",
        "filename": file.filename,
        "model_size": model_size,
        "message": "转录任务已启动",
    }


@router.get("/transcribe-status/{task_id}")
async def get_transcribe_status(
    task_id: str,
    current_admin: User = Depends(get_current_admin),
):
    """轮询转录任务状态"""
    task = _TRANSCRIBE_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return task.model_dump()


@router.get("/transcribe-tasks")
async def list_transcribe_tasks(
    current_admin: User = Depends(get_current_admin),
):
    """列出最近的转录任务（最多 20 条）"""
    tasks = sorted(_TRANSCRIBE_TASKS.values(), key=lambda t: t.created_at, reverse=True)[:20]
    return [t.model_dump() for t in tasks]


@router.delete("/transcribe/{task_id}")
async def delete_transcribe_task(
    task_id: str,
    current_admin: User = Depends(get_current_admin),
):
    """清理转录任务记录（不影响已下载的 SRT）"""
    if task_id not in _TRANSCRIBE_TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    del _TRANSCRIBE_TASKS[task_id]
    return {"message": "已清理"}


# ==================== 语料管理 ====================

@router.get("/materials", response_model=MaterialListResponse)
async def admin_get_materials(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
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
    # 时长筛选 (秒)。max_duration=None 表示无上限 (用于 "长视频 >600s" 档)。
    if min_duration is not None:
        query = query.where(Material.duration >= min_duration)
    if max_duration is not None:
        query = query.where(Material.duration <= max_duration)

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


# ==================== 编辑语料 ====================

@router.put("/materials/{material_id}")
async def update_material(
    material_id: int,
    payload: MaterialUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """编辑语料信息（仅更新 payload 中提供的字段）"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="语料不存在")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的字段")

    # title 截断防超长
    if "title" in update_data and update_data["title"]:
        update_data["title"] = update_data["title"][:200]
    if "description" in update_data and update_data["description"]:
        update_data["description"] = update_data["description"][:1000]

    # difficulty 范围保护
    if "difficulty" in update_data and update_data["difficulty"] is not None:
        d = update_data["difficulty"]
        if d < 1 or d > 5:
            raise HTTPException(status_code=400, detail="difficulty 必须在 1-5 之间")
        update_data["difficulty"] = d

    for field, value in update_data.items():
        setattr(material, field, value)

    await db.commit()
    await db.refresh(material)

    return {
        "message": "已更新",
        "success": True,
        "material": {
            "id": material.id,
            "title": material.title,
            "description": material.description,
            "category": material.category,
            "difficulty": material.difficulty,
            "duration": material.duration,
            "is_active": material.is_active,
        }
    }


# ==================== 批量删除 / 批量状态 ====================

@router.post("/materials/batch-delete")
async def batch_delete_materials(
    payload: Dict[str, List[int]],
    delete_files: bool = Query(False, description="是否同时删除 OSS 文件"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量删除语料。payload: {"ids": [1,2,3]}"""
    ids = payload.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="ids 不能为空")

    result = await db.execute(select(Material).where(Material.id.in_(ids)))
    materials = result.scalars().all()

    deleted = 0
    if delete_files:
        storage = get_storage_service()
        for m in materials:
            if m.storage_type != 'local':
                try:
                    for path_field in [m.video_path, m.subtitle_path, m.cover_path]:
                        if not path_field:
                            continue
                        # path 可能是 object key 或带 bucket 的 url — 取最后一段当 key 不够准
                        # 实际生产用 url 中 / 后的路径; 这里保守: 只删带 videos/ subtitles/ covers 前缀的 key
                        for prefix in ["videos/", "subtitles/", "covers/"]:
                            if prefix in path_field:
                                key = path_field[path_field.index(prefix):]
                                await storage.delete_file(key)
                                break
                except Exception as e:
                    print(f"[BatchDelete] 删除 OSS 文件失败 (id={m.id}): {e}")

    for m in materials:
        await db.delete(m)
        deleted += 1

    await db.commit()

    skipped = len(ids) - deleted
    msg = f"已删除 {deleted} 个语料"
    if skipped:
        msg += f" (跳过 {skipped} 个: 不存在)"

    return {"message": msg, "success": True, "deleted": deleted}


@router.post("/materials/batch-status")
async def batch_update_status(
    payload: Dict[str, Any],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量发布/取消发布。payload: {"ids": [1,2,3], "is_active": true}"""
    ids = payload.get("ids", [])
    is_active = payload.get("is_active")
    if not ids:
        raise HTTPException(status_code=400, detail="ids 不能为空")
    if is_active is None:
        raise HTTPException(status_code=400, detail="is_active 必填")

    result = await db.execute(select(Material).where(Material.id.in_(ids)))
    materials = result.scalars().all()

    updated = 0
    for m in materials:
        m.is_active = bool(is_active)
        updated += 1
    await db.commit()

    skipped = len(ids) - updated
    action = "发布" if is_active else "取消发布"
    msg = f"已{action} {updated} 个语料"
    if skipped:
        msg += f" (跳过 {skipped} 个: 不存在)"

    return {"message": msg, "success": True, "updated": updated}


# ==================== 重新生成字幕 / 重新解读 ====================

@router.post("/materials/{material_id}/retranscribe")
async def retranscribe_material(
    material_id: int,
    model_size: str = Query("base", description="tiny / base / small"),
    language: Optional[str] = Query(None, description="强制语言, 留空自动检测"),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """从 OSS 下载视频 → faster-whisper 转录 → 上传新 SRT 到 OSS → 替换 subtitle_path → 重新解析字幕
    返回 task_id (后台运行, 前端轮询 status)"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="语料不存在")
    if not material.video_path:
        raise HTTPException(status_code=400, detail="语料没有视频文件")

    task_id = uuid.uuid4().hex[:16]
    _TRANSCRIBE_TASKS[task_id] = TranscribeTask(
        task_id=task_id,
        filename=f"material_{material_id}_retranscribe",
        model_size=model_size,
        language=language,
        status="pending",
        message="已加入队列,等待执行...",
        created_at=datetime.now().isoformat(),
    )

    async def _do_retranscribe():
        from app.services.video_transcriber import _transcribe_sync
        tmpdir = tempfile.mkdtemp(prefix="retrans_")
        local_video = os.path.join(tmpdir, "video.mp4")
        local_srt = os.path.join(tmpdir, "subtitles.srt")
        try:
            t = _TRANSCRIBE_TASKS[task_id]
            t.status = "extracting"
            t.message = "下载视频从 OSS..."

            # 从 OSS 拉视频到本地
            storage = get_storage_service()
            # 找到 object key: video_path 一般是 object key 或 url
            # storage.download_file 接受 object key; 假设路径就是 key
            video_key = material.video_path
            for prefix in ["videos/", "subtitles/", "covers/"]:
                if prefix in video_key and not video_key.startswith(prefix):
                    video_key = video_key[video_key.index(prefix):]
            await storage.download_file(video_key, local_video)

            t.status = "transcribing"
            t.message = "faster-whisper 转录中..."

            # 同步转录包成异步 (run in thread pool)
            loop = asyncio.get_event_loop()
            result_data = await loop.run_in_executor(
                None, _transcribe_sync, local_video, model_size, language,
                lambda pct, msg: setattr(t, 'progress', pct) or setattr(t, 'message', msg)
            )

            if not result_data.get("success"):
                raise RuntimeError(result_data.get("error", "转录失败"))

            srt_text = result_data["srt"]
            with open(local_srt, "w", encoding="utf-8") as f:
                f.write(srt_text)

            t.message = f"已转录 {result_data.get('segment_count', 0)} 条, 上传 OSS..."

            # 上传新 SRT 到 OSS
            srt_key = generate_object_key("subtitle", f"{material_id}_retrans.srt")
            new_subtitle_path = await storage.upload_file(
                srt_text.encode("utf-8"), srt_key, "text/plain"
            )

            # 更新 DB
            material.subtitle_path = new_subtitle_path
            material.duration = int(result_data.get("duration", 0))

            # 删除旧字幕 + 写入新字幕
            from sqlalchemy import delete as sql_delete
            await db.execute(sql_delete(Subtitle).where(Subtitle.material_id == material_id))

            subtitles = parse_srt(srt_text, material_id)
            for sub in subtitles:
                db.add(Subtitle(**sub.model_dump()))

            await db.commit()

            t.status = "done"
            t.progress = 100
            t.message = f"完成!字幕 {len(subtitles)} 条, 语言={result_data.get('language')}"
            t.srt = srt_text
            t.language_detected = result_data.get("language")
            t.duration = result_data.get("duration")
            t.segment_count = result_data.get("segment_count")
            t.finished_at = datetime.now().isoformat()
        except Exception as e:
            t.status = "failed"
            t.error = f"{type(e).__name__}: {str(e)[:300]}"
            t.message = "转录失败"
            t.finished_at = datetime.now().isoformat()
            import traceback
            traceback.print_exc()
        finally:
            try:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass

    asyncio.create_task(_do_retranscribe())

    return {"task_id": task_id, "status": "pending", "message": "重新转录已启动"}


@router.post("/materials/{material_id}/reinterpret")
async def reinterpret_material(
    material_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """重新生成 AI 解读 (单词/短语/语法/地道表达)
    会清空旧的 VideoInterpretation, 触发后台任务"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="语料不存在")

    # 清空旧解读
    from app.models.models import VideoInterpretation
    from sqlalchemy import delete as sql_delete
    await db.execute(
        sql_delete(VideoInterpretation).where(VideoInterpretation.material_id == material_id)
    )

    # 重置状态 + commit 让后台任务能看到 pending
    material.interpretation_status = "pending"
    await db.commit()
    await db.refresh(material)

    # 触发后台任务
    try:
        from app.services.interpretation_tasks import generate_interpretations_for_material
        asyncio.create_task(generate_interpretations_for_material(material_id))
    except Exception as e:
        print(f"[Reinterpret] 触发失败: {e}")
        return {"message": "触发失败", "success": False, "error": str(e)}

    return {"message": "已重新触发 AI 解读", "success": True, "material_id": material_id}


# ==================== CSV 导出 ====================

@router.get("/materials/export")
async def export_materials_csv(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """导出语料列表为 CSV (UTF-8 BOM, Excel 友好)"""
    import csv
    import io

    query = select(Material)
    if category:
        query = query.where(Material.category == category)
    if is_active is not None:
        query = query.where(Material.is_active == is_active)
    if keyword:
        query = query.where(Material.title.ilike(f"%{keyword}%"))
    query = query.order_by(Material.created_at.desc())

    result = await db.execute(query)
    materials = result.scalars().all()

    buf = io.StringIO()
    buf.write("\ufeff")  # BOM 让 Excel 不乱码
    writer = csv.writer(buf)
    writer.writerow([
        "id", "title", "category", "difficulty", "duration",
        "view_count", "is_active", "storage_type",
        "video_path", "subtitle_path", "cover_path",
        "interpretation_status", "created_at"
    ])
    for m in materials:
        writer.writerow([
            m.id, m.title, m.category or "", m.difficulty, m.duration or "",
            m.view_count, "true" if m.is_active else "false",
            m.storage_type, m.video_path or "",
            m.subtitle_path or "", m.cover_path or "",
            m.interpretation_status or "", m.created_at.isoformat() if m.created_at else ""
        ])

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=materials-{timestamp}.csv"
        }
    )


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


# ==================== 视频时长探测 (ffprobe) ====================

@router.post("/materials/probe-duration")
async def probe_material_duration(
    req: ProbeDurationRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    给定 video_path (OSS object key)，从 OSS 下载到本地，ffprobe 取时长（秒）。
    不入库 — 调用方拿 duration 后自行决定是否写入。

    用法：
    1. 编辑语料: 前端拿 material.video_path → probe → 填到 input
    2. 上传新视频: presign upload 完拿 object_key → probe → 填到 form
    """
    storage = get_storage_service()
    if not await storage.file_exists(req.video_path):
        raise HTTPException(status_code=404, detail=f"视频文件不存在: {req.video_path}")

    # 下载到临时文件
    tmpdir = tempfile.mkdtemp(prefix="probe_")
    tmp_path = os.path.join(tmpdir, os.path.basename(req.video_path))
    try:
        ok = await storage.download_file(req.video_path, tmp_path)
        if not ok:
            raise HTTPException(status_code=500, detail="下载视频失败")
        duration = _ffprobe_duration(tmp_path)
        if duration <= 0:
            raise HTTPException(status_code=422, detail="ffprobe 未能提取时长（视频可能损坏）")
        # Material.duration 是 Integer, 取整秒
        duration_int = int(round(duration))
        return {"video_path": req.video_path, "duration": duration_int, "duration_raw": round(duration, 2)}
    finally:
        # 清理临时文件
        try:
            os.remove(tmp_path)
            os.rmdir(tmpdir)
        except OSError:
            pass


@router.post("/materials/backfill-durations")
async def backfill_durations(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    批量: 遍历所有 duration IS NULL 的语料, 从 OSS 下载 + ffprobe + UPDATE 库。
    Idempotent — 已填的跳过, 没视频文件的跳过。
    """
    result = await db.execute(
        select(Material).where(Material.duration.is_(None)).order_by(Material.id)
    )
    materials = result.scalars().all()
    storage = get_storage_service()
    updated = []
    skipped = []
    failed = []
    for m in materials:
        if not m.video_path:
            skipped.append({"id": m.id, "reason": "video_path is null"})
            continue
        if not await storage.file_exists(m.video_path):
            skipped.append({"id": m.id, "reason": f"OSS file not found: {m.video_path}"})
            continue
        tmpdir = tempfile.mkdtemp(prefix="bf_")
        tmp_path = os.path.join(tmpdir, os.path.basename(m.video_path))
        try:
            ok = await storage.download_file(m.video_path, tmp_path)
            if not ok:
                failed.append({"id": m.id, "reason": "download failed"})
                continue
            duration = _ffprobe_duration(tmp_path)
            if duration <= 0:
                failed.append({"id": m.id, "reason": "ffprobe returned 0"})
                continue
            m.duration = int(round(duration))
            updated.append({"id": m.id, "duration": int(round(duration))})
        finally:
            try:
                os.remove(tmp_path)
                os.rmdir(tmpdir)
            except OSError:
                pass
    await db.commit()
    return {
        "total_null_before": len(materials),
        "updated_count": len(updated),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
    }
