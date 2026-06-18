"""Task 1.12: 端到端冒烟 - 听写 → 入 Vocabulary → 出现在 review-queue"""
import pytest


@pytest.mark.asyncio
async def test_e2e_dictation_to_review_loop(
    client, auth_headers, db_session, test_user
):
    """完整流程：提交低分听写 → 入 Vocabulary → 出现在 review-queue"""
    from app.models.models import Material, Subtitle, Vocabulary, DictationRecord
    from sqlalchemy import select

    # 准备数据
    material = Material(
        id=99901, title="E2E", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99901, material_id=99901, sequence=1,
        text_en="hello world",
        start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    # 1. 提交低分听写
    response = await client.post(
        "/api/learning/dictation/submit",
        headers=auth_headers,
        json={
            "material_id": 99901,
            "subtitle_id": 99901,
            "user_input": "helo wrld",  # 错两个
        },
    )
    assert response.status_code == 200
    data = response.json()
    score = data["score"]
    assert score < 60, f"全错应 <60，实际 {score}"

    # 2. DictationRecord 写入
    recs = (await db_session.execute(
        select(DictationRecord).where(DictationRecord.user_id == test_user.id)
    )).scalars().all()
    assert len(recs) == 1
    assert recs[0].score == score

    # 3. Vocabulary 表有错词
    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert len(vocabs) >= 1, f"低分应入 Vocabulary，实际 0"
    vocab_words = [v.word for v in vocabs]
    # 至少应该有 hello 或 world 中之一
    assert any(w in vocab_words for w in ["hello", "world"]), \
        f"应至少包含 hello/world，实际: {vocab_words}"

    # 4. 出现在 review-queue
    response = await client.get(
        "/api/learning/vocabulary/review-queue",
        headers=auth_headers,
    )
    assert response.status_code == 200
    queue = response.json()
    queue_words = [item.get("word") for item in queue.get("items", []) if isinstance(item, dict)]
    if not queue_words and "queue" in queue:
        queue_words = [item.get("word") for item in queue["queue"]]
    # review-queue 可能不返回 word 字段，只返回 vocabulary_id
    queue_ids = [item.get("vocabulary_id") or item.get("id") for item in queue.get("items", queue.get("queue", []))]
    vocab_ids = [v.id for v in vocabs]
    assert any(qid in vocab_ids for qid in queue_ids if qid is not None), \
        f"review-queue 应包含新增 vocab {vocab_ids}，实际 {queue_ids}"


@pytest.mark.asyncio
async def test_e2e_interpretation_to_review_loop(
    client, auth_headers, db_session, test_user
):
    """完整流程：EnglishCards 标 unknown → 入 Vocabulary → 出现在 review-queue"""
    from app.models.models import Material, VideoInterpretation, Vocabulary
    from sqlalchemy import select

    material = Material(
        id=99902, title="E2E2", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99902, material_id=99902, category="word",
        content_en="serendipity", content_cn="意外的好运",
    )
    db_session.add(interp)
    await db_session.commit()

    # 1. 标 unknown
    response = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99902, "material_id": 99902, "status": "unknown"},
    )
    assert response.status_code == 200

    # 2. Vocabulary 表有 serendipity
    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert any(v.word == "serendipity" for v in vocabs), \
        f"serendipity 应在生词表，实际: {[v.word for v in vocabs]}"

    # 3. 出现在 review-queue
    response = await client.get(
        "/api/learning/vocabulary/review-queue",
        headers=auth_headers,
    )
    assert response.status_code == 200
    queue = response.json()
    queue_items = queue.get("items", queue.get("queue", []))
    queue_ids = [item.get("vocabulary_id") or item.get("id") for item in queue_items]
    vocab_ids = [v.id for v in vocabs]
    assert any(qid in vocab_ids for qid in queue_ids if qid is not None)


@pytest.mark.asyncio
async def test_e2e_high_score_no_vocab_no_review(
    client, auth_headers, db_session, test_user
):
    """全对听写不应入 Vocabulary，也不应进 review-queue"""
    from app.models.models import Material, Subtitle, Vocabulary
    from sqlalchemy import select

    material = Material(
        id=99903, title="E2E3", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=99903, material_id=99903, sequence=1,
        text_en="good morning",
        start_time=0, end_time=1000,
    )
    db_session.add(subtitle)
    await db_session.commit()

    # 全对
    response = await client.post(
        "/api/learning/dictation/submit",
        headers=auth_headers,
        json={
            "material_id": 99903,
            "subtitle_id": 99903,
            "user_input": "good morning",
        },
    )
    assert response.status_code == 200
    assert response.json()["score"] >= 60

    # 无新 vocab
    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert len(vocabs) == 0, f"全对应无 vocab，实际 {len(vocabs)}"
