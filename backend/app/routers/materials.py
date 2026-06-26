"""
语料管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Annotated, Optional, List
import asyncio
import os
import shutil
from pathlib import Path
import time

from app.database import get_db
from app.utils.rate_limit import limiter
from app.models.models import Material, Subtitle, VideoInterpretation, InterpretationLearning, User, Tag, MaterialTag
from app.schemas.schemas import (
    MaterialResponse,
    MaterialListResponse,
    SubtitleResponse,
    CategoryResponse,
    MessageResponse,
    InterpretationResponse,
    InterpretationListResponse,
    InterpretationStatusResponse,
    TagResponse,
    PresignUploadRequest,
    PresignUploadResponse,
    PresignedFileInfo,
    FinalizeUploadRequest,
)
from app.config import settings
from app.services.subtitle_parser import parse_srt_file
from app.services.storage import get_storage_service, generate_object_key
from app.services.deepseek import translate_subtitles, translate_text
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/api/materials", tags=["语料管理"])

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def is_cloud_url(path: str) -> bool:
    """判断是否为云存储URL"""
    return path.startswith('http://') or path.startswith('https://')


def is_oss_object_key(path: str) -> bool:
    """判断是否为OSS对象键（不是完整URL，且看起来像对象键）"""
    # 对象键格式如: videos/2026/03/xxx.mp4
    if is_cloud_url(path):
        return False
    # 如果包含 / 且不包含 :// 则可能是对象键
    return '/' in path and '://' not in path


def _get_video_base_url() -> str:
    """获取视频流基础URL，优先使用配置值"""
    if settings.video_base_url:
        return settings.video_base_url.rstrip('/')
    # 本地开发环境回退
    return "http://127.0.0.1:8000"


def get_file_url(file_path: str | None, add_cache_buster: bool = False, use_video_stream: bool = False) -> str:
    """
    获取文件访问 URL（同步版本，用于本地文件）
    - 云存储URL直接返回
    - 本地路径转换为静态文件URL
    - OSS对象键需要使用 get_file_url_async
    """
    if file_path is None:
        return ""

    # 如果已经是完整的HTTP URL（云存储），直接返回
    if is_cloud_url(file_path):
        return file_path

    # 本地文件处理
    path = Path(file_path)
    try:
        # 尝试获取相对路径
        rel_path = path.relative_to(PROJECT_ROOT)
        rel_path_str = rel_path.as_posix()
    except ValueError:
        # 如果不是相对路径，直接返回
        rel_path_str = file_path

    # 视频文件使用专门的视频流端点（支持 Range 请求）
    if use_video_stream:
        url = f"{_get_video_base_url()}/video/{rel_path_str}"
    else:
        url = f"/static/{rel_path_str}"

    # 为视频文件添加缓存破坏参数
    if add_cache_buster and path.exists():
        mtime = int(path.stat().st_mtime)
        url = f"{url}?t={mtime}"

    return url


async def get_file_url_async(file_path: str | None, add_cache_buster: bool = False) -> str:
    """
    获取文件访问 URL（异步版本，支持OSS对象键）
    - 云存储URL直接返回
    - OSS对象键动态生成签名URL
    - 本地路径转换为静态文件URL
    """
    if file_path is None:
        return ""

    from urllib.parse import urlparse, unquote

    # 如果已经是完整的HTTP URL（云存储），需要检查是否过期
    if is_cloud_url(file_path):
        # 检查是否是阿里云OSS的签名URL
        if 'aliyuncs.com' in file_path and settings.storage_type == 'aliyun_oss':
            # 从URL中提取对象键
            try:
                parsed = urlparse(file_path)
                # 提取路径部分，循环解码直到不再变化
                object_key = parsed.path.lstrip('/')
                while True:
                    decoded = unquote(object_key)
                    if decoded == object_key:
                        break
                    object_key = decoded
                # 生成新的签名URL（有效期7天）
                from app.services.storage import get_storage_service
                storage = get_storage_service()
                return await storage.get_file_url(object_key, expires=604800)
            except Exception as e:
                print(f"解析OSS URL失败: {e}")
                return file_path
        # 其他云存储URL直接返回
        return file_path

    # 检查是否是OSS对象键且使用OSS存储
    if settings.storage_type == 'aliyun_oss' and is_oss_object_key(file_path):
        from app.services.storage import get_storage_service
        # 循环解码直到不再变化
        object_key = file_path
        while True:
            decoded = unquote(object_key)
            if decoded == object_key:
                break
            object_key = decoded
        storage = get_storage_service()
        # 动态生成新的签名URL（有效期7天）
        return await storage.get_file_url(object_key, expires=604800)

    # 本地文件处理
    return get_file_url(file_path, add_cache_buster=add_cache_buster)


async def _load_material_tags(material_id: int, db: AsyncSession) -> List[TagResponse]:
    """加载材料的标签列表"""
    result = await db.execute(
        select(Tag)
        .join(MaterialTag, MaterialTag.tag_id == Tag.id)
        .where(MaterialTag.material_id == material_id)
        .order_by(Tag.display_order, Tag.name)
    )
    tags = result.scalars().all()
    return [TagResponse(id=t.id, name=t.name, type=t.type, color=t.color, display_order=t.display_order) for t in tags]


@router.get("", response_model=MaterialListResponse)
async def get_materials(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    keyword: Optional[str] = None,
    tag_id: Optional[int] = None,
    duration_range: Optional[str] = None,  # 视频库前台筛选: 'short' (< 3 分钟) / 'medium' (3-10 分钟) / 'long' (> 10 分钟)
    db: AsyncSession = Depends(get_db)
):
    """获取语料列表（支持分页和筛选）"""
    query = select(Material).where(Material.is_active == True)

    # 筛选条件
    if category:
        query = query.where(Material.category == category)
    if difficulty:
        query = query.where(Material.difficulty == difficulty)
    if keyword:
        query = query.where(Material.title.ilike(f"%{keyword}%"))
    if tag_id:
        # 通过 material_tags 关联表筛选
        query = query.where(
            Material.id.in_(
                select(MaterialTag.material_id).where(MaterialTag.tag_id == tag_id)
            )
        )
    # 时长筛选 (前台"视频库" duration_range)
    # 注: Material.duration 是 Integer (秒), NULL 不参与比较自动排除
    if duration_range == 'short':    # < 3 分钟
        query = query.where(Material.duration < 180)
    elif duration_range == 'medium':  # 3-10 分钟
        query = query.where(Material.duration >= 180, Material.duration <= 600)
    elif duration_range == 'long':    # > 10 分钟
        query = query.where(Material.duration > 600)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(Material.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    materials = result.scalars().all()

    # 转换响应
    items = []
    for m in materials:
        tags = await _load_material_tags(m.id, db)
        item = MaterialResponse(
            id=m.id,
            title=m.title,
            description=m.description,
            video_path=await get_file_url_async(m.video_path, add_cache_buster=True),
            subtitle_path=await get_file_url_async(m.subtitle_path),
            cover_path=await get_file_url_async(m.cover_path),
            category=m.category,
            difficulty=m.difficulty,
            duration=m.duration,
            view_count=m.view_count,
            interpretation_status=m.interpretation_status or 'pending',
            tags=tags,
            created_at=m.created_at
        )
        items.append(item)

    return MaterialListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取场景分类列表"""
    query = select(
        Material.category,
        func.count(Material.id).label("count")
    ).where(
        Material.is_active == True,
        Material.category.isnot(None)
    ).group_by(Material.category)

    result = await db.execute(query)
    rows = result.all()

    return [CategoryResponse(name=row[0], count=row[1]) for row in rows]


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个语料详情"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语料不存在"
        )

    # 增加浏览次数
    material.view_count += 1
    await db.commit()

    return MaterialResponse(
        id=material.id,
        title=material.title,
        description=material.description,
        video_path=await get_file_url_async(material.video_path, add_cache_buster=True),
        subtitle_path=await get_file_url_async(material.subtitle_path),
        cover_path=await get_file_url_async(material.cover_path),
        category=material.category,
        difficulty=material.difficulty,
        duration=material.duration,
        view_count=material.view_count,
        interpretation_status=material.interpretation_status or 'pending',
        tags=await _load_material_tags(material.id, db),
        created_at=material.created_at
    )


