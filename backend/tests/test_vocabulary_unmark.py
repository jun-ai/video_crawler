"""
Batch 5 P0-1: 取消掌握 (unmark) 端点

后端 /learning/vocabulary/{id}/unmaster 加端点:
- 设置 mastered=False
- 保留 SM-2 字段 (next_review_at / ease_factor / interval_days 等)
- 跨用户隔离
"""
import pytest
from app.models.models import Material, Vocabulary


@pytest.mark.asyncio
async def test_unmark_vocabulary_sets_false(
    client, auth_headers, db_session, test_user
):
    """PUT /unmaster 设置 mastered=False"""
    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Vocabulary(
        user_id=test_user.id, material_id=1, word="mastered",
        review_count=5, mastered=True
    ))
    await db_session.commit()

    # 找一个真实的 vocab id
    from sqlalchemy import select
    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.word == "mastered")
    )
    vocab = result.scalar_one()
    vocab_id = vocab.id

    response = await client.put(
        f"/api/learning/vocabulary/{vocab_id}/unmaster",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 验证 mastered 已翻转
    await db_session.refresh(vocab)
    assert vocab.mastered is False
    # SM-2 字段保留
    assert vocab.review_count == 5  # 历史保留


@pytest.mark.asyncio
async def test_unmark_vocabulary_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """B 用户的 vocab 用 A 的 token unmark → 404"""
    from app.models.models import User
    from app.services.auth import get_password_hash
    from sqlalchemy import select

    other = User(
        username="otherunmark",
        phone="13800139999",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)

    db_session.add(Material(id=2, title="V2", duration=10,
                            video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"))
    db_session.add(Vocabulary(
        user_id=other.id, material_id=2, word="other_mastered",
        review_count=3, mastered=True
    ))
    await db_session.commit()

    result = await db_session.execute(
        select(Vocabulary).where(Vocabulary.word == "other_mastered")
    )
    other_vocab = result.scalar_one()
    other_id = other_vocab.id

    response = await client.put(
        f"/api/learning/vocabulary/{other_id}/unmaster",
        headers=auth_headers
    )
    assert response.status_code == 404

    # 验证 B 的 vocab 未变
    await db_session.refresh(other_vocab)
    assert other_vocab.mastered is True


@pytest.mark.asyncio
async def test_unmark_vocabulary_404(
    client, auth_headers, db_session, test_user
):
    """不存在的 vocab id → 404"""
    response = await client.put(
        "/api/learning/vocabulary/99999/unmaster",
        headers=auth_headers
    )
    assert response.status_code == 404