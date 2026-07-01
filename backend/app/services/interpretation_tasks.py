"""
后台解读生成任务
管理员上传视频后自动在后台触发 AI 生成单词/短语/语法卡片
"""
import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.models import Material, Subtitle, VideoInterpretation, InterpretationLearning
from app.services.deepseek import (
    generate_word_cards,
    generate_phrase_cards,
    generate_grammar_points,
    generate_idiom_cards,
)

logger = logging.getLogger(__name__)


# ========== 实时进度跟踪 (供前端轮询展示) ==========
# 6 个 stage 顺序: parse → translate → words → phrases → grammar → idioms
# 写入 materials.progress (JSON 字符串) — 前端 GET /api/materials/{id}/progress 读取

# 阶段定义 (key, 默认 label)
PROGRESS_STAGES: List[Tuple[str, str]] = [
    ("parse",     "解析新字幕"),
    ("translate", "字幕 EN→CN 翻译"),
    ("words",     "AI 生成单词"),
    ("phrases",   "AI 生成短语"),
    ("grammar",   "AI 生成语法点"),
    ("idioms",    "AI 生成地道表达"),
]


async def _set_progress(material_id: int, partial: dict) -> None:
    """写入 materials.progress 当前进度 (异步, 失败也不抛)"""
    try:
        async with async_session_maker() as db:
            result = await db.execute(select(Material).where(Material.id == material_id))
            mat = result.scalar_one_or_none()
            if not mat:
                return
            # 读取已有 progress 作为基线 (保留 stages 列表, 增量更新)
            existing: dict = {}
            if mat.progress:
                try:
                    existing = json.loads(mat.progress)
                except Exception:
                    existing = {}
            stages = existing.get("stages", [
                {"key": k, "label": lbl, "status": "pending"} for k, lbl in PROGRESS_STAGES
            ])
            # 增量合并 partial 到各 stage
            for s in stages:
                if s["key"] in partial:
                    s.update(partial[s["key"]])
            payload = {
                "stages": stages,
                "updated_at": datetime.utcnow().isoformat(),
                "error": existing.get("error"),
            }
            mat.progress = json.dumps(payload, ensure_ascii=False)
            await db.commit()
    except Exception as e:
        logger.warning(f"[Progress] _set_progress({material_id}) failed: {e}")


def _build_initial_progress() -> str:
    """新建一个空 progress JSON (所有 stage 默认 pending)"""
    payload = {
        "stages": [
            {"key": k, "label": lbl, "status": "pending"} for k, lbl in PROGRESS_STAGES
        ],
        "updated_at": datetime.utcnow().isoformat(),
        "error": None,
    }
    return json.dumps(payload, ensure_ascii=False)


# 句子末尾标点 (用于 full-sentence 扩展)
_SENT_END = '.!?。！？'
# 窗口大小: 最多向前 / 向后看多少条字幕拼接完整句子
_CONTEXT_WINDOW = 6


def _build_grammar_explanation(item: dict) -> str:
    """
    从 4 个结构化字段 (structure_analysis / similar_expressions / usage_scenario / alternative_phrasings)
    拼成可读 explanation, 给前端按段落渲染。

    AI 新 prompt 不再要求 explanation 字段 (强制用结构化 4 字段表达),
    这里后端兜底, 保证前端永远能拿到一个可读 explanation 段落。

    输出格式 (用 \\n 真换行, 不是字面 \\n):
        结构: {structure_analysis}
        举一反三: {similar_expressions}
        使用场景: {usage_scenario}
        相似表达: {alternative_phrasings}
    """
    parts = []
    sa = item.get("structure_analysis", "").strip()
    if sa:
        parts.append(f"结构: {sa}")
    se = item.get("similar_expressions", "").strip()
    if se:
        parts.append(f"举一反三: {se}")
    us = item.get("usage_scenario", "").strip()
    if us:
        parts.append(f"使用场景: {us}")
    ap = item.get("alternative_phrasings", "").strip()
    if ap:
        parts.append(f"相似表达: {ap}")
    return "\n".join(parts)


