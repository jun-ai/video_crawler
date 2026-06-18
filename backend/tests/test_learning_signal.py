"""LearningSignalService 单元测试 - Task 1.1-1.4"""
import pytest
from app.services.learning_signal import LearningSignalService
from app.models.models import Vocabulary, Material, Subtitle, VideoInterpretation


@pytest.mark.asyncio
async def test_dictation_low_score_creates_vocabulary(db_session, test_user):
    """听写 score<60 应创建 Vocabulary 记录（错词入生词本）"""
    material = Material(
        id=99001, title="Test Material", duration=100,
        video_path="/fake/video.mp4",
        subtitle_path="/fake/subtitle.srt",
        cover_path="/fake/cover.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99001, material_id=99001, sequence=1,
        text_en="hello world", text_cn="你好世界",
        start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    service = LearningSignalService(db_session, test_user)
    await service.process_dictation_result(
        material_id=99001,
        subtitle_id=99001,
        score=40,
        user_input="helo world",
        correct_text="hello world",
    )

    from sqlalchemy import select
    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )
    vocabs = result.scalars().all()
    assert len(vocabs) >= 1, f"应至少创建 1 个生词，实际 {len(vocabs)}"
    vocab_words = [v.word for v in vocabs]
    assert "hello" in vocab_words, f"hello 应在生词列表，实际: {vocab_words}"


@pytest.mark.asyncio
async def test_dictation_high_score_no_vocabulary(db_session, test_user):
    """听写 score>=60 不应创建 Vocabulary"""
    material = Material(
        id=99002, title="T2", duration=100,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99002, material_id=99002, sequence=1,
        text_en="hello world", start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    service = LearningSignalService(db_session, test_user)
    result = await service.process_dictation_result(
        material_id=99002, subtitle_id=99002,
        score=85, user_input="hello world", correct_text="hello world",
    )
    assert result == [], f"高分应返回空列表，实际 {result}"


@pytest.mark.asyncio
async def test_interpretation_unknown_creates_vocabulary(db_session, test_user):
    """EnglishCards 标 unknown 应入 Vocabulary"""
    material = Material(
        id=99003, title="T3", duration=100,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99003, material_id=99003, category="word",
        content_en="ubiquitous", content_cn="普遍",
    )
    db_session.add(interp)
    await db_session.commit()

    service = LearningSignalService(db_session, test_user)
    await service.process_interpretation_status(
        interpretation_id=99003,
        status="unknown",
        content="ubiquitous",
    )

    from sqlalchemy import select
    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )
    vocabs = result.scalars().all()
    assert any(v.word == "ubiquitous" for v in vocabs), \
        f"ubiquitous 应在生词列表，实际: {[v.word for v in vocabs]}"


@pytest.mark.asyncio
async def test_interpretation_known_no_vocabulary(db_session, test_user):
    """EnglishCards 标 known/learning 不应入 Vocabulary"""
    material = Material(
        id=99004, title="T4", duration=100,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99004, material_id=99004, category="word",
        content_en="hello", content_cn="你好",
    )
    db_session.add(interp)
    await db_session.commit()

    service = LearningSignalService(db_session, test_user)
    result = await service.process_interpretation_status(
        interpretation_id=99004,
        status="known",
        content="hello",
    )
    assert result is None, f"known 应返回 None，实际 {result}"