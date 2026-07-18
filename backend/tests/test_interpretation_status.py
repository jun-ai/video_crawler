"""Task 1.6: set_interpretation_status 接入 LearningSignalService 测试"""
import pytest


@pytest.mark.asyncio
async def test_set_interpretation_status_unknown_creates_vocabulary(
    client, auth_headers, db_session, test_user
):
    """EnglishCards 标 unknown 应入 Vocabulary"""
    from app.models.models import Material, VideoInterpretation, InterpretationLearning, Vocabulary
    from sqlalchemy import select

    material = Material(
        id=99601, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99601, material_id=99601, category="word",
        content_en="ubiquitous", content_cn="普遍",
    )
    db_session.add(interp)
    await db_session.commit()

    response = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99601, "material_id": 99601, "status": "unknown"},
    )
    assert response.status_code == 200, f"got {response.status_code}: {response.text}"

    # Vocabulary 表有 ubiquitous
    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert any(v.word == "ubiquitous" for v in vocabs), \
        f"ubiquitous 应在生词表，实际 {[v.word for v in vocabs]}"

    # InterpretationLearning 记录已写
    il = (await db_session.execute(
        select(InterpretationLearning).where(
            InterpretationLearning.user_id == test_user.id,
            InterpretationLearning.interpretation_id == 99601,
        )
    )).scalar_one_or_none()
    assert il is not None
    assert il.status == "unknown"


@pytest.mark.asyncio
async def test_set_interpretation_status_known_no_vocabulary(
    client, auth_headers, db_session, test_user
):
    """EnglishCards 标 known 不应入 Vocabulary"""
    from app.models.models import Material, VideoInterpretation, Vocabulary
    from sqlalchemy import select

    material = Material(
        id=99602, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99602, material_id=99602, category="word",
        content_en="common", content_cn="常见",
    )
    db_session.add(interp)
    await db_session.commit()

    response = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99602, "material_id": 99602, "status": "known"},
    )
    assert response.status_code == 200

    vocabs = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.user_id == test_user.id)
    )).scalars().all()
    assert len(vocabs) == 0, f"known 不应入 Vocabulary，实际 {len(vocabs)}"


@pytest.mark.asyncio
async def test_get_interpretation_status_unmarked_when_no_record(
    client, auth_headers, db_session
):
    """从未操作过的卡片必须是 unmarked，不能伪装成用户主动点过 unknown。"""
    from app.models.models import Material, VideoInterpretation

    material = Material(
        id=99604, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    db_session.add(VideoInterpretation(
        id=99604, material_id=99604, category="word",
        content_en="fresh", content_cn="新的",
    ))
    await db_session.commit()

    response = await client.get(
        "/api/learning/interpretation/status/99604",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()[0]["status"] == "unmarked"


@pytest.mark.asyncio
async def test_set_interpretation_status_update_existing(
    client, auth_headers, db_session, test_user
):
    """重复设置状态应更新而非新增"""
    from app.models.models import Material, VideoInterpretation, InterpretationLearning
    from sqlalchemy import select

    material = Material(
        id=99603, title="T", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(material)
    interp = VideoInterpretation(
        id=99603, material_id=99603, category="word",
        content_en="test", content_cn="测试",
    )
    db_session.add(interp)
    await db_session.commit()

    # 第一次：unknown
    r1 = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99603, "material_id": 99603, "status": "unknown"},
    )
    assert r1.status_code == 200

    # 第二次：known（更新）
    r2 = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99603, "material_id": 99603, "status": "known"},
    )
    assert r2.status_code == 200

    # 只有 1 条 InterpretationLearning
    records = (await db_session.execute(
        select(InterpretationLearning).where(
            InterpretationLearning.user_id == test_user.id,
            InterpretationLearning.interpretation_id == 99603,
        )
    )).scalars().all()
    assert len(records) == 1
    assert records[0].status == "known"


@pytest.mark.asyncio
async def test_set_interpretation_status_not_found(client, auth_headers):
    """不存在的解读项应 404"""
    response = await client.post(
        "/api/learning/interpretation/status",
        headers=auth_headers,
        json={"interpretation_id": 99999, "material_id": 99999, "status": "known"},
    )
    assert response.status_code == 404