def _extend_to_full_sentence(
    start_seq: int,
    seq_map: Dict[int, "Subtitle"],
    seed_cn: str = "",
) -> Tuple[str, str]:
    """
    从 start_seq 对应的字幕向前 + 向后拼接完整句子。
    返回 (完整英文, 完整中文)。如果无法拼接成完整句子,返回原始单条字幕。

    算法:
    - 向后走最多 5 条字幕,直到遇到句末标点 (.!?。！？)
    - 向前走最多 1 条字幕,只为了解决"单词离句首很近"场景(英文极少)
    """
    if start_seq not in seq_map:
        return "", ""

    cur = seq_map[start_seq]
    parts_en: List[str] = [cur.text_en or ""]
    parts_cn: List[str] = [cur.text_cn or seed_cn] if (cur.text_cn or seed_cn) else [""]

    # 1) 向后拼接直到句末标点
    for offset in range(1, _CONTEXT_WINDOW):
        next_seq = start_seq + offset
        if next_seq not in seq_map:
            break
        nxt = seq_map[next_seq]
        parts_en.append(nxt.text_en or "")
        if nxt.text_cn:
            parts_cn.append(nxt.text_cn)
        # 检查当前追加的这条 EN 是否结尾标点
        text_en_stripped = (nxt.text_en or "").rstrip()
        if text_en_stripped and text_en_stripped[-1] in _SENT_END:
            break
        # 也接受长度超长 (>= 220 字符算长句,不再拼)
        if sum(len(p) for p in parts_en) > 400:
            break

    full_en = " ".join(p.strip() for p in parts_en if p.strip())
    # CN 用 EN 实际拼接的同等数量 (对齐字幕 1:1)
    if parts_cn and parts_cn[0]:
        full_cn = "".join(parts_cn[:len(parts_en)])
    else:
        full_cn = seed_cn

    return full_en, full_cn


