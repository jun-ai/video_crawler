"""
Batch 5 P1-3: 词汇 is_due 待复习筛选

后端 /learning/vocabulary 加 is_due 参数:
- is_due=True: next_review_at 不为空 + <= now + 未 mastered
- is_due=False: 已复习过 + next_review_at 为空 或 > now

测试覆盖:
- is_due=true: 返回到期 + 未掌握的
- is_due=false: 返回未到期的 (包括未复习过的)
- 排除 mastered (已掌握的不算待复习)
- 跨用户隔离
"""
from datetime import datetime, timezone, timedelta
import pytest


@pytest.mark.asyncio
async def test_vocabulary_filter_due_true(
    client, auth_headers, db_session, test_user
):
    """is_due=true: 返回到期 + 未掌握"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    now = datetime.now(timezone.utc)
    past = now - timedelta(days=1)  # 已到期
    future = now + timedelta(days=3)  # 未到期

    db_session.add_all([
        # 1. 到期 + 未掌握 (应包含)
        Vocabulary(user_id=test_user.id, material_id=1, word="due1",
                   review_count=1, next_review_at=past, mastered=False),
        # 2. 到期 + 已掌握 (应排除, 已掌握不算)
        Vocabulary(user_id=test_user.id, material_id=1, word="due_mastered",
                   review_count=2, next_review_at=past, mastered=True),
        # 3. 未到期 + 未掌握 (应排除)
        Vocabulary(user_id=test_user.id, material_id=1, word="future1",
                   review_count=1, next_review_at=future, mastered=False),
        # 4. next_review_at 为空 + 未掌握 (应排除, 没复习过)
        Vocabulary(user_id=test_user.id, material_id=1, word="new1",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_due=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    words = [item["word"] for item in data["items"]]
    assert "due1" in words
    assert "due_mastered" not in words
    assert "future1" not in words
    assert "new1" not in words


@pytest.mark.asyncio
async def test_vocabulary_filter_due_false(
    client, auth_headers, db_session, test_user
):
    """is_due=false: 返回未到期 (含新词)"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    now = datetime.now(timezone.utc)
    past = now - timedelta(days=1)
    future = now + timedelta(days=3)

    db_session.add_all([
        Vocabulary(user_id=test_user.id, material_id=1, word="due1",
                   review_count=1, next_review_at=past, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="future1",
                   review_count=1, next_review_at=future, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="new1",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_due=false",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    words = [item["word"] for item in data["items"]]
    assert "due1" not in words
    assert "future1" in words
    assert "new1" in words


@pytest.mark.asyncio
async def test_vocabulary_due_excludes_mastered(
    client, auth_headers, db_session, test_user
):
    """已掌握 + 已到期 -> 不算待复习 (语义: 已掌握永久免复习)"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    past = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(Vocabulary(
        user_id=test_user.id, material_id=1, word="mastered_past",
        review_count=5, next_review_at=past, mastered=True
    ))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_due=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    words = [item["word"] for item in response.json()["items"]]
    assert "mastered_past" not in words


@pytest.mark.asyncio
async def test_vocabulary_due_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """跨用户: B 用户的到期生词不会出现在 A 用户的待复习"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="otherdue",
        phone="13800139998",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    past = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(Vocabulary(
        user_id=other_user.id, material_id=1, word="other_due",
        review_count=1, next_review_at=past, mastered=False
    ))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_due=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    words = [item["word"] for item in response.json()["items"]]
    assert "other_due" not in words