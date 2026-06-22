"""
后台解读生成任务
管理员上传视频后自动在后台触发 AI 生成单词/短语/语法卡片
"""
import asyncio
import json
import logging
from typing import Dict, List, Any

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

            results = await asyncio.gather(
                _retry(generate_word_cards, subtitle_dicts),
                _retry(generate_phrase_cards, subtitle_dicts),
                _retry(generate_grammar_points, subtitle_dicts),
                _retry(generate_idiom_cards, subtitle_dicts),
                return_exceptions=True,
            )

            words_result = results[0] if not isinstance(results[0], Exception) else []
            phrases_result = results[1] if not isinstance(results[1], Exception) else []
            grammar_result = results[2] if not isinstance(results[2], Exception) else []
            idioms_result = results[3] if not isinstance(results[3], Exception) else []

            if isinstance(results[0], Exception):
                logger.error(f"[InterpTask] Word generation failed: {results[0]}")
            if isinstance(results[1], Exception):
                logger.error(f"[InterpTask] Phrase generation failed: {results[1]}")
            if isinstance(results[2], Exception):
                logger.error(f"[InterpTask] Grammar generation failed: {results[2]}")
            if isinstance(results[3], Exception):
                logger.error(f"[InterpTask] Idiom generation failed: {results[3]}")

            if not words_result and not phrases_result and not grammar_result and not idioms_result:
                material.interpretation_status = 'failed'
                await db.commit()
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
                    # 如果 AI 没有单独提供 context，用字幕原文填充
                    if not item.get("context_sentence"):
                        item["context_sentence"] = sub.text_en
                    if not item.get("context_translation") and sub.text_cn:
                        item["context_translation"] = sub.text_cn
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
                interp = VideoInterpretation(
                    material_id=material_id,
                    category='grammar',
                    content_en=item.get("content_en", ""),
                    content_cn=item.get("content_cn"),
                    explanation=item.get("explanation"),
                    example_sentence=item.get("example_sentence"),
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
