"""
Batch 5 P0-4: 词汇批量操作

后端 3 个批量端点:
- POST /vocabulary/batch-master: 批量标记掌握 (mastered=True, 保留 SM-2 历史)
- POST /vocabulary/batch-unmaster: 批量取消掌握 (mastered=False, 保留 SM-2)
- POST /vocabulary/batch-delete: 批量删除

测试覆盖:
- batch-master: 标记多个为已掌握
- batch-unmaster: 取消多个
- batch-delete: 删除多个
- 空 ids: 返回 success=False
- 跨用户隔离: B 用户的词不能被 A 操作
"""
import pytest


@pytest.fixture
async def vocab_setup(db_session, test_user):
    """基础 fixture: 1 个 material + 3 个生词 (新词/已掌握/学习中)"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    v_new = Vocabulary(user_id=test_user.id, material_id=1, word="new_word",
                      review_count=0, next_review_at=None, mastered=False)
    v_learning = Vocabulary(user_id=test_user.id, material_id=1, word="learning_word",
                           review_count=2, next_review_at=None, mastered=False)
    v_mastered = Vocabulary(user_id=test_user.id, material_id=1, word="mastered_word",
                           review_count=5, next_review_at=None, mastered=True)
    db_session.add_all([v_new, v_learning, v_mastered])
    await db_session.commit()
    await db_session.refresh(v_new)
    await db_session.refresh(v_learning)
    await db_session.refresh(v_mastered)
    return {"new": v_new, "learning": v_learning, "mastered": v_mastered}


@pytest.mark.asyncio
async def test_batch_master_marks_multiple(client, auth_headers, vocab_setup):
    """batch-master: 把 new + learning 标记为已掌握 (mastered_word 已掌握, 无变化)"""
    ids = [vocab_setup["new"].id, vocab_setup["learning"].id]

    response = await client.post(
        "/api/learning/vocabulary/batch-master",
        json={"ids": ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "已标记 2 词" in data["message"]

    # 验证数据库状态
    list_response = await client.get(
        "/api/learning/vocabulary?page_size=100",
        headers=auth_headers
    )
    items = list_response.json()["items"]
    mastered_words = {item["word"] for item in items if item["mastered"]}
    assert {"new_word", "learning_word", "mastered_word"}.issubset(mastered_words)


@pytest.mark.asyncio
async def test_batch_unmaster_marks_multiple(client, auth_headers, db_session, vocab_setup):
    """batch-unmaster: 把 mastered 取消 (mastered_word -> not mastered, 保留 SM-2)"""
    from app.models.models import Vocabulary
    from sqlalchemy import select

    vocab_id = vocab_setup["mastered"].id
    ids = [vocab_id]

    response = await client.post(
        "/api/learning/vocabulary/batch-unmaster",
        json={"ids": ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "已取消 1 词" in data["message"]

    # 直接查 DB 验证 mastered=False + SM-2 历史保留 (review_count=5, ease_factor=2.5)
    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.id == vocab_id)
    )
    v = result.scalar_one()
    assert v.mastered is False
    assert v.review_count == 5  # SM-2 历史保留
    assert v.ease_factor == 2.5  # SM-2 历史保留


@pytest.mark.asyncio
async def test_batch_delete_removes_multiple(client, auth_headers, vocab_setup):
    """batch-delete: 删除 new + mastered, learning 保留"""
    ids = [vocab_setup["new"].id, vocab_setup["mastered"].id]

    response = await client.post(
        "/api/learning/vocabulary/batch-delete",
        json={"ids": ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "已删除 2 词" in data["message"]

    # 验证数据库: 只剩 learning_word
    list_response = await client.get(
        "/api/learning/vocabulary?page_size=100",
        headers=auth_headers
    )
    items = list_response.json()["items"]
    words = [item["word"] for item in items]
    assert "new_word" not in words
    assert "mastered_word" not in words
    assert "learning_word" in words


@pytest.mark.asyncio
async def test_batch_empty_ids_returns_false(client, auth_headers):
    """空 ids 列表: 返回 success=False, 不报错"""
    for endpoint in ["batch-master", "batch-unmaster", "batch-delete"]:
        response = await client.post(
            f"/api/learning/vocabulary/{endpoint}",
            json={"ids": []},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "无选中项" in data["message"]


@pytest.mark.asyncio
async def test_batch_cross_user_isolation(
    client, auth_headers, db_session, test_user, vocab_setup
):
    """跨用户隔离: B 用户的词汇 id 不能被 A 操作"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    # 创建 B 用户 + 一个生词
    other_user = User(
        username="otherbatch",
        phone="13800139955",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=2, title="V2", duration=10,
                            video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"))

    other_vocab = Vocabulary(
        user_id=other_user.id, material_id=2, word="other_user_word",
        review_count=0, next_review_at=None, mastered=False
    )
    db_session.add(other_vocab)
    await db_session.commit()
    await db_session.refresh(other_vocab)

    # A 试图操作 B 的词汇 id
    response = await client.post(
        "/api/learning/vocabulary/batch-master",
        json={"ids": [other_vocab.id]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # A 的请求应跳过 B 的词 (success=True 但更新 0 条)
    assert "已标记 0 词" in data["message"]
    assert "跳过 1 条" in data["message"]

    # 验证 B 的词没被改
    list_response = await client.get(
        "/api/learning/vocabulary?page_size=100",
        headers=auth_headers
    )
    items = list_response.json()["items"]
    other_item = next((i for i in items if i["word"] == "other_user_word"), None)
    assert other_item is None  # A 看不到 B 的词

    # 单独验证 B 的词没改 (用 B 的 auth)
    from app.services.auth import create_access_token
    b_token = create_access_token(data={"sub": str(other_user.id)})
    b_headers = {"Authorization": f"Bearer {b_token}"}

    b_list = await client.get(
        "/api/learning/vocabulary?page_size=100",
        headers=b_headers
    )
    b_items = b_list.json()["items"]
    b_word = next(i for i in b_items if i["word"] == "other_user_word")
    assert b_word["mastered"] is False  # 未被 A 修改