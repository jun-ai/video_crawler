"""
Batch 5 P2-5: 词汇星标 (重点标记)

后端:
- Vocabulary model 加 starred 字段 (Boolean, default=False, indexed)
- alembic migration: a3bb785_starred_add_vocabulary_starred
- PUT /vocabulary/{id}/star: 标记重点
- PUT /vocabulary/{id}/unstar: 取消重点
- POST /vocabulary/batch-star: 批量标记
- POST /vocabulary/batch-unstar: 批量取消
- get_vocabulary 响应含 starred
- sort_by='starred_first': starred 优先
- export JSON/CSV 含 starred

测试覆盖:
- star/unstar 单条 (含 toggle 重复 idempotent)
- batch-star / batch-unstar
- 跨用户隔离
- starred 与 mastered 互不影响
- starred_first 排序
- 空 ids 返回 success=False
"""
import pytest


@pytest.fixture
async def star_setup(db_session, test_user):
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    v1 = Vocabulary(user_id=test_user.id, material_id=1, word="run",
                   review_count=0, next_review_at=None, mastered=False)
    v2 = Vocabulary(user_id=test_user.id, material_id=1, word="jog",
                   review_count=5, next_review_at=None, mastered=True)
    v3 = Vocabulary(user_id=test_user.id, material_id=1, word="sprint",
                   review_count=2, next_review_at=None, mastered=False)
    db_session.add_all([v1, v2, v3])
    await db_session.commit()
    await db_session.refresh(v1)
    await db_session.refresh(v2)
    await db_session.refresh(v3)
    return {"run": v1, "jog": v2, "sprint": v3}


@pytest.mark.asyncio
async def test_star_marks_vocabulary(client, auth_headers, db_session, star_setup):
    """PUT /star: 把指定词标为重点"""
    vocab_id = star_setup["run"].id

    response = await client.put(
        f"/api/learning/vocabulary/{vocab_id}/star",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # DB 验证 starred=True
    from app.models.models import Vocabulary
    from sqlalchemy import select
    v = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.id == vocab_id)
    )).scalar_one()
    assert v.starred is True


@pytest.mark.asyncio
async def test_star_idempotent(client, auth_headers, db_session, star_setup):
    """重复 star 不报错 (idempotent)"""
    vocab_id = star_setup["run"].id

    # 第一次 star
    r1 = await client.put(f"/api/learning/vocabulary/{vocab_id}/star", headers=auth_headers)
    assert r1.status_code == 200

    # 第二次 star 仍然 OK
    r2 = await client.put(f"/api/learning/vocabulary/{vocab_id}/star", headers=auth_headers)
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_unstar_removes_star(client, auth_headers, db_session, star_setup):
    """unstar 后 starred=False"""
    from app.models.models import Vocabulary
    from sqlalchemy import select

    vocab_id = star_setup["run"].id

    # 先 star
    await client.put(f"/api/learning/vocabulary/{vocab_id}/star", headers=auth_headers)

    # 再 unstar
    response = await client.put(
        f"/api/learning/vocabulary/{vocab_id}/unstar",
        headers=auth_headers
    )
    assert response.status_code == 200

    v = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.id == vocab_id)
    )).scalar_one()
    assert v.starred is False