async def generate_interpretations_for_material(material_id: int):
    """
    后台任务：为指定素材生成解读内容（单词卡片 + 短语卡片 + 语法点 + 地道表达）
    流程：pending → generating → done / failed
    """
    async with async_session_maker() as db:
        try:
            # 短暂等待，确保调用方事务已完全提交
            await asyncio.sleep(1)

            # 1. 获取素材并标记为 generating
            result = await db.execute(select(Material).where(Material.id == material_id))
            material = result.scalar_one_or_none()
            if not material:
                logger.error(f"[InterpTask] Material {material_id} not found")
                return

            material.interpretation_status = 'generating'
            await db.commit()
            # 只写 AI 4 个 stage 为 running (parse / translate 由各自 caller 提前处理)
            # - replace-subtitle caller: parse=done, translate=done (因为真的跑了)
            # - interpretation/generate caller: parse=skipped, translate=skipped (因为重新解读不重跑)
            await _set_progress(material_id, {
                "words": {"status": "running", "started_at": datetime.utcnow().isoformat()},
                "phrases": {"status": "running", "started_at": datetime.utcnow().isoformat()},
                "grammar": {"status": "running", "started_at": datetime.utcnow().isoformat()},
                "idioms": {"status": "running", "started_at": datetime.utcnow().isoformat()},
            })

            # 2. 获取所有字幕（带完整信息）
            result = await db.execute(
                select(Subtitle)
                .where(Subtitle.material_id == material_id)
                .order_by(Subtitle.sequence)
            )
            subtitles = result.scalars().all()

            if not subtitles:
                material.interpretation_status = 'failed'
                await db.commit()
                logger.warning(f"[InterpTask] Material {material_id} has no subtitles")
                return

            # 构建带 id/sequence/time 的字幕字典列表
            subtitle_dicts = [{
                "id": s.id,
                "sequence": s.sequence,
                "text_en": s.text_en,
                "text_cn": s.text_cn,
                "start_time": s.start_time,
            } for s in subtitles]

            # 构建 sequence → subtitle 映射表
            seq_map = {s.sequence: s for s in subtitles}

            # 3. 并行调用 AI（单词 + 短语 + 语法 + 地道表达），每个带 2 次重试
            logger.info(f"[InterpTask] Starting AI generation for material {material_id}")

            async def _retry(fn, *args, max_retries=2):
                """带重试的 AI 调用包装"""
                for attempt in range(max_retries + 1):
                    try:
                        return await fn(*args)
                    except Exception as e:
                        if attempt < max_retries:
                            logger.warning(f"[InterpTask] {fn.__name__} attempt {attempt+1} failed: {e}, retrying...")
                            await asyncio.sleep(2 * (attempt + 1))
                        else:
                            raise
                return []

            # 每个 AI 生成器独立写自己的 stage 状态 (start / done / failed)
            async def _track(stage_key: str, fn):
                started = datetime.utcnow().isoformat()
                try:
                    res = await _retry(fn, subtitle_dicts)
                    n = len(res) if isinstance(res, list) else 0
                    await _set_progress(material_id, {
                        stage_key: {"status": "done", "started_at": started,
                                    "finished_at": datetime.utcnow().isoformat(), "count": n}
                    })
                    return res
                except Exception as e:
                    await _set_progress(material_id, {
                        stage_key: {"status": "failed",
                                    "started_at": started,
                                    "finished_at": datetime.utcnow().isoformat(),
                                    "error": str(e)[:200]}
                    })
                    raise

            results = await asyncio.gather(
                _track("words", generate_word_cards),
                _track("phrases", generate_phrase_cards),
                _track("grammar", generate_grammar_points),
                _track("idioms", generate_idiom_cards),
                return_exceptions=True,
            )

            # 处理 _track 包装结果 (成功的 list 或 raise 的 Exception)
            words_result = results[0] if not isinstance(results[0], BaseException) else []
            phrases_result = results[1] if not isinstance(results[1], BaseException) else []
            grammar_result = results[2] if not isinstance(results[2], BaseException) else []
            idioms_result = results[3] if not isinstance(results[3], BaseException) else []

            # Exception 已被 _track 写入 progress.stage.error, 这里只记日志
            for stage_key, r in zip(["words","phrases","grammar","idioms"], results):
                if isinstance(r, BaseException):
                    logger.error(f"[InterpTask] {stage_key} failed: {r}")

            if not words_result and not phrases_result and not grammar_result and not idioms_result:
                material.interpretation_status = 'failed'
                await db.commit()
                # 在 progress 顶层记录致命错误 (前端高亮显示)
                async with async_session_maker() as db:
                    r2 = await db.execute(select(Material).where(Material.id == material_id))
                    m2 = r2.scalar_one_or_none()
                    if m2 and m2.progress:
                        try:
                            pdata = json.loads(m2.progress)
                            pdata["error"] = "所有 AI 阶段都失败"
                            m2.progress = json.dumps(pdata, ensure_ascii=False)
                            await db.commit()
                        except Exception:
                            pass
                logger.error(f"[InterpTask] All AI generation failed for material {material_id}")
                return

            # 4. 删除旧的解读数据和学习状态
            old_interp_result = await db.execute(
                select(VideoInterpretation.id).where(VideoInterpretation.material_id == material_id)
            )
            old_interp_ids = [row[0] for row in old_interp_result.fetchall()]
            if old_interp_ids:
                await db.execute(
                    delete(InterpretationLearning).where(
                        InterpretationLearning.interpretation_id.in_(old_interp_ids)
                    )
                )
            await db.execute(
                delete(VideoInterpretation).where(VideoInterpretation.material_id == material_id)
            )

            # 5. 保存单词卡片
            def _resolve_subtitle(item: dict) -> dict:
                """将 AI 返回的 subtitle_sequence 映射为实际 subtitle_id / first_appearance_time"""
                seq = item.pop("subtitle_sequence", None)
                if seq is not None and seq in seq_map:
                    sub = seq_map[seq]
                    item["subtitle_id"] = sub.id
                    item["first_appearance_time"] = sub.start_time
                    # 把字幕原文扩展成完整句子 (跨多个 subtitle 拼接直到末尾标点)
                    # SRT 按时间切片导致单条字幕可能在中段开始/结束;用户看到截断的 "语境" 体验很差
                    full_en, full_cn = _extend_to_full_sentence(
                        seq, seq_map, sub.text_cn if sub.text_cn else ""
                    )
                    # 如果 AI 没有单独提供 context，用扩展后的字幕原文填充
                    if not item.get("context_sentence"):
                        item["context_sentence"] = full_en or sub.text_en
                    if not item.get("context_translation") and sub.text_cn:
                        item["context_translation"] = full_cn or sub.text_cn
                return item

            for i, item in enumerate(words_result):
                item = _resolve_subtitle(item)
                interp = VideoInterpretation(
                    material_id=material_id,
                    category='word',
                    content_en=item.get("content_en", ""),
                    content_cn=item.get("content_cn"),
                    phonetic=item.get("phonetic"),
                    part_of_speech=item.get("part_of_speech"),
                    english_definition=item.get("english_definition"),
                    synonyms=item.get("synonyms"),
                    explanation=item.get("explanation"),
                    example_sentence=item.get("example_sentence"),
                    subtitle_id=item.get("subtitle_id"),
                    first_appearance_time=item.get("first_appearance_time"),
                    context_sentence=item.get("context_sentence"),
                    context_translation=item.get("context_translation"),
                    other_pos_definitions=item.get("other_pos_definitions"),
                    difficulty=item.get("difficulty", 2),
                    frequency_rank=item.get("frequency_rank"),
                    sequence=i,
                )
                db.add(interp)

            # 保存短语卡片
            for i, item in enumerate(phrases_result):
                item = _resolve_subtitle(item)
                interp = VideoInterpretation(
                    material_id=material_id,
                    category='phrase',
                    content_en=item.get("content_en", ""),
                    content_cn=item.get("content_cn"),
                    phonetic=item.get("phonetic"),
                    english_definition=item.get("english_definition"),
                    synonyms=item.get("synonyms"),
                    explanation=item.get("explanation"),
                    example_sentence=item.get("example_sentence"),
                    subtitle_id=item.get("subtitle_id"),
                    first_appearance_time=item.get("first_appearance_time"),
                    context_sentence=item.get("context_sentence"),
                    context_translation=item.get("context_translation"),
                    difficulty=item.get("difficulty", 2),
                    sequence=i,
                )
                db.add(interp)

            # 保存语法点
            for i, item in enumerate(grammar_result):
                item = _resolve_subtitle(item)
                # 兜底: 如果 AI 没返 explanation (新 prompt 删了,强制用结构化 4 字段),
                # 用 4 个结构化字段拼成可读解释
                if not item.get("explanation"):
                    item["explanation"] = _build_grammar_explanation(item)
                interp = VideoInterpretation(
                    material_id=material_id,
                    category='grammar',
                    content_en=item.get("content_en", ""),
                    content_cn=item.get("content_cn"),
                    explanation=item.get("explanation"),
                    example_sentence=item.get("example_sentence"),
                    structure_analysis=item.get("structure_analysis"),
                    similar_expressions=item.get("similar_expressions"),
                    usage_scenario=item.get("usage_scenario"),
                    alternative_phrasings=item.get("alternative_phrasings"),
                    subtitle_id=item.get("subtitle_id"),
                    first_appearance_time=item.get("first_appearance_time"),
                    context_sentence=item.get("context_sentence"),
                    context_translation=item.get("context_translation"),
                    difficulty=item.get("difficulty", 2),
                    sequence=i,
                )
                db.add(interp)

            # 保存地道表达卡片
            for i, item in enumerate(idioms_result):
                item = _resolve_subtitle(item)
                interp = VideoInterpretation(
                    material_id=material_id,
                    category='idiom',
                    content_en=item.get("content_en", ""),
                    content_cn=item.get("content_cn"),
                    explanation=item.get("explanation"),
                    example_sentence=item.get("example_sentence"),
                    subtitle_id=item.get("subtitle_id"),
                    first_appearance_time=item.get("first_appearance_time"),
                    context_sentence=item.get("context_sentence"),
                    context_translation=item.get("context_translation"),
                    difficulty=item.get("difficulty", 2),
                    sequence=i,
                )
                db.add(interp)

            # 6. 标记为完成
            material.interpretation_status = 'done'
            await db.commit()
            logger.info(
                f"[InterpTask] Done for material {material_id}: "
                f"{len(words_result)} words, {len(phrases_result)} phrases, "
                f"{len(grammar_result)} grammar, {len(idioms_result)} idioms"
            )

        except Exception as e:
            logger.error(f"[InterpTask] Failed for material {material_id}: {e}", exc_info=True)
            try:
                async with async_session_maker() as db2:
                    result = await db2.execute(select(Material).where(Material.id == material_id))
                    mat = result.scalar_one_or_none()
                    if mat:
                        mat.interpretation_status = 'failed'
                        await db2.commit()
            except Exception:
                pass
