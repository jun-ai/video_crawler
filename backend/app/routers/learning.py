"""
学习记录路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import joinedload
from typing import Annotated, List, Optional
from datetime import datetime, timedelta, timezone
import json
import logging

from app.database import get_db
from app.models.models import User, LearningRecord, Material, Vocabulary, Subtitle, DictationRecord, SubtitleAnnotation, SubtitleBookmark, VideoInterpretation
from app.schemas.schemas import (
    LearningRecordCreate,
    LearningRecordResponse,
    VocabularyCreate,
    VocabularyResponse,
    MessageResponse,
    PronunciationEvaluateRequest,
    PronunciationEvaluateResponse,
    InterpretationLearningCreate,
    InterpretationLearningResponse,
    LearningStatisticsResponse,
    LearningCalendarResponse,
    LearningTrendResponse,
    LearningRecordWithMaterialResponse,
    LearningRecordListResponse,
    SpeechRecognizeResponse,
    DictationSubmitRequest,
    DictationSubmitResponse,
    DictationRecordResponse,
    DictationStatisticsResponse,
    DictationResultDetail,
    SubtitleAnnotationCreate,
    SubtitleAnnotationResponse,
    SubtitleAnnotationListResponse,
    SubtitleBookmarkCreate,
    SubtitleBookmarkResponse,
    ReviewSubmitRequest,
    ReviewQueueResponse,
    ReviewStatsResponse
)
from app.routers.auth import get_current_user
from app.services.deepseek import evaluate_pronunciation as ai_evaluate_pronunciation
from app.services.speech_recognition import speech_service
from app.services.audio_converter import convert_webm_to_wav, check_ffmpeg_available
from app.services.dictation_checker import dictation_checker
from app.models.models import InterpretationLearning, VideoInterpretation
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learning", tags=["学习记录"])

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def get_file_url(file_path: str) -> str:
    """获取文件访问 URL - 将绝对路径转为静态文件URL"""
    if not file_path:
        return ""

    # 如果已经是 HTTP URL（云存储），直接返回
    if file_path.startswith('http://') or file_path.startswith('https://'):
        return file_path

    path = Path(file_path)
    try:
        rel_path = path.relative_to(PROJECT_ROOT)
        rel_path_str = rel_path.as_posix()
    except ValueError:
        # 如果无法转换为相对路径，尝试直接使用文件名
        rel_path_str = path.name

    return f"/static/{rel_path_str}"


@router.post("/progress", response_model=MessageResponse)
async def update_progress(
    data: LearningRecordCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """更新学习进度"""
    # 检查语料是否存在
    result = await db.execute(select(Material).where(Material.id == data.material_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语料不存在"
        )

    # 查找或创建学习记录
    result = await db.execute(
        select(LearningRecord).where(
            LearningRecord.user_id == current_user.id,
            LearningRecord.material_id == data.material_id
        )
    )
    record = result.scalar_one_or_none()

    if record:
        record.progress = data.progress
        record.last_position = data.last_position
        # 如果从未完成变为完成，设置完成时间
        if data.completed and not record.completed:
            record.completed_at = datetime.now(timezone.utc)
        record.completed = data.completed
        record.last_watched_at = datetime.now(timezone.utc)
        if data.watch_duration and data.watch_duration > 0:
            record.watch_duration = (record.watch_duration or 0) + data.watch_duration
    else:
        record = LearningRecord(
            user_id=current_user.id,
            material_id=data.material_id,
            progress=data.progress,
            last_position=data.last_position,
            completed=data.completed,
            watch_duration=data.watch_duration or 0
        )
        db.add(record)

    await db.commit()

    return MessageResponse(message="进度已更新", success=True)


@router.get("/history", response_model=List[LearningRecordResponse])
async def get_history(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取学习历史"""
    result = await db.execute(
        select(LearningRecord)
        .where(LearningRecord.user_id == current_user.id)
        .order_by(LearningRecord.updated_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()

    return records


@router.get("/progress/{material_id}", response_model=LearningRecordResponse)
async def get_material_progress(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某个语料的学习进度"""
    result = await db.execute(
        select(LearningRecord).where(
            LearningRecord.user_id == current_user.id,
            LearningRecord.material_id == material_id
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="暂无学习记录"
        )

    return record


# ==================== 生词本 ====================

@router.post("/vocabulary", response_model=VocabularyResponse)
async def add_vocabulary(
    data: VocabularyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """添加生词"""
    vocabulary = Vocabulary(
        user_id=current_user.id,
        word=data.word,
        context=data.context,
        material_id=data.material_id,
        subtitle_id=data.subtitle_id
    )

    db.add(vocabulary)
    await db.commit()
    await db.refresh(vocabulary)

    return vocabulary


@router.get("/vocabulary")
async def get_vocabulary(
    current_user: Annotated[User, Depends(get_current_user)],
    mastered: bool = None,
    material_id: int = None,
    sort_by: str = Query('newest', description="排序方式: newest/oldest/word_asc/word_desc/review_count"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取生词列表（分页）"""
    base_query = select(Vocabulary).where(Vocabulary.user_id == current_user.id)

    if mastered is not None:
        base_query = base_query.where(Vocabulary.mastered == mastered)

    if material_id is not None:
        base_query = base_query.where(Vocabulary.material_id == material_id)

    # 统计总数
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 分页查询
    query = select(Vocabulary).options(
        joinedload(Vocabulary.subtitle),
        joinedload(Vocabulary.material)
    ).where(Vocabulary.user_id == current_user.id)

    if mastered is not None:
        query = query.where(Vocabulary.mastered == mastered)
    if material_id is not None:
        query = query.where(Vocabulary.material_id == material_id)

    # 排序
    order_map = {
        'newest': Vocabulary.created_at.desc(),
        'oldest': Vocabulary.created_at.asc(),
        'word_asc': Vocabulary.word.asc(),
        'word_desc': Vocabulary.word.desc(),
        'review_count': Vocabulary.review_count.desc(),
    }
    query = query.order_by(order_map.get(sort_by, Vocabulary.created_at.desc()))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    vocabularies = result.scalars().unique().all()

    # 构建响应
    items = []
    for vocab in vocabularies:
        vocab_dict = {
            "id": vocab.id,
            "user_id": vocab.user_id,
            "word": vocab.word,
            "context": vocab.context,
            "material_id": vocab.material_id,
            "material_title": vocab.material.title if vocab.material else None,
            "subtitle_id": vocab.subtitle_id,
            "mastered": vocab.mastered,
            "context_cn": vocab.subtitle.text_cn if vocab.subtitle else None,
            "created_at": vocab.created_at
        }
        items.append(vocab_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/vocabulary/{vocabulary_id}/master", response_model=MessageResponse)
async def mark_vocabulary_mastered(
    vocabulary_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """标记生词为已掌握"""
    result = await db.execute(
        select(Vocabulary).where(
            Vocabulary.id == vocabulary_id,
            Vocabulary.user_id == current_user.id
        )
    )
    vocabulary = result.scalar_one_or_none()

    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生词不存在"
        )

    vocabulary.mastered = True
    await db.commit()

    return MessageResponse(message="已标记为掌握", success=True)


@router.delete("/vocabulary/{vocabulary_id}", response_model=MessageResponse)
async def delete_vocabulary(
    vocabulary_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """删除生词"""
    result = await db.execute(
        select(Vocabulary).where(
            Vocabulary.id == vocabulary_id,
            Vocabulary.user_id == current_user.id
        )
    )
    vocabulary = result.scalar_one_or_none()

    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生词不存在"
        )

    await db.delete(vocabulary)
    await db.commit()

    return MessageResponse(message="生词已删除", success=True)


# ==================== 单词查询缓存 ====================
# 内存级缓存：单词不会变，查一次永久缓存
_word_lookup_cache: dict[str, dict] = {}


@router.get("/vocabulary/lookup")
async def lookup_vocabulary(
    word: str = Query(..., description="要查询的单词"),
    db: AsyncSession = Depends(get_db)
):
    """查询单词 - 获取音标、释义和例句（三级缓存：内存 → DB → DeepSeek）"""
    word_lower = word.lower().strip()

    # 第一级：内存缓存
    if word_lower in _word_lookup_cache:
        return _word_lookup_cache[word_lower]

    # 第二级：从 VideoInterpretation 表查（管理员上传时 AI 预生成的词卡）
    result = await db.execute(
        select(VideoInterpretation).where(
            VideoInterpretation.category == 'word',
            VideoInterpretation.content_en.ilike(word_lower)
        ).limit(1)
    )
    interp = result.scalar_one_or_none()
    if interp:
        data = {
            "word": word_lower,
            "phonetic": interp.phonetic or "",
            "translation": interp.content_cn or interp.english_definition or "",
            "example": interp.example_sentence or ""
        }
        _word_lookup_cache[word_lower] = data
        return data

    # 第三级：调用 DeepSeek API（仅在缓存和 DB 都没有时）
    try:
        from app.services.deepseek import lookup_word, get_deepseek_service

        if get_deepseek_service():
            result = await lookup_word(word)
            data = {
                "word": word_lower,
                "phonetic": result.get("phonetic", ""),
                "translation": result.get("translation", ""),
                "example": result.get("example", "")
            }
            _word_lookup_cache[word_lower] = data
            return data
        else:
            data = {"word": word_lower, "phonetic": "", "translation": word_lower, "example": ""}
            _word_lookup_cache[word_lower] = data
            return data
    except Exception as e:
        logger.warning(f"查询单词失败({word_lower}): {e}")
        data = {"word": word_lower, "phonetic": "", "translation": word_lower, "example": ""}
        # 失败也缓存，避免短时间内重复调失败
        _word_lookup_cache[word_lower] = data
        return data


# ==================== 发音评测 ====================

@router.post("/pronunciation/evaluate", response_model=PronunciationEvaluateResponse)
async def evaluate_pronunciation_endpoint(
    data: PronunciationEvaluateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """发音评测"""
    try:
        result = await ai_evaluate_pronunciation(data.spoken_text, data.expected_text)
        return PronunciationEvaluateResponse(
            score=result.get("score", 70),
            accuracy=result.get("accuracy", "评估完成"),
            fluency=result.get("fluency", "继续练习"),
            problems=result.get("problems", []),
            suggestions=result.get("suggestions", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发音评测失败: {str(e)}"
        )


# ==================== 解读项学习状态 ====================

@router.post("/interpretation/status", response_model=InterpretationLearningResponse)
async def set_interpretation_status(
    data: InterpretationLearningCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """设置解读项的学习状态（认识/不认识/模糊）"""
    # 查找解读项是否存在
    result = await db.execute(
        select(VideoInterpretation).where(VideoInterpretation.id == data.interpretation_id)
    )
    interp = result.scalar_one_or_none()
    if not interp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="解读项不存在"
        )

    # 查找或创建学习状态记录
    result = await db.execute(
        select(InterpretationLearning).where(
            InterpretationLearning.user_id == current_user.id,
            InterpretationLearning.interpretation_id == data.interpretation_id
        )
    )
    record = result.scalar_one_or_none()

    if record:
        record.status = data.status
    else:
        record = InterpretationLearning(
            user_id=current_user.id,
            interpretation_id=data.interpretation_id,
            status=data.status
        )
        db.add(record)

    # 触发学习信号服务（unknown 状态入生词本）
    if data.status == "unknown":
        try:
            from app.services.learning_signal import LearningSignalService
            signal = LearningSignalService(db, current_user)
            await signal.process_interpretation_status(
                interpretation_id=data.interpretation_id,
                status=data.status,
                content=interp.content_en,
            )
        except Exception as sig_err:
            print(f"[WARN] LearningSignalService 失败: {sig_err}")

    await db.commit()
    await db.refresh(record)

    # 返回带解读内容的响应
    return InterpretationLearningResponse(
        id=record.id,
        user_id=record.user_id,
        interpretation_id=data.interpretation_id,
        material_id=data.material_id,
        content_en=interp.content_en,
        content_cn=interp.content_cn,
        category=interp.category,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.get("/interpretation/status/{material_id}", response_model=List[InterpretationLearningResponse])
async def get_material_interpretation_status(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某个材料的所有解读项学习状态"""
    # 获取该材料的所有解读项
    result = await db.execute(
        select(VideoInterpretation).where(
            VideoInterpretation.material_id == material_id
        ).order_by(VideoInterpretation.category, VideoInterpretation.sequence)
    )
    interpretations = result.scalars().all()

    if not interpretations:
        return []

    # 获取用户对这些解读项的学习状态
    interp_ids = [interp.id for interp in interpretations]
    result = await db.execute(
        select(InterpretationLearning).where(
            InterpretationLearning.user_id == current_user.id,
            InterpretationLearning.interpretation_id.in_(interp_ids)
        )
    )
    learning_records = {lr.interpretation_id: lr for lr in result.scalars().all()}

    # 组合响应
    response = []
    for interp in interpretations:
        lr = learning_records.get(interp.id)
        response.append(InterpretationLearningResponse(
            id=lr.id if lr else 0,
            user_id=current_user.id,
            material_id=material_id,
            interpretation_id=interp.id,
            content_en=interp.content_en,
            content_cn=interp.content_cn,
            category=interp.category,
            status=lr.status if lr else "unknown",
            created_at=lr.created_at if lr else None,
            updated_at=lr.updated_at if lr else None
        ))

    return response


# ==================== 学习统计 ====================

@router.get("/statistics", response_model=LearningStatisticsResponse)
async def get_learning_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取学习统计数据"""
    try:
        # 1. 统计学习材料数量
        result = await db.execute(
            select(
                func.count(LearningRecord.id).label('total'),
                func.sum(case((LearningRecord.completed == True, 1), else_=0)).label('completed')
            ).where(LearningRecord.user_id == current_user.id)
        )
        row = result.first()
        total_materials = row[0] or 0 if row else 0
        completed_materials = row[1] or 0 if row else 0
        in_progress_materials = total_materials - completed_materials

        # 2. 统计生词数量
        result = await db.execute(
            select(
                func.count(Vocabulary.id).label('total'),
                func.sum(case((Vocabulary.mastered == True, 1), else_=0)).label('mastered')
            ).where(Vocabulary.user_id == current_user.id)
        )
        vocab_row = result.first()
        total_vocabulary = vocab_row[0] or 0 if vocab_row else 0
        mastered_vocabulary = vocab_row[1] or 0 if vocab_row else 0

        # 3. 计算学习天数
        result = await db.execute(
            select(func.count(func.distinct(func.date(LearningRecord.updated_at))))
            .where(LearningRecord.user_id == current_user.id)
        )
        total_learning_days = result.scalar() or 0

        # 4. 计算本周学习天数
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())  # 本周一
        result = await db.execute(
            select(func.count(func.distinct(func.date(LearningRecord.updated_at))))
            .where(
                LearningRecord.user_id == current_user.id,
                func.date(LearningRecord.updated_at) >= week_start
            )
        )
        this_week_learning_days = result.scalar() or 0

        # 5. 计算连续学习天数
        streak_days = 0
        result = await db.execute(
            select(func.distinct(func.date(LearningRecord.updated_at)))
            .where(LearningRecord.user_id == current_user.id)
            .order_by(func.date(LearningRecord.updated_at).desc())
        )
        rows = result.fetchall()
        learning_dates = [row[0] for row in rows if row[0] is not None]

        if learning_dates:
            check_date = today
            # 如果今天没学习，从昨天开始检查
            if learning_dates[0] != today:
                check_date = today - timedelta(days=1)

            for i, date in enumerate(learning_dates):
                expected_date = check_date - timedelta(days=i)
                if date == expected_date:
                    streak_days += 1
                else:
                    break

        # 6. 计算累计观看时长（分钟）
        result = await db.execute(
            select(func.coalesce(func.sum(LearningRecord.watch_duration), 0))
            .where(LearningRecord.user_id == current_user.id)
        )
        total_watch_seconds = result.scalar() or 0
        total_watch_minutes = total_watch_seconds // 60

        return LearningStatisticsResponse(
            total_materials=total_materials,
            completed_materials=completed_materials,
            in_progress_materials=in_progress_materials,
            total_vocabulary=total_vocabulary,
            mastered_vocabulary=mastered_vocabulary,
            total_learning_days=total_learning_days,
            this_week_learning_days=this_week_learning_days,
            streak_days=streak_days,
            total_watch_minutes=total_watch_minutes
        )
    except Exception as e:
        print(f"Error in get_learning_statistics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get("/trend", response_model=LearningTrendResponse)
async def get_learning_trend(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=7, ge=3, le=30, description="查询天数"),
):
    """获取学习趋势数据（最近N天的每日学习材料数量）"""
    try:
        today = datetime.now().date()
        start_date = today - timedelta(days=days - 1)

        result = await db.execute(
            select(
                func.date(LearningRecord.updated_at).label('date'),
                func.count(func.distinct(LearningRecord.material_id)).label('count')
            )
            .where(
                LearningRecord.user_id == current_user.id,
                func.date(LearningRecord.updated_at) >= start_date,
                func.date(LearningRecord.updated_at) <= today
            )
            .group_by(func.date(LearningRecord.updated_at))
        )

        daily_data = {row.date: row.count for row in result.fetchall() if row.date is not None}

        dates = []
        counts = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            dates.append(d.strftime('%m-%d'))
            counts.append(daily_data.get(d, 0))

        return LearningTrendResponse(dates=dates, counts=counts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习趋势失败: {str(e)}"
        )


def _build_record_with_material(record: LearningRecord, material: Material) -> LearningRecordWithMaterialResponse:
    """构建带材料信息的学习记录响应"""
    return LearningRecordWithMaterialResponse(
        id=record.id,
        user_id=record.user_id,
        material_id=record.material_id,
        progress=record.progress,
        last_position=record.last_position,
        completed=record.completed,
        total_watch_duration=record.watch_duration or 0,
        created_at=record.created_at,
        updated_at=record.updated_at,
        material_title=material.title,
        material_cover=get_file_url(material.cover_path),
        material_category=material.category,
        material_difficulty=material.difficulty,
        material_duration=material.duration
    )


@router.get("/calendar", response_model=LearningCalendarResponse)
async def get_learning_calendar(
    year: int = Query(default=None, description="年份"),
    month: int = Query(default=None, ge=1, le=12, description="月份"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取学习日历数据"""
    try:
        today = datetime.now().date()
        if not year:
            year = today.year
        if not month:
            month = today.month

        # 1. 查询所有有学习记录的日期
        result = await db.execute(
            select(func.distinct(func.date(LearningRecord.updated_at)))
            .where(LearningRecord.user_id == current_user.id)
            .order_by(func.date(LearningRecord.updated_at))
        )
        all_dates = [row[0] for row in result.fetchall() if row[0] is not None]

        # 2. 计算连续学习天数
        streak = 0
        if all_dates:
            sorted_dates = sorted(all_dates, reverse=True)
            check_date = today
            if sorted_dates[0] != today:
                check_date = today - timedelta(days=1)
            for i, date in enumerate(sorted_dates):
                expected = check_date - timedelta(days=i)
                if date == expected:
                    streak += 1
                else:
                    break

        # 3. 计算最长连续天数
        max_streak = 0
        if all_dates:
            sorted_asc = sorted(all_dates)
            current_streak = 1
            for i in range(1, len(sorted_asc)):
                if (sorted_asc[i] - sorted_asc[i-1]).days == 1:
                    current_streak += 1
                else:
                    max_streak = max(max_streak, current_streak)
                    current_streak = 1
            max_streak = max(max_streak, current_streak)

        # 4. 当月累计观看分钟数
        month_start = datetime(year, month, 1).date()
        if month == 12:
            month_end = datetime(year + 1, 1, 1).date()
        else:
            month_end = datetime(year, month + 1, 1).date()

        result = await db.execute(
            select(func.coalesce(func.sum(LearningRecord.watch_duration), 0))
            .where(
                LearningRecord.user_id == current_user.id,
                func.date(LearningRecord.updated_at) >= month_start,
                func.date(LearningRecord.updated_at) < month_end
            )
        )
        monthly_seconds = result.scalar() or 0
        monthly_minutes = monthly_seconds // 60

        # 5. 计算每日学习材料数量
        daily_result = await db.execute(
            select(
                func.date(LearningRecord.updated_at).label('date'),
                func.count(func.distinct(LearningRecord.material_id)).label('count')
            )
            .where(
                LearningRecord.user_id == current_user.id,
                func.date(LearningRecord.updated_at) >= month_start,
                func.date(LearningRecord.updated_at) < month_end
            )
            .group_by(func.date(LearningRecord.updated_at))
        )
        daily_counts = {
            row.date.strftime('%Y-%m-%d'): row.count
            for row in daily_result.fetchall()
            if row.date is not None
        }

        return LearningCalendarResponse(
            dates=[d.strftime('%Y-%m-%d') for d in all_dates],
            streak=streak,
            max_streak=max_streak,
            total_days=len(all_dates),
            monthly_minutes=monthly_minutes,
            daily_counts=daily_counts
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取日历数据失败: {str(e)}"
        )


@router.get("/recent", response_model=List[LearningRecordWithMaterialResponse])
async def get_recent_learning(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取最近学习的材料（未完成的）"""
    result = await db.execute(
        select(LearningRecord, Material)
        .join(Material, LearningRecord.material_id == Material.id)
        .where(
            LearningRecord.user_id == current_user.id,
            LearningRecord.completed == False
        )
        .order_by(LearningRecord.updated_at.desc())
        .limit(limit)
    )
    records = result.all()

    return [_build_record_with_material(record, material) for record, material in records]


@router.get("/completed", response_model=List[LearningRecordWithMaterialResponse])
async def get_completed_learning(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取已完成的材料"""
    result = await db.execute(
        select(LearningRecord, Material)
        .join(Material, LearningRecord.material_id == Material.id)
        .where(
            LearningRecord.user_id == current_user.id,
            LearningRecord.completed == True
        )
        .order_by(LearningRecord.updated_at.desc())
        .limit(limit)
    )
    records = result.all()

    return [_build_record_with_material(record, material) for record, material in records]


@router.get("/records", response_model=LearningRecordListResponse)
async def get_learning_records(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    completed: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页获取学习记录"""
    # 构建查询条件
    base_query = select(LearningRecord, Material).join(
        Material, LearningRecord.material_id == Material.id
    ).where(LearningRecord.user_id == current_user.id)

    if completed is not None:
        base_query = base_query.where(LearningRecord.completed == completed)

    # 获取总数
    count_query = select(func.count(LearningRecord.id)).where(
        LearningRecord.user_id == current_user.id
    )
    if completed is not None:
        count_query = count_query.where(LearningRecord.completed == completed)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    # 分页查询
    result = await db.execute(
        base_query
        .order_by(LearningRecord.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    records = result.all()

    items = [_build_record_with_material(record, material) for record, material in records]

    return LearningRecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ==================== 语音识别 ====================

@router.post("/speech/recognize", response_model=SpeechRecognizeResponse)
async def recognize_and_evaluate_speech(
    audio: UploadFile = File(...),
    expected_text: str = Form(...),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    语音识别 + 发音评测一体化接口

    Args:
        audio: 上传的音频文件 (webm 格式)
        expected_text: 期望的文本（原字幕）

    Returns:
        识别结果 + 发音评测结果
    """
    try:
        # 1. 读取音频数据
        audio_data = await audio.read()

        if not audio_data:
            return SpeechRecognizeResponse(
                success=False,
                recognized_text="",
                confidence=0,
                error="音频数据为空"
            )

        # 2. 检查 ffmpeg 是否可用
        if not check_ffmpeg_available():
            return SpeechRecognizeResponse(
                success=False,
                recognized_text="",
                confidence=0,
                error="服务器未安装 ffmpeg，无法处理音频"
            )

        # 3. 转换格式 (webm -> wav，Whisper推荐格式)
        try:
            wav_data = await convert_webm_to_wav(audio_data)
        except Exception as e:
            return SpeechRecognizeResponse(
                success=False,
                recognized_text="",
                confidence=0,
                error=f"音频格式转换失败: {str(e)}"
            )

        # 4. 调用语音识别
        recognition_result = await speech_service.recognize_audio(
            wav_data,
            audio_format="wav",
            rate=16000,
            language="en"
        )

        if not recognition_result["success"]:
            return SpeechRecognizeResponse(
                success=False,
                recognized_text="",
                confidence=0,
                error=recognition_result.get("error", "语音识别失败")
            )

        recognized_text = recognition_result["text"]

        # 5. 调用发音评测
        try:
            pronunciation_result = await ai_evaluate_pronunciation(recognized_text, expected_text)
            pronunciation_response = PronunciationEvaluateResponse(
                score=pronunciation_result.get("score", 70),
                accuracy=pronunciation_result.get("accuracy", ""),
                fluency=pronunciation_result.get("fluency", ""),
                problems=pronunciation_result.get("problems", []),
                suggestions=pronunciation_result.get("suggestions", [])
            )
        except Exception as e:
            pronunciation_response = PronunciationEvaluateResponse(
                score=70,
                accuracy="评测服务暂时不可用",
                fluency="",
                problems=[],
                suggestions=[]
            )

        return SpeechRecognizeResponse(
            success=True,
            recognized_text=recognized_text,
            confidence=recognition_result.get("confidence", 0.8),
            pronunciation_result=pronunciation_response
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音处理失败: {str(e)}"
        )


# ==================== 听写练习 ====================

@router.post("/dictation/submit", response_model=DictationSubmitResponse)
async def submit_dictation(
    data: DictationSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    提交听写答案并校验
    """
    # 1. 获取正确答案
    result = await db.execute(
        select(Subtitle).where(Subtitle.id == data.subtitle_id)
    )
    subtitle = result.scalar_one_or_none()
    if not subtitle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="字幕不存在"
        )

    # 2. 校验答案
    check_result = dictation_checker.check_partial_correct(
        data.user_input,
        subtitle.text_en
    )

    # 3. 保存记录
    record = DictationRecord(
        user_id=current_user.id,
        material_id=data.material_id,
        subtitle_id=data.subtitle_id,
        user_input=data.user_input,
        correct_text=subtitle.text_en,
        score=check_result["score"],
        accuracy_details=json.dumps(check_result["details"]),
        passed=check_result["passed"]
    )
    db.add(record)
    await db.flush()  # 给 record 分配 id

    # 3.5 触发学习信号服务（低分错词入 Vocabulary）
    new_vocabs: list = []
    try:
        from app.services.learning_signal import LearningSignalService
        signal = LearningSignalService(db, current_user)
        new_vocabs = await signal.process_dictation_result(
            material_id=data.material_id,
            subtitle_id=data.subtitle_id,
            score=check_result["score"],
            user_input=data.user_input,
            correct_text=subtitle.text_en,
        )
    except Exception as sig_err:
        # 信号服务失败不影响主流程
        print(f"[WARN] LearningSignalService 失败: {sig_err}")

    await db.commit()
    await db.refresh(record)

    # 4. 构建详情列表
    details = [DictationResultDetail(**d) for d in check_result["details"]]

    return DictationSubmitResponse(
        id=record.id,
        user_input=data.user_input,
        correct_text=subtitle.text_en,
        score=check_result["score"],
        passed=check_result["passed"],
        details=details,
        feedback=check_result["feedback"]
    )


@router.get("/dictation/records/{material_id}", response_model=List[DictationRecordResponse])
async def get_dictation_records(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某材料的听写记录"""
    result = await db.execute(
        select(DictationRecord)
        .where(
            DictationRecord.user_id == current_user.id,
            DictationRecord.material_id == material_id
        )
        .order_by(DictationRecord.created_at.desc())
    )
    records = result.scalars().all()
    return records


@router.get("/dictation/statistics", response_model=DictationStatisticsResponse)
async def get_dictation_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取听写统计数据"""
    # 总尝试次数
    total_result = await db.execute(
        select(func.count(DictationRecord.id))
        .where(DictationRecord.user_id == current_user.id)
    )
    total_attempts = total_result.scalar() or 0

    # 通过次数
    passed_result = await db.execute(
        select(func.count(DictationRecord.id))
        .where(
            DictationRecord.user_id == current_user.id,
            DictationRecord.passed == True
        )
    )
    passed_count = passed_result.scalar() or 0

    # 平均分
    avg_result = await db.execute(
        select(func.avg(DictationRecord.score))
        .where(DictationRecord.user_id == current_user.id)
    )
    avg_score = avg_result.scalar() or 0

    return DictationStatisticsResponse(
        total_attempts=total_attempts,
        passed_count=passed_count,
        average_score=round(float(avg_score), 1) if avg_score else 0.0
    )


# ==================== 字幕标注 ====================

@router.post("/annotations", response_model=SubtitleAnnotationResponse)
async def add_annotation(
    data: SubtitleAnnotationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """添加字幕标注"""
    # 检查字幕是否存在
    result = await db.execute(select(Subtitle).where(Subtitle.id == data.subtitle_id))
    subtitle = result.scalar_one_or_none()
    if not subtitle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="字幕不存在"
        )

    annotation = SubtitleAnnotation(
        user_id=current_user.id,
        material_id=data.material_id,
        subtitle_id=data.subtitle_id,
        start_offset=data.start_offset,
        end_offset=data.end_offset,
        annotated_text=data.annotated_text,
        annotation_type=data.annotation_type,
        note=data.note,
        color=data.color
    )

    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)

    return annotation


@router.get("/annotations/subtitle/{subtitle_id}", response_model=List[SubtitleAnnotationResponse])
async def get_subtitle_annotations(
    subtitle_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某条字幕的所有标注"""
    result = await db.execute(
        select(SubtitleAnnotation)
        .where(
            SubtitleAnnotation.user_id == current_user.id,
            SubtitleAnnotation.subtitle_id == subtitle_id
        )
        .order_by(SubtitleAnnotation.start_offset)
    )
    annotations = result.scalars().all()
    return annotations


@router.get("/annotations/{material_id}", response_model=List[SubtitleAnnotationResponse])
async def get_material_annotations(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某材料的所有标注"""
    result = await db.execute(
        select(SubtitleAnnotation)
        .where(
            SubtitleAnnotation.user_id == current_user.id,
            SubtitleAnnotation.material_id == material_id
        )
        .order_by(SubtitleAnnotation.subtitle_id, SubtitleAnnotation.start_offset)
    )
    annotations = result.scalars().all()
    return annotations


@router.delete("/annotations/{annotation_id}", response_model=MessageResponse)
async def delete_annotation(
    annotation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """删除标注"""
    result = await db.execute(
        select(SubtitleAnnotation).where(
            SubtitleAnnotation.id == annotation_id,
            SubtitleAnnotation.user_id == current_user.id
        )
    )
    annotation = result.scalar_one_or_none()

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注不存在"
        )

    await db.delete(annotation)
    await db.commit()

    return MessageResponse(message="标注已删除", success=True)


@router.put("/annotations/{annotation_id}", response_model=SubtitleAnnotationResponse)
async def update_annotation(
    annotation_id: int,
    data: SubtitleAnnotationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """更新标注"""
    result = await db.execute(
        select(SubtitleAnnotation).where(
            SubtitleAnnotation.id == annotation_id,
            SubtitleAnnotation.user_id == current_user.id
        )
    )
    annotation = result.scalar_one_or_none()

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注不存在"
        )

    annotation.start_offset = data.start_offset
    annotation.end_offset = data.end_offset
    annotation.annotated_text = data.annotated_text
    annotation.annotation_type = data.annotation_type
    annotation.note = data.note
    annotation.color = data.color

    await db.commit()
    await db.refresh(annotation)

    return annotation


# ==================== 字幕收藏 ====================

@router.post("/bookmarks", response_model=SubtitleBookmarkResponse)
async def add_bookmark(
    data: SubtitleBookmarkCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """收藏字幕行"""
    # 检查字幕是否存在
    result = await db.execute(select(Subtitle).where(Subtitle.id == data.subtitle_id))
    subtitle = result.scalar_one_or_none()
    if not subtitle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="字幕不存在"
        )

    # 检查是否已收藏
    result = await db.execute(
        select(SubtitleBookmark).where(
            SubtitleBookmark.user_id == current_user.id,
            SubtitleBookmark.subtitle_id == data.subtitle_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已收藏该字幕"
        )

    bookmark = SubtitleBookmark(
        user_id=current_user.id,
        material_id=data.material_id,
        subtitle_id=data.subtitle_id,
        note=data.note
    )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)

    return SubtitleBookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        material_id=bookmark.material_id,
        subtitle_id=bookmark.subtitle_id,
        note=bookmark.note,
        practice_count=0,
        created_at=bookmark.created_at,
        subtitle_text_en=subtitle.text_en,
        subtitle_text_cn=subtitle.text_cn,
        subtitle_start_time=subtitle.start_time
    )


@router.delete("/bookmarks/{bookmark_id}", response_model=MessageResponse)
async def remove_bookmark(
    bookmark_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """取消收藏"""
    result = await db.execute(
        select(SubtitleBookmark).where(
            SubtitleBookmark.id == bookmark_id,
            SubtitleBookmark.user_id == current_user.id
        )
    )
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    await db.delete(bookmark)
    await db.commit()

    return MessageResponse(message="已取消收藏", success=True)


@router.post("/bookmarks/{bookmark_id}/practice", response_model=MessageResponse)
async def increment_bookmark_practice(
    bookmark_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """增加收藏字幕的练习次数"""
    result = await db.execute(
        select(SubtitleBookmark).where(
            SubtitleBookmark.id == bookmark_id,
            SubtitleBookmark.user_id == current_user.id
        )
    )
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    bookmark.practice_count = (bookmark.practice_count or 0) + 1
    await db.commit()

    return MessageResponse(message=f"练习次数已更新为 {bookmark.practice_count}", success=True)


@router.get("/bookmarks/check/{material_id}")
async def check_bookmarks(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """检查某个材料中哪些字幕已收藏，返回 subtitle_id 集合"""
    result = await db.execute(
        select(SubtitleBookmark.subtitle_id).where(
            SubtitleBookmark.user_id == current_user.id,
            SubtitleBookmark.material_id == material_id
        )
    )
    bookmarked_ids = [row[0] for row in result.fetchall()]
    return {"bookmarked_ids": bookmarked_ids}


@router.get("/bookmarks/all", response_model=List[SubtitleBookmarkResponse])
async def get_all_user_bookmarks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取用户所有字幕收藏（join Material, 单次查询解决 N+1）

    替代前端循环调用 /bookmarks/{material_id} 的 N+1 模式。
    按 created_at desc 排序，最新收藏在前。
    """
    result = await db.execute(
        select(SubtitleBookmark, Subtitle)
        .join(Subtitle, SubtitleBookmark.subtitle_id == Subtitle.id)
        .where(SubtitleBookmark.user_id == current_user.id)
        .order_by(SubtitleBookmark.created_at.desc())
    )
    rows = result.all()

    response = []
    for bookmark, subtitle in rows:
        response.append(SubtitleBookmarkResponse(
            id=bookmark.id,
            user_id=bookmark.user_id,
            material_id=bookmark.material_id,
            subtitle_id=bookmark.subtitle_id,
            note=bookmark.note,
            practice_count=bookmark.practice_count or 0,
            created_at=bookmark.created_at,
            subtitle_text_en=subtitle.text_en,
            subtitle_text_cn=subtitle.text_cn,
            subtitle_start_time=subtitle.start_time,
        ))
    return response


@router.get("/bookmarks/{material_id}", response_model=List[SubtitleBookmarkResponse])
async def get_material_bookmarks(
    material_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取某材料的所有收藏字幕"""
    result = await db.execute(
        select(SubtitleBookmark, Subtitle)
        .join(Subtitle, SubtitleBookmark.subtitle_id == Subtitle.id)
        .where(
            SubtitleBookmark.user_id == current_user.id,
            SubtitleBookmark.material_id == material_id
        )
        .order_by(Subtitle.start_time)
    )
    rows = result.all()

    response = []
    for bookmark, subtitle in rows:
        response.append(SubtitleBookmarkResponse(
            id=bookmark.id,
            user_id=bookmark.user_id,
            material_id=bookmark.material_id,
            subtitle_id=bookmark.subtitle_id,
            note=bookmark.note,
            practice_count=bookmark.practice_count or 0,
            created_at=bookmark.created_at,
            subtitle_text_en=subtitle.text_en,
            subtitle_text_cn=subtitle.text_cn,
            subtitle_start_time=subtitle.start_time
        ))

    return response


# ==================== 生词复习 (SM-2) ====================

@router.get("/vocabulary/review-queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取待复习生词队列"""
    now = datetime.now()

    # 查询待复习的生词：next_review_at <= now 且未掌握
    result = await db.execute(
        select(Vocabulary).options(
            joinedload(Vocabulary.subtitle),
            joinedload(Vocabulary.material)
        ).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == False,
            or_(
                Vocabulary.next_review_at <= now,
                Vocabulary.next_review_at.is_(None)
            )
        ).order_by(
            # MySQL: NULL 默认为 ASC 时排在最前（兼容原 PostgreSQL 行为）
            # 用 case when 显式处理，保证跨 DB 一致
            case((Vocabulary.next_review_at.is_(None), 0), else_=1),
            Vocabulary.next_review_at.asc()
        )
        .limit(limit)
    )
    vocabularies = result.scalars().unique().all()

    # 统计总数
    due_result = await db.execute(
        select(func.count(Vocabulary.id)).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == False,
            or_(
                Vocabulary.next_review_at <= now,
                Vocabulary.next_review_at.is_(None)
            )
        )
    )
    total_due = due_result.scalar() or 0

    learning_result = await db.execute(
        select(func.count(Vocabulary.id)).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == False
        )
    )
    total_learning = learning_result.scalar() or 0

    # 构建响应
    items = []
    for vocab in vocabularies:
        items.append(VocabularyResponse(
            id=vocab.id,
            user_id=vocab.user_id,
            word=vocab.word,
            context=vocab.context,
            material_id=vocab.material_id,
            material_title=vocab.material.title if vocab.material else None,
            subtitle_id=vocab.subtitle_id,
            mastered=vocab.mastered,
            context_cn=vocab.subtitle.text_cn if vocab.subtitle else None,
            next_review_at=vocab.next_review_at,
            review_count=vocab.review_count,
            last_reviewed_at=vocab.last_reviewed_at,
            ease_factor=vocab.ease_factor,
            interval_days=vocab.interval_days,
            created_at=vocab.created_at
        ))

    return ReviewQueueResponse(items=items, total_due=total_due, total_learning=total_learning)


@router.post("/vocabulary/review", response_model=VocabularyResponse)
async def submit_review(
    data: ReviewSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """提交复习结果 (SM-2 算法)"""
    from app.services.spaced_repetition import sm2_algorithm

    result = await db.execute(
        select(Vocabulary).where(
            Vocabulary.id == data.vocabulary_id,
            Vocabulary.user_id == current_user.id
        )
    )
    vocab = result.scalar_one_or_none()

    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生词不存在"
        )

    # 运行 SM-2 算法
    new_ease, new_interval, new_count = sm2_algorithm(
        quality=data.quality,
        ease_factor=vocab.ease_factor,
        interval_days=vocab.interval_days,
        review_count=vocab.review_count
    )

    # 更新词汇记录
    vocab.ease_factor = new_ease
    vocab.interval_days = new_interval
    vocab.review_count = new_count
    vocab.last_reviewed_at = datetime.now()

    # 计算下次复习时间
    next_review = datetime.now() + timedelta(days=new_interval)
    vocab.next_review_at = next_review

    # 如果质量 >= 4 且复习次数 >= 5，标记为已掌握
    if data.quality >= 4 and new_count >= 5:
        vocab.mastered = True
        vocab.next_review_at = datetime.now() + timedelta(days=365)

    await db.commit()
    await db.refresh(vocab)

    return VocabularyResponse(
        id=vocab.id,
        user_id=vocab.user_id,
        word=vocab.word,
        context=vocab.context,
        material_id=vocab.material_id,
        material_title=None,
        subtitle_id=vocab.subtitle_id,
        mastered=vocab.mastered,
        context_cn=None,
        next_review_at=vocab.next_review_at,
        review_count=vocab.review_count,
        last_reviewed_at=vocab.last_reviewed_at,
        ease_factor=vocab.ease_factor,
        interval_days=vocab.interval_days,
        created_at=vocab.created_at
    )


@router.get("/vocabulary/review-stats", response_model=ReviewStatsResponse)
async def get_review_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """获取复习统计"""
    now = datetime.now()

    # 待复习数
    due_result = await db.execute(
        select(func.count(Vocabulary.id)).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == False,
            or_(
                Vocabulary.next_review_at <= now,
                Vocabulary.next_review_at.is_(None)
            )
        )
    )
    total_due = due_result.scalar() or 0

    # 学习中
    learning_result = await db.execute(
        select(func.count(Vocabulary.id)).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == False
        )
    )
    total_learning = learning_result.scalar() or 0

    # 已掌握
    mastered_result = await db.execute(
        select(func.count(Vocabulary.id)).where(
            Vocabulary.user_id == current_user.id,
            Vocabulary.mastered == True
        )
    )
    total_mastered = mastered_result.scalar() or 0

    return ReviewStatsResponse(
        total_due=total_due,
        total_learning=total_learning,
        total_mastered=total_mastered
    )
