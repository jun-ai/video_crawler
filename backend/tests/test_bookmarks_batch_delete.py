"""
Batch 4 P1-5: Favorites 批量删除字幕收藏

后端 POST /learning/bookmarks/batch-delete 接受 ids 数组, 单次删多个
权限: 仅删当前用户自己的 (user_id 隔离, 防越权)

测试覆盖:
- 正常批量删 (3 项)
- 空数组返回 success=false
- 不存在的 id 跳过
- 跨用户隔离 (A 用户不能删 B 用户的收藏)
"""
import pytest


@pytest.mark.asyncio
async def test_batch_delete_removes_multiple(
    client, auth_headers, db_session, test_user
):
    """批量删除 3 项"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"),
        Subtitle(id=2, material_id=1, sequence=2, start_time=5, end_time=10, text_en="B"),
        Subtitle(id=3, material_id=1, sequence=3, start_time=10, end_time=15, text_en="C"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=2),
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=3),
    ])
    await db_session.commit()

    ids = [1, 2, 3]
    response = await client.post(
        "/api/learning/bookmarks/batch-delete",
        json={"ids": ids},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "3 项" in data["message"]

    # 验证 DB 全部删了
    from sqlalchemy import select, func
    count_result = await db_session.execute(
        select(func.count(SubtitleBookmark.id))
        .where(SubtitleBookmark.user_id == test_user.id)
    )
    assert count_result.scalar() == 0


@pytest.mark.asyncio
async def test_batch_delete_empty_ids_returns_false(
    client, auth_headers
):
    """空 ids 数组返回 success=false"""
    response = await client.post(
        "/api/learning/bookmarks/batch-delete",
        json={"ids": []},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_batch_delete_nonexistent_ids_skipped(
    client, auth_headers, db_session, test_user
):
    """不存在的 id 跳过, 只删存在的"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    db_session.add(SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1))
    await db_session.commit()

    response = await client.post(
        "/api/learning/bookmarks/batch-delete",
        json={"ids": [1, 999, 888]},  # 999/888 不存在
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "1 项" in data["message"]


@pytest.mark.asyncio
async def test_batch_delete_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """A 用户不能删 B 用户的收藏 (越权防护)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark, User
    from app.services.auth import get_password_hash

    # 创建另一个用户
    other_user = User(
        username="otheruser",
        phone="13900139000",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)  # 拿 ID
    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    db_session.add(SubtitleBookmark(user_id=other_user.id, material_id=1, subtitle_id=1))
    await db_session.commit()

    # A 用户尝试删 B 用户的收藏
    response = await client.post(
        "/api/learning/bookmarks/batch-delete",
        json={"ids": [1]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "0 项" in data["message"]  # 一个都没删

    # B 用户的收藏还在
    from sqlalchemy import select
    rs = await db_session.execute(
        select(SubtitleBookmark).where(SubtitleBookmark.user_id == other_user.id)
    )
    assert len(rs.scalars().all()) == 1


@pytest.mark.asyncio
async def test_batch_delete_partial_ownership(
    client, auth_headers, db_session, test_user
):
    """混合: A 自己的 + B 用户的, 只删自己的"""
    from app.models.models import Material, Subtitle, SubtitleBookmark, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="otheruser2",
        phone="13900139001",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)  # 拿 ID
    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"),
        Subtitle(id=2, material_id=1, sequence=2, start_time=5, end_time=10, text_en="B"),
    ])
    db_session.add_all([
        SubtitleBookmark(id=1, user_id=test_user.id, material_id=1, subtitle_id=1),  # A 自己的
        SubtitleBookmark(id=2, user_id=other_user.id, material_id=1, subtitle_id=2),  # B 的
    ])
    await db_session.commit()

    response = await client.post(
        "/api/learning/bookmarks/batch-delete",
        json={"ids": [1, 2]},  # 尝试全删
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "1 项" in data["message"]  # 只删 1 个

    # 验证: A 自己的删了, B 的还在
    from sqlalchemy import select
    rs_a = await db_session.execute(
        select(SubtitleBookmark).where(SubtitleBookmark.user_id == test_user.id)
    )
    rs_b = await db_session.execute(
        select(SubtitleBookmark).where(SubtitleBookmark.user_id == other_user.id)
    )
    assert len(rs_a.scalars().all()) == 0
    assert len(rs_b.scalars().all()) == 1