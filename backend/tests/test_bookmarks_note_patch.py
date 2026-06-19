"""
Batch 5 P1-2: Favorites 笔记功能 (后端 PATCH)

后端 PATCH /learning/bookmarks/{id} 接受 {note}, 允许编辑字幕收藏笔记。
权限: 仅自己的收藏 (user_id 隔离, 防越权)

测试覆盖:
- 编辑笔记 (200, 笔记内容持久化)
- 清空笔记 (空字符串 -> null)
- 不存在的 id (404)
- 跨用户越权 (改别人笔记 -> 404)
- 不传 note (no-op)
"""
import pytest


@pytest.mark.asyncio
async def test_update_bookmark_note(
    client, auth_headers, db_session, test_user
):
    """编辑笔记 (200, 持久化)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    bm = SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1, note=None)
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    response = await client.patch(
        f"/api/learning/bookmarks/{bm.id}",
        json={"note": "这句很扎心, 收藏"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["note"] == "这句很扎心, 收藏"

    # 验证 DB 持久化
    await db_session.refresh(bm)
    assert bm.note == "这句很扎心, 收藏"


@pytest.mark.asyncio
async def test_update_bookmark_clear_note(
    client, auth_headers, db_session, test_user
):
    """清空笔记 (空字符串 -> null)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    bm = SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1,
                          note="已有笔记")
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    response = await client.patch(
        f"/api/learning/bookmarks/{bm.id}",
        json={"note": ""},
        headers=auth_headers
    )
    assert response.status_code == 200
    # 空字符串 -> None
    await db_session.refresh(bm)
    assert bm.note is None


@pytest.mark.asyncio
async def test_update_bookmark_nonexistent_returns_404(
    client, auth_headers
):
    """不存在的 id -> 404"""
    response = await client.patch(
        "/api/learning/bookmarks/99999",
        json={"note": "test"},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_bookmark_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """改别人笔记 -> 404 (越权防护)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="othernote",
        phone="13800139999",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    bm = SubtitleBookmark(user_id=other_user.id, material_id=1, subtitle_id=1,
                          note="别人的笔记")
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    # A 用户尝试改 B 用户的笔记
    response = await client.patch(
        f"/api/learning/bookmarks/{bm.id}",
        json={"note": "hack"},
        headers=auth_headers
    )
    assert response.status_code == 404

    # 别人笔记没变
    await db_session.refresh(bm)
    assert bm.note == "别人的笔记"


@pytest.mark.asyncio
async def test_update_bookmark_noop_when_note_omitted(
    client, auth_headers, db_session, test_user
):
    """不传 note -> 笔记不变 (no-op)"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))
    db_session.add(Subtitle(id=1, material_id=1, sequence=1, start_time=0, end_time=5, text_en="A"))
    bm = SubtitleBookmark(user_id=test_user.id, material_id=1, subtitle_id=1,
                          note="原笔记")
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)

    response = await client.patch(
        f"/api/learning/bookmarks/{bm.id}",
        json={},  # 不传 note
        headers=auth_headers
    )
    assert response.status_code == 200
    await db_session.refresh(bm)
    assert bm.note == "原笔记"