"""
Batch 4 P1-3: Vocabulary 新词独立筛选

前端加第 4 个 chip '新词' (review_count=0), 跟 '学习中'/'已掌握' 并列。
之前 vocab-learning 和 vocab-new 合并到 '学习中', 用户无法区分。

后端: GET /learning/vocabulary 加 is_new: bool 参数
前端: filterStatus string ('all'/'learning'/'mastered'/'new')
"""
import pytest


@pytest.mark.asyncio
async def test_vocabulary_filter_is_new_true(
    client, auth_headers, db_session, test_user
):
    """is_new=true 只返回 review_count=0 的新词"""
    from app.models.models import Vocabulary

    db_session.add(Vocabulary(user_id=test_user.id, word="new1", review_count=0))
    db_session.add(Vocabulary(user_id=test_user.id, word="new2", review_count=0))
    db_session.add(Vocabulary(user_id=test_user.id, word="reviewed1", review_count=3))
    db_session.add(Vocabulary(user_id=test_user.id, word="reviewed2", review_count=10))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_new=true&page_size=50",
        headers=auth_headers
    )
    assert response.status_code == 200
    items = response.json()["items"]
    words = {item["word"] for item in items}
    assert words == {"new1", "new2"}, f"expected only new words, got {words}"
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_vocabulary_filter_is_new_false(
    client, auth_headers, db_session, test_user
):
    """is_new=false 只返回 review_count>0 的已复习词"""
    from app.models.models import Vocabulary

    db_session.add(Vocabulary(user_id=test_user.id, word="new1", review_count=0))
    db_session.add(Vocabulary(user_id=test_user.id, word="reviewed1", review_count=3))
    db_session.add(Vocabulary(user_id=test_user.id, word="reviewed2", review_count=10))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?is_new=false&page_size=50",
        headers=auth_headers
    )
    assert response.status_code == 200
    items = response.json()["items"]
    words = {item["word"] for item in items}
    assert words == {"reviewed1", "reviewed2"}, f"expected only reviewed, got {words}"


@pytest.mark.asyncio
async def test_vocabulary_filter_combined_mastered_and_is_new(
    client, auth_headers, db_session, test_user
):
    """mastered + is_new 可组合 (AND 关系)"""
    from app.models.models import Vocabulary

    db_session.add(Vocabulary(user_id=test_user.id, word="m_new", mastered=True, review_count=0))
    db_session.add(Vocabulary(user_id=test_user.id, word="m_reviewed", mastered=True, review_count=5))
    db_session.add(Vocabulary(user_id=test_user.id, word="l_new", mastered=False, review_count=0))
    await db_session.commit()

    # mastered=true AND is_new=true -> 只 m_new
    response = await client.get(
        "/api/learning/vocabulary?mastered=true&is_new=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    words = {item["word"] for item in response.json()["items"]}
    assert words == {"m_new"}


@pytest.mark.asyncio
async def test_vocabulary_filter_no_is_new_returns_all(
    client, auth_headers, db_session, test_user
):
    """不传 is_new 返回全部 (新词+复习过的)"""
    from app.models.models import Vocabulary

    db_session.add(Vocabulary(user_id=test_user.id, word="new1", review_count=0))
    db_session.add(Vocabulary(user_id=test_user.id, word="reviewed1", review_count=3))
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?page_size=50",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 2