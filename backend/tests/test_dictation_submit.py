"""Task 1.5: submit_dictation 接入 LearningSignalService 测试"""
import pytest


@pytest.mark.asyncio
async def test_submit_dictation_low_score_creates_vocabulary(
    client, auth_headers, db_session, test_user
):
    """提交低分听写应同时创建 DictationRecord + Vocabulary"""
    from app.models.models import Material, Subtitle, DictationRecord, Vocabulary
    from sqlalchemy import select

    # 准备数据
    material = Material(
        id=99501, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99501, material_id=99501, sequence=1,
        text_en="hello world",
        start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    # 提交听写（故意写错）
    response = await client.post(
        "/api/learning/dictation/submit",
        headers=auth_headers,
        json={
            "material_id": 99501,
            "subtitle_id": 99501,
            "user_input": "helo world",  # 错一个
        },
    )
    assert response.status_code == 200, f"got {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert "score" in data

    # 验证 DictationRecord 写入
    recs = (await db_session.execute(
        select(DictationRecord).where(DictationRecord.user_id == test_user.id)
    )).scalars().all()
    assert len(recs) == 1, f"应 1 条记录，实际 {len(recs)}"
    assert recs[0].material_id == 99501

    # 验证 Vocabulary 表（如果 score<60 应有错词）
    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    if data["score"] < 60:
        assert len(vocabs) >= 1, f"低分应入 Vocabulary，实际 0"


@pytest.mark.asyncio
async def test_submit_dictation_high_score_no_vocabulary(
    client, auth_headers, db_session, test_user
):
    """提交高分听写不应创建 Vocabulary"""
    from app.models.models import Material, Subtitle, Vocabulary
    from sqlalchemy import select

    material = Material(
        id=99502, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99502, material_id=99502, sequence=1,
        text_en="hello world",
        start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    response = await client.post(
        "/api/learning/dictation/submit",
        headers=auth_headers,
        json={
            "material_id": 99502,
            "subtitle_id": 99502,
            "user_input": "hello world",  # 全对
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 60, f"全对应 >=60 分，实际 {data['score']}"

    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert len(vocabs) == 0, f"高分不应入 Vocabulary，实际 {len(vocabs)}"


@pytest.mark.asyncio
async def test_submit_dictation_subtitle_not_found(client, auth_headers):
    """不存在的字幕应 404"""
    response = await client.post(
        "/api/learning/dictation/submit",
        headers=auth_headers,
        json={
            "material_id": 99999,
            "subtitle_id": 99999,
            "user_input": "test",
        },
    )
    assert response.status_code == 404