@pytest.mark.asyncio
async def test_star_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """A 不能 star B 的词 (404)"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="otherstar",
        phone="13800139900",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    other_vocab = Vocabulary(
        user_id=other_user.id, material_id=1, word="other_word",
        review_count=0, next_review_at=None, mastered=False
    )
    db_session.add(other_vocab)
    await db_session.commit()
    await db_session.refresh(other_vocab)

    # A 尝试 star B 的词
    response = await client.put(
        f"/api/learning/vocabulary/{other_vocab.id}/star",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_star_does_not_change_mastered(
    client, auth_headers, db_session, star_setup
):
    """star 不影响 mastered (两个维度独立)"""
    from app.models.models import Vocabulary
    from sqlalchemy import select

    # 'jog' 是 mastered=True, star 一下, mastered 仍为 True
    vocab_id = star_setup["jog"].id

    response = await client.put(
        f"/api/learning/vocabulary/{vocab_id}/star",
        headers=auth_headers
    )
    assert response.status_code == 200

    v = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.id == vocab_id)
    )).scalar_one()
    assert v.starred is True
    assert v.mastered is True  # mastered 保持 True


@pytest.mark.asyncio
async def test_master_does_not_change_starred(
    client, auth_headers, db_session, star_setup
):
    """master 不影响 starred (反向验证)"""
    from app.models.models import Vocabulary
    from sqlalchemy import select

    # 先 star 'run'
    vocab_id = star_setup["run"].id
    await client.put(f"/api/learning/vocabulary/{vocab_id}/star", headers=auth_headers)

    # 再 master
    await client.put(f"/api/learning/vocabulary/{vocab_id}/master", headers=auth_headers)

    v = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.id == vocab_id)
    )).scalar_one()
    assert v.starred is True  # starred 保持
    assert v.mastered is True


@pytest.mark.asyncio
async def test_batch_star_marks_multiple(client, auth_headers, db_session, star_setup):
    """batch-star: 标记多个"""
    ids = [star_setup["run"].id, star_setup["sprint"].id]

    response = await client.post(
        "/api/learning/vocabulary/batch-star",
        json={"ids": ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "已标记 2 词为重点" in data["message"]

    # DB 验证
    from app.models.models import Vocabulary
    from sqlalchemy import select
    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.id.in_(ids))
    )
    vocabs = result.scalars().all()
    for v in vocabs:
        assert v.starred is True


@pytest.mark.asyncio
async def test_batch_unstar_removes_multiple(client, auth_headers, db_session, star_setup):
    """batch-unstar: 取消多个"""
    from app.models.models import Vocabulary
    from sqlalchemy import select

    # 先全部 star
    all_ids = [star_setup["run"].id, star_setup["sprint"].id]
    await client.post(
        "/api/learning/vocabulary/batch-star",
        json={"ids": all_ids},
        headers=auth_headers
    )

    # 再 batch unstar
    response = await client.post(
        "/api/learning/vocabulary/batch-unstar",
        json={"ids": all_ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "已取消 2 词的重点" in response.json()["message"]

    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.id.in_(all_ids))
    )
    vocabs = result.scalars().all()
    for v in vocabs:
        assert v.starred is False


@pytest.mark.asyncio
async def test_batch_star_cross_user_isolation(
    client, auth_headers, db_session, test_user, star_setup
):
    """batch-star: B 的 id 被 A 操作应跳过"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash
    from sqlalchemy import select

    other_user = User(
        username="otherbatchstar",
        phone="13800139888",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=2, title="V2", duration=10,
                            video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"))
    db_session.add(Vocabulary(
        user_id=other_user.id, material_id=2, word="other_star",
        review_count=0, next_review_at=None, mastered=False
    ))
    await db_session.commit()

    other_vocab = (await db_session.execute(
        select(Vocabulary).where(Vocabulary.word == "other_star")
    )).scalar_one()

    response = await client.post(
        "/api/learning/vocabulary/batch-star",
        json={"ids": [other_vocab.id]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "已标记 0 词为重点" in data["message"]
    assert "跳过 1 条" in data["message"]


@pytest.mark.asyncio
async def test_batch_star_empty_ids_returns_false(client, auth_headers):
    """空 ids 返回 success=False"""
    for endpoint in ["batch-star", "batch-unstar"]:
        response = await client.post(
            f"/api/learning/vocabulary/{endpoint}",
            json={"ids": []},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


@pytest.mark.asyncio
async def test_get_vocabulary_includes_starred(client, auth_headers, star_setup):
    """/vocabulary 响应含 starred 字段"""
    # 先 star 'run'
    await client.put(
        f"/api/learning/vocabulary/{star_setup['run'].id}/star",
        headers=auth_headers
    )

    response = await client.get(
        "/api/learning/vocabulary?page_size=100",
        headers=auth_headers
    )
    assert response.status_code == 200
    items = response.json()["items"]
    run = next(i for i in items if i["word"] == "run")
    assert run["starred"] is True
    jog = next(i for i in items if i["word"] == "jog")
    assert jog["starred"] is False


@pytest.mark.asyncio
async def test_sort_starred_first(client, auth_headers, star_setup):
    """sort_by=starred_first: starred 词排前"""
    # 只 star 'run'
    await client.put(
        f"/api/learning/vocabulary/{star_setup['run'].id}/star",
        headers=auth_headers
    )

    response = await client.get(
        "/api/learning/vocabulary?sort_by=starred_first&page_size=100",
        headers=auth_headers
    )
    items = response.json()["items"]
    # 'run' 是 starred, 应该排第一位
    assert items[0]["word"] == "run"
    assert items[0]["starred"] is True


@pytest.mark.asyncio
async def test_export_includes_starred(client, auth_headers, star_setup):
    """export JSON/CSV 都含 starred"""
    await client.put(
        f"/api/learning/vocabulary/{star_setup['run'].id}/star",
        headers=auth_headers
    )

    # JSON
    r_json = await client.get(
        "/api/learning/vocabulary/export?format=json",
        headers=auth_headers
    )
    body = r_json.json()
    run = next(i for i in body["items"] if i["word"] == "run")
    assert run["starred"] is True

    # CSV
    r_csv = await client.get(
        "/api/learning/vocabulary/export?format=csv",
        headers=auth_headers
    )
    import csv
    import io
    text = r_csv.content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    assert "starred" in reader.fieldnames
    run_csv = next(r for r in rows if r["word"] == "run")
    assert run_csv["starred"] == "true"


@pytest.mark.asyncio
async def test_star_nonexistent_returns_404(client, auth_headers):
    """star 不存在的 id 返回 404"""
    response = await client.put(
        "/api/learning/vocabulary/99999/star",
        headers=auth_headers
    )
    assert response.status_code == 404