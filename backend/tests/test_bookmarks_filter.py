"""
Batch 4 P1-4: Favorites 搜索 + 按视频筛选

后端 /bookmarks/all 加 search + material_id 参数:
- search: 字幕 text_en/text_cn 模糊匹配 (ilike)
- material_id: 按视频 ID 严格匹配
"""
import pytest


@pytest.mark.asyncio
async def test_bookmarks_all_no_filters_returns_all(
    client, auth_headers, db_session, test_user
):
    """不传参数返回全部 (向后兼容)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    m1 = Material(id=1, title="Vid1", duration=10,
                  video_path="/v1.mp4", subtitle_path="/s1.srt", cover_path="/c1.jpg")
    m2 = Material(id=2, title="Vid2", duration=10,
                  video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg")
    db_session.add_all([m1, m2])
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="Hello world", text_cn="你好世界"),
        Subtitle(id=2, material_id=2, sequence=1, start_time=0, end_time=5, text_en="Good morning", text_cn="早上好"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=2, subtitle_id=2),
    ])
    await db_session.commit()

    response = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_bookmarks_all_search_english(
    client, auth_headers, db_session, test_user
):
    """search 匹配 text_en"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5,
                 text_en="Hello beautiful world", text_cn="你好世界"),
        Subtitle(id=2, material_id=1, sequence=2, start_time=5, end_time=10,
                 text_en="Good morning", text_cn="早上好"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=2),
    ])
    await db_session.commit()

    response = await client.get("/api/learning/bookmarks/all?search=beautiful", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert "beautiful" in items[0]["subtitle_text_en"]


@pytest.mark.asyncio
async def test_bookmarks_all_search_chinese(
    client, auth_headers, db_session, test_user
):
    """search 匹配 text_cn (中文)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5,
                 text_en="Hello", text_cn="你好"),
        Subtitle(id=2, material_id=1, sequence=2, start_time=5, end_time=10,
                 text_en="Morning", text_cn="早上好"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=2),
    ])
    await db_session.commit()

    response = await client.get("/api/learning/bookmarks/all?search=早上", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["subtitle_text_cn"] == "早上好"


@pytest.mark.asyncio
async def test_bookmarks_all_filter_by_material(
    client, auth_headers, db_session, test_user
):
    """material_id 严格筛选"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add_all([
        Material(id=1, title="V1", duration=10, video_path="/v1.mp4", subtitle_path="/s1.srt", cover_path="/c1.jpg"),
        Material(id=2, title="V2", duration=10, video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"),
    ])
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A", text_cn="A"),
        Subtitle(id=2, material_id=2, sequence=1, start_time=0, end_time=5, text_en="B", text_cn="B"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=2, subtitle_id=2),
    ])
    await db_session.commit()

    response = await client.get("/api/learning/bookmarks/all?material_id=1", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["material_id"] == 1
    assert items[0]["material_title"] == "V1"


@pytest.mark.asyncio
async def test_bookmarks_all_search_and_material_combined(
    client, auth_headers, db_session, test_user
):
    """search + material_id 可组合 (AND)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add_all([
        Material(id=1, title="V1", duration=10, video_path="/v1.mp4", subtitle_path="/s1.srt", cover_path="/c1.jpg"),
        Material(id=2, title="V2", duration=10, video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"),
    ])
    db_session.add_all([
        Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="apple", text_cn="苹果"),
        Subtitle(id=2, material_id=2, sequence=1, start_time=0, end_time=5, text_en="banana apple", text_cn="香蕉苹果"),
    ])
    db_session.add_all([
        SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1),
        SubtitleBookmark(user_id=test_user.id, material_id=2, subtitle_id=2),
    ])
    await db_session.commit()

    # 搜 apple 但只来自 V1 → 只返回 subtitle 1
    response = await client.get("/api/learning/bookmarks/all?search=apple&material_id=1",
                                 headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["subtitle_text_en"] == "apple"