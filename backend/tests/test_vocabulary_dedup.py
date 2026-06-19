"""
Batch 5 P2-10: 词汇查重 (加入生词本自动去重)

后端 2 个改动:
- POST /vocabulary: 同一用户已有同 word (大小写不敏感) 时, 走 update 而非新建
  - 更新 context / material_id / subtitle_id
  - mastered 状态保留 (已掌握的不会被取消)
- GET /vocabulary/check: 前端预检端点, 返回 { exists, vocabulary }

测试覆盖:
- 重复加入: 走 update 路径 (数量不变 + context 被覆盖)
- 重复加入 mastered: 不改变 mastered 状态
- 跨用户: A 用户的词不影响 B 用户查重
- 大小写不敏感: 'Hello' 和 'hello' 视为同一个词
- check 端点: exists=false (未存在) / exists=true (存在) / 空 word
"""
import pytest


@pytest.mark.asyncio
async def test_add_vocabulary_dedup_existing(
    client, auth_headers, db_session, test_user
):
    """重复加入: 走 update 路径 (数量不变 + context 被新覆盖)"""
    from app.models.models import Material, Vocabulary
    from sqlalchemy import select, func

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    # 已有 hello (context=old)
    existing = Vocabulary(user_id=test_user.id, material_id=1, word="hello",
                         context="old context", review_count=2, next_review_at=None, mastered=False)
    db_session.add(existing)
    await db_session.commit()
    await db_session.refresh(existing)
    existing_id = existing.id

    # 再次加入 hello (new context)
    response = await client.post(
        "/api/learning/vocabulary",
        json={"word": "hello", "context": "new context", "material_id": 1},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == existing_id  # 走 update, id 不变
    assert data["context"] == "new context"  # context 被覆盖

    # DB 中只有 1 条 (没有创建重复)
    count_q = select(func.count()).select_from(Vocabulary).where(
        Vocabulary.user_id == test_user.id
    )
    total = (await db_session.execute(count_q)).scalar()
    assert total == 1


@pytest.mark.asyncio
async def test_add_vocabulary_case_insensitive(
    client, auth_headers, db_session, test_user
):
    """大小写不敏感: 'Hello' / 'hello' / 'HELLO' 视为同一个词"""
    from app.models.models import Material, Vocabulary
    from sqlalchemy import select, func

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Vocabulary(user_id=test_user.id, material_id=1, word="Hello",
                             review_count=0, next_review_at=None, mastered=False))
    await db_session.commit()

    # 大写加入
    response = await client.post(
        "/api/learning/vocabulary",
        json={"word": "HELLO", "context": "from uppercase"},
        headers=auth_headers
    )
    assert response.status_code == 200

    # DB 中只有 1 条
    count_q = select(func.count()).select_from(Vocabulary).where(
        Vocabulary.user_id == test_user.id
    )
    total = (await db_session.execute(count_q)).scalar()
    assert total == 1


@pytest.mark.asyncio
async def test_add_vocabulary_preserves_mastered(
    client, auth_headers, db_session, test_user
):
    """重复加入不改变 mastered 状态 (已掌握不会被降级)"""
    from app.models.models import Material, Vocabulary
    from sqlalchemy import select

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    mastered_vocab = Vocabulary(user_id=test_user.id, material_id=1, word="jog",
                                review_count=5, next_review_at=None, mastered=True)
    db_session.add(mastered_vocab)
    await db_session.commit()
    await db_session.refresh(mastered_vocab)

    # 再次加入
    response = await client.post(
        "/api/learning/vocabulary",
        json={"word": "jog", "context": "new"},
        headers=auth_headers
    )
    assert response.status_code == 200

    # mastered 状态保持 True, review_count 不变
    q = select(Vocabulary).where(Vocabulary.id == mastered_vocab.id)
    v = (await db_session.execute(q)).scalar_one()
    assert v.mastered is True
    assert v.review_count == 5


@pytest.mark.asyncio
async def test_add_vocabulary_cross_user_no_conflict(
    client, auth_headers, db_session, test_user
):
    """跨用户: A 的词不影响 B 加入同 word"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash, create_access_token

    other_user = User(
        username="otherdedup",
        phone="13800139922",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    # B 加入 hello
    db_session.add(Vocabulary(user_id=other_user.id, material_id=1, word="hello",
                             review_count=0, next_review_at=None, mastered=False))
    await db_session.commit()

    # A 加入 hello (不应被去重到 B 的词)
    response = await client.post(
        "/api/learning/vocabulary",
        json={"word": "hello"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # A 应该创建新词, 不是返回 B 的
    assert data["user_id"] == test_user.id

    # DB 中现在应该有 2 条 (A + B 各一条)
    from sqlalchemy import select, func
    count_q = select(func.count()).select_from(Vocabulary)
    total = (await db_session.execute(count_q)).scalar()
    assert total == 2


@pytest.mark.asyncio
async def test_check_vocabulary_exists_returns_false(
    client, auth_headers, db_session, test_user
):
    """check 端点: 单词未存在时 returns { exists: False, vocabulary: null }"""
    db_session.add(__import__('app.models.models', fromlist=['Material']).Material(
        id=1, title="V", duration=10,
        video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"
    ))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary/check?word=newword",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False
    assert data["vocabulary"] is None


@pytest.mark.asyncio
async def test_check_vocabulary_exists_returns_true(
    client, auth_headers, db_session, test_user
):
    """check 端点: 单词存在时返回完整信息"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    v = Vocabulary(user_id=test_user.id, material_id=1, word="hello",
                  review_count=3, next_review_at=None, mastered=False)
    db_session.add(v)
    await db_session.commit()
    await db_session.refresh(v)

    response = await client.get(
        "/api/learning/vocabulary/check?word=hello",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is True
    assert data["vocabulary"]["id"] == v.id
    assert data["vocabulary"]["word"] == "hello"
    assert data["vocabulary"]["mastered"] is False
    assert data["vocabulary"]["review_count"] == 3


@pytest.mark.asyncio
async def test_check_vocabulary_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """check 端点: A 看不到 B 的词 (跨用户隔离)"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="othercheck",
        phone="13800139911",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Vocabulary(user_id=other_user.id, material_id=1, word="secret",
                             review_count=0, next_review_at=None, mastered=False))
    await db_session.commit()

    # A 查 'secret' 应返回 not exists
    response = await client.get(
        "/api/learning/vocabulary/check?word=secret",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False


@pytest.mark.asyncio
async def test_check_vocabulary_empty_word(client, auth_headers):
    """check 端点: 空 word 返回 not exists (不报错)"""
    response = await client.get(
        "/api/learning/vocabulary/check?word=",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False


@pytest.mark.asyncio
async def test_add_vocabulary_empty_word_rejected(
    client, auth_headers, db_session, test_user
):
    """add 端点: 空 word 返回 400"""
    from app.models.models import Material
    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    await db_session.commit()

    response = await client.post(
        "/api/learning/vocabulary",
        json={"word": "   "},
        headers=auth_headers
    )
    assert response.status_code == 400