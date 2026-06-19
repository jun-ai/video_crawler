"""P2-4: bookmark.last_practiced_at + /bookmarks/all 返回 material_cover"""
import pytest
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_increment_practice_sets_last_practiced_at(
    client, auth_headers, db_session, test_user
):
    """调 /practice 端点后, bookmark.last_practiced_at 应被设置"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    mat = Material(
        id=99500, title="M", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99500, material_id=99500, sequence=1,
        text_en="hi", start_time=0, end_time=1000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id, material_id=99500, subtitle_id=99500,
    )
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    # 初始状态: last_practiced_at 应为 None
    assert bm.last_practiced_at is None
    assert bm.practice_count == 0

    # 调练习端点
    resp = await client.post(
        f"/api/learning/bookmarks/{bm.id}/practice",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    # 验证
    await db_session.refresh(bm)
    assert bm.practice_count == 1
    assert bm.last_practiced_at is not None
    # SQLite 可能返回 naive datetime, 兼容两种
    last_time = bm.last_practiced_at
    now = datetime.now(timezone.utc)
    if last_time.tzinfo is None:
        last_time = last_time.replace(tzinfo=timezone.utc)
    diff = abs((now - last_time).total_seconds())
    assert diff < 5, f"last_practiced_at 偏差 {diff}s 太大"


@pytest.mark.asyncio
async def test_increment_practice_updates_last_practiced_at_each_time(
    client, auth_headers, db_session, test_user
):
    """连续 2 次调用 practice, last_practiced_at 应随之更新"""
    from app.models.models import Material, Subtitle, SubtitleBookmark
    import asyncio

    mat = Material(
        id=99400, title="M", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99400, material_id=99400, sequence=1,
        text_en="hi", start_time=0, end_time=1000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id, material_id=99400, subtitle_id=99400,
    )
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    # 第 1 次
    resp = await client.post(
        f"/api/learning/bookmarks/{bm.id}/practice",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    await db_session.refresh(bm)
    first_time = bm.last_practiced_at
    assert first_time is not None
    assert bm.practice_count == 1

    # 等 50ms 保证时间戳可分辨
    await asyncio.sleep(0.05)

    # 第 2 次
    resp = await client.post(
        f"/api/learning/bookmarks/{bm.id}/practice",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    await db_session.refresh(bm)
    second_time = bm.last_practiced_at
    assert second_time is not None
    assert bm.practice_count == 2
    # 第二次应 >= 第一次
    assert second_time >= first_time


@pytest.mark.asyncio
async def test_get_all_bookmarks_returns_material_cover(
    client, auth_headers, db_session, test_user
):
    """/bookmarks/all 响应应包含 material_cover (来自 material.cover_path)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    mat = Material(
        id=99300, title="M", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt",
        cover_path="/covers/test-cover.jpg",  # 真实路径, 端点应转换为 URL
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99300, material_id=99300, sequence=1,
        text_en="hi", start_time=0, end_time=1000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id, material_id=99300, subtitle_id=99300,
    )
    db_session.add(bm)
    await db_session.commit()

    resp = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert "material_cover" in item, "响应应包含 material_cover 字段"
    # 应是 file_url 转换后的字符串 (含 /covers/test-cover.jpg 路径)
    assert item["material_cover"] is not None
    assert "test-cover.jpg" in item["material_cover"]


@pytest.mark.asyncio
async def test_get_all_bookmarks_response_includes_last_practiced_at(
    client, auth_headers, db_session, test_user
):
    """/bookmarks/all 响应应包含 last_practiced_at 字段 (None 或时间戳)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    mat = Material(
        id=99200, title="M", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99200, material_id=99200, sequence=1,
        text_en="hi", start_time=0, end_time=1000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id, material_id=99200, subtitle_id=99200,
        practice_count=2,
    )
    db_session.add(bm)
    await db_session.commit()

    resp = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    # 字段应存在 (允许 None, 因为还没练习过)
    assert "last_practiced_at" in item
    assert item["last_practiced_at"] is None