@router.get("/{material_id}/subtitles", response_model=List[SubtitleResponse])
async def get_subtitles(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取语料的字幕列表"""
    result = await db.execute(
        select(Subtitle)
        .where(Subtitle.material_id == material_id)
        .order_by(Subtitle.sequence)
    )
    subtitles = result.scalars().all()

    return subtitles


@router.get("/{material_id}/interpretation", response_model=InterpretationListResponse)
async def get_interpretation(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取视频解读内容（单词、短语、语法）"""
    result = await db.execute(
        select(VideoInterpretation)
        .where(VideoInterpretation.material_id == material_id)
        .order_by(VideoInterpretation.category, VideoInterpretation.sequence)
    )
    interpretations = result.scalars().all()

    # 按类别分组
    words = []
    phrases = []
    grammar = []
    idioms = []

    for item in interpretations:
        if item.category == 'word':
            words.append(InterpretationResponse.model_validate(item))
        elif item.category == 'phrase':
            phrases.append(InterpretationResponse.model_validate(item))
        elif item.category == 'grammar':
            grammar.append(InterpretationResponse.model_validate(item))
        elif item.category == 'idiom':
            idioms.append(InterpretationResponse.model_validate(item))

    return InterpretationListResponse(
        words=words,
        phrases=phrases,
        grammar=grammar,
        idioms=idioms
    )


@router.get("/{material_id}/interpretation/status", response_model=InterpretationStatusResponse)
async def get_interpretation_status(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取解读生成状态"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="语料不存在")

    # 统计已生成的卡片数
    count_result = await db.execute(
        select(VideoInterpretation.category, func.count(VideoInterpretation.id))
        .where(VideoInterpretation.material_id == material_id)
        .group_by(VideoInterpretation.category)
    )
    counts = {row[0]: row[1] for row in count_result.fetchall()}

    return InterpretationStatusResponse(
        material_id=material_id,
        status=material.interpretation_status or 'pending',
        words_count=counts.get('word', 0),
        phrases_count=counts.get('phrase', 0),
        grammar_count=counts.get('grammar', 0),
        idioms_count=counts.get('idiom', 0)
    )


@router.post("/{material_id}/interpretation/generate")
@limiter.limit("3/minute")
async def generate_interpretation_endpoint(
    request: Request,
    material_id: int,
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """触发后台生成视频解读内容（立即返回，后台执行）。force=true 可强制重新生成。"""
    from app.services.interpretation_tasks import generate_interpretations_for_material

    # 检查视频是否存在
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="语料不存在")

    if material.interpretation_status == 'generating':
        return {"message": "正在生成中", "status": "generating", "material_id": material_id}

    # 已有解读数据 → 直接返回，不重复调 LLM（force=true 除外）
    if material.interpretation_status == 'done' and not force:
        return {"message": "解读已生成", "status": "done", "material_id": material_id}

    # 检查字幕
    result = await db.execute(
        select(func.count(Subtitle.id)).where(Subtitle.material_id == material_id)
    )
    if (result.scalar() or 0) == 0:
        raise HTTPException(status_code=400, detail="该视频没有字幕，无法生成解读")

    # 触发后台任务
    asyncio.create_task(generate_interpretations_for_material(material_id))

    return {"message": "已开始生成", "status": "generating", "material_id": material_id}


@router.post("/presign-upload", response_model=PresignUploadResponse)
async def presign_upload(
    req: PresignUploadRequest,
    current_admin: User = Depends(get_current_admin),
):
    """生成 OSS PUT presigned URL,前端用这个直接上传到 OSS(绕过 backend)

    用途:解决大文件上传慢的问题(200MB 视频经 backend 中转要 5+ 分钟)
    流程:
      1. 前端调这个接口,得到 3 个 presigned URL
      2. 前端用 PUT 直接上传 3 个文件到 OSS,带 onUploadProgress 真实进度
      3. 上传完成调 /finalize-upload 创建 Material 记录

    需要管理员权限
    """
    storage = get_storage_service()
    expires = 3600  # 1 小时有效

    video_key = generate_object_key('video', req.video_name)
    subtitle_key = generate_object_key('subtitle', req.subtitle_name)
    cover_key = generate_object_key('cover', req.cover_name)

    video_url = await storage.sign_put_url(video_key, "video/mp4", expires)
    subtitle_url = await storage.sign_put_url(subtitle_key, "text/plain", expires)
    cover_url = await storage.sign_put_url(cover_key, "image/jpeg", expires)

    return PresignUploadResponse(
        video=PresignedFileInfo(url=video_url, key=video_key, content_type="video/mp4"),
        subtitle=PresignedFileInfo(url=subtitle_url, key=subtitle_key, content_type="text/plain"),
        cover=PresignedFileInfo(url=cover_url, key=cover_key, content_type="image/jpeg"),
    )


@router.post("/finalize-upload", response_model=MessageResponse)
async def finalize_upload(
    req: FinalizeUploadRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """前端直传 OSS 完成后,调这个接口创建 Material 记录

    验证 3 个文件都已上传到 OSS,然后:
    1. 创建 Material 记录
    2. 下载并解析字幕
    3. 触发后台 AI 解读生成
    """
    storage = get_storage_service()

    # 验证文件都已存在
    if not await storage.file_exists(req.video_key):
        raise HTTPException(status_code=404, detail="视频文件未上传到 OSS")
    if not await storage.file_exists(req.subtitle_key):
        raise HTTPException(status_code=404, detail="字幕文件未上传到 OSS")
    if not await storage.file_exists(req.cover_key):
        raise HTTPException(status_code=404, detail="封面文件未上传到 OSS")

    # 创建 Material
    material = Material(
        title=req.title,
        description=req.description,
        video_path=req.video_key,
        subtitle_path=req.subtitle_key,
        cover_path=req.cover_key,
        category=req.category,
        difficulty=req.difficulty,
        is_active=False,
    )
    db.add(material)
    await db.flush()

    # 下载字幕到临时文件,解析入库
    try:
        tmp_path = f"/tmp/subtitle_{material.id}_{int(time.time())}.srt"
        downloaded = await storage.download_file(req.subtitle_key, tmp_path)
        if downloaded:
            subtitles = await parse_srt_file(tmp_path, material.id)
            for sub in subtitles:
                db.add(Subtitle(**sub.model_dump()))
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        else:
            print(f"[WARN] 字幕文件下载失败: {req.subtitle_key}")
    except Exception as e:
        print(f"字幕解析失败: {e}")

    await db.commit()

    # 触发后台解读
    try:
        from app.services.interpretation_tasks import generate_interpretations_for_material
        asyncio.create_task(generate_interpretations_for_material(material.id))
    except Exception as e:
        print(f"[WARN] 触发解读生成失败: {e}")

    return MessageResponse(message="语料创建成功", success=True)


@router.post("", response_model=MessageResponse)
async def create_material(
    title: Annotated[str, Form()],
    video: Annotated[UploadFile, File()],
    subtitle: Annotated[UploadFile, File()],
    cover: Annotated[UploadFile, File()],
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    difficulty: int = Form(2),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建语料（上传视频、字幕、封面）- 需要管理员权限"""
    storage = get_storage_service()

    # 读取文件内容
    video_data = await video.read()
    subtitle_data = await subtitle.read()
    cover_data = await cover.read()

    # 生成存储键
    video_key = generate_object_key('video', video.filename or 'video.mp4')
    subtitle_key = generate_object_key('subtitle', subtitle.filename or 'subtitle.srt')
    cover_key = generate_object_key('cover', cover.filename or 'cover.jpg')

    # 上传文件到存储服务
    video_url = await storage.upload_file(video_data, video_key, 'video/mp4')
    subtitle_url = await storage.upload_file(subtitle_data, subtitle_key, 'text/plain')
    cover_url = await storage.upload_file(cover_data, cover_key, 'image/jpeg')

    # 创建语料记录（默认未发布，需要管理员审核）
    material = Material(
        title=title,
        description=description,
        video_path=video_url,  # 存储完整URL
        subtitle_path=subtitle_url,
        cover_path=cover_url,
        category=category,
        difficulty=difficulty,
        is_active=False  # 默认未发布，需要管理员审核
    )

    db.add(material)
    await db.flush()

    # 解析字幕（从上传的内容）
    try:
        # 临时保存字幕文件用于解析
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.srt', delete=False) as tmp:
            tmp.write(subtitle_data)
            tmp_path = tmp.name

        subtitles = await parse_srt_file(tmp_path, material.id)
        for sub in subtitles:
            db.add(Subtitle(**sub.model_dump()))

        # 删除临时文件
        os.unlink(tmp_path)
    except Exception as e:
        print(f"字幕解析失败: {e}")

    await db.commit()

    # 触发后台解读生成
    try:
        from app.services.interpretation_tasks import generate_interpretations_for_material
        asyncio.create_task(generate_interpretations_for_material(material.id))
    except Exception as e:
        print(f"[WARN] 触发解读生成失败: {e}")

    return MessageResponse(message="语料创建成功", success=True)


# ==================== 字幕翻译 ====================

@router.post("/{material_id}/translate")
async def translate_subtitles_endpoint(
    material_id: int,
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """翻译字幕 — 分批 + 渐进保存

    长字幕(>40 条)按 BATCH=40 分批调 AI, 每批单独 commit。
    - 增量重试: 已翻译的字幕跳过, 失败批次再调会只重试 pending 部分
    - 单批失败不影响前面已 commit 的批次
    - 返回 translated_count / total / failed_batches 方便前端展示进度
    """
    result = await db.execute(
        select(Subtitle)
        .where(Subtitle.material_id == material_id)
        .order_by(Subtitle.sequence)
    )
    subtitles = result.scalars().all()

    if not subtitles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该视频没有字幕"
        )

    # 全部已翻译 → 短路
    if all(sub.text_cn for sub in subtitles):
        return {
            "success": True,
            "subtitles": [{"text_en": sub.text_en, "text_cn": sub.text_cn} for sub in subtitles],
            "message": "字幕已有翻译"
        }

    # 只翻译未翻译的 (增量重试友好)
    pending = [(idx, sub) for idx, sub in enumerate(subtitles) if not sub.text_cn]
    total_pending = len(pending)
    BATCH = 40
    translated_count = 0
    failed_batches = []

    try:
        for batch_start in range(0, total_pending, BATCH):
            batch = pending[batch_start:batch_start + BATCH]
            batch_lo = batch_start + 1
            batch_hi = min(batch_start + BATCH, total_pending)
            inputs = [{"text_en": sub.text_en} for _, sub in batch]
            print(f"[TRANSLATE] material {material_id}: batch {batch_lo}-{batch_hi}/{total_pending}")

            translated_batch = await translate_subtitles(inputs)

            batch_ok = 0
            for i, (orig_idx, sub) in enumerate(batch):
                if i < len(translated_batch) and translated_batch[i].get("text_cn"):
                    subtitles[orig_idx].text_cn = translated_batch[i]["text_cn"]
                    batch_ok += 1
                    translated_count += 1

            await db.commit()

            if batch_ok == 0:
                failed_batches.append(f"{batch_lo}-{batch_hi}")
                print(f"[TRANSLATE] material {material_id}: batch {batch_lo}-{batch_hi} 全部失败 (AI 返回空)")
            else:
                print(f"[TRANSLATE] material {material_id}: batch {batch_lo}-{batch_hi} ok {batch_ok}/{len(batch)}")

        msg = f"翻译完成 {translated_count}/{total_pending}"
        if failed_batches:
            msg += f", 失败批次: {','.join(failed_batches)}"
        return {
            "success": True,
            "translated_count": translated_count,
            "total": total_pending,
            "failed_batches": failed_batches,
            "message": msg,
            "subtitles": [{"text_en": sub.text_en, "text_cn": sub.text_cn} for sub in subtitles]
        }
    except Exception as e:
        print(f"[ERROR] 翻译失败 material {material_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"翻译失败: {str(e)}"
        )


# ==================== 文本翻译 ====================

@router.post("/translate-text")
async def translate_text_endpoint(
    request: dict
):
    """翻译单个文本"""
    text = request.get("text", "")
    if not text:
        return {"translation": ""}

    try:
        result = await translate_text(text)
        return result
    except Exception as e:
        print(f"[ERROR] 文本翻译失败: {e}")
        return {"translation": text}
