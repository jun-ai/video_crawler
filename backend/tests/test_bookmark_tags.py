"""
Batch 5 P1-2: 字幕收藏用户标签 (Favorites-analysis.md P1-2)

后端:
- 新增 UserTag model (user_id + name 唯一, color, created_at)
- 新增 BookmarkTag 关联表 (bookmark_id + user_tag_id 复合主键)
- alembic migration: fb4a4d1_usertags
- GET /learning/bookmark-tags — 列出当前用户所有标签 + 使用次数
- POST /learning/bookmark-tags — 创建新标签 (同 user_id + name 唯一 → 409)
- DELETE /learning/bookmark-tags/{tag_id} — 删除 (用户隔离, 级联删关联)
- PUT /learning/bookmarks/{id}/tags — 设置标签 (replace-all, auto-create)
- GET /learning/bookmarks/all 响应含 tags

设计:
- UserTag 与全局 Tag (material 维度) 区分 — 用户自有的收藏维度标签
- 多对多: 一个 bookmark 可有多个标签, 一个标签可被多个 bookmark 使用
- API 按 name 操作 (前端不关心 tag_id), 后端 auto-create
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import UserTag, BookmarkTag, SubtitleBookmark


@pytest.fixture
async def bookmark_for_user(client, auth_headers, db_session, test_user):
    """创建一个测试用的 bookmark (当前用户, 带 Material + Subtitle 让 /all JOIN 能命中)"""
    from app.models.models import Material, Subtitle
    mat = Material(
        id=99800, title="Tag测试视频", duration=60,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99800, material_id=99800, sequence=1,
        text_en="test english", text_cn="测试中文",
        start_time=1000, end_time=2000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id,
        material_id=99800,
        subtitle_id=99800,
        note="test note"
    )
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)
    return bm


@pytest.fixture
async def bookmark_for_other_user(db_session, test_user):
    """创建另一个用户的 bookmark (用于隔离测试, 带 Material + Subtitle)"""
    from app.models.models import User, Material, Subtitle
    other = User(username="other_user_tags", phone="13900000099", password_hash="x")
    db_session.add(other)
    await db_session.flush()  # 拿到 other.id
    mat = Material(
        id=99801, title="别人视频", duration=60,
        video_path="/y.mp4", subtitle_path="/y.srt", cover_path="/y.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99801, material_id=99801, sequence=1,
        text_en="other", text_cn="别的",
        start_time=1000, end_time=2000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=other.id,
        material_id=99801,
        subtitle_id=99801,
    )
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)
    return bm, other


# ==================== Tag CRUD ====================

@pytest.mark.asyncio
async def test_list_tags_empty(client, auth_headers):
    """空用户 GET /bookmark-tags 返回空数组"""
    res = await client.get("/api/learning/bookmark-tags", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_create_tag_success(client, auth_headers):
    """POST /bookmark-tags 创建成功, 返回 201"""
    res = await client.post("/api/learning/bookmark-tags", json={"name": "语法"}, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "语法"
    assert data["color"] == "#5c6ef5"
    assert data["usage_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_tag_duplicate_409(client, auth_headers):
    """同名 tag 第二次创建 → 409"""
    await client.post("/api/learning/bookmark-tags", json={"name": "重点"}, headers=auth_headers)
    res = await client.post("/api/learning/bookmark-tags", json={"name": "重点"}, headers=auth_headers)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_create_tag_empty_name_400(client, auth_headers):
    """空 name → 400"""
    res = await client.post("/api/learning/bookmark-tags", json={"name": "  "}, headers=auth_headers)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_tag_cross_user_same_name_ok(client, auth_headers, db_session):
    """跨用户同名允许 (每个用户有自己的 tag 池)"""
    from app.models.models import User
    other = User(username="other_dup", phone="13900000098", password_hash="x")
    db_session.add(other)
    await db_session.flush()  # 拿到 other.id
    other_tag = UserTag(user_id=other.id, name="重点")
    db_session.add(other_tag)
    await db_session.commit()

    # 当前用户也能创建同名
    res = await client.post("/api/learning/bookmark-tags", json={"name": "重点"}, headers=auth_headers)
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_delete_tag_success(client, auth_headers, db_session, test_user):
    """DELETE /bookmark-tags/{id} 成功"""
    tag = UserTag(user_id=test_user.id, name="要删的")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    res = await client.delete(f"/api/learning/bookmark-tags/{tag.id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_delete_tag_cross_user_404(client, auth_headers, db_session):
    """删除别人的 tag → 404"""
    from app.models.models import User
    other = User(username="other_del", phone="13900000097", password_hash="x")
    db_session.add(other)
    await db_session.flush()  # 拿到 other.id
    other_tag = UserTag(user_id=other.id, name="别人的")
    db_session.add(other_tag)
    await db_session.commit()
    await db_session.refresh(other_tag)

    res = await client.delete(f"/api/learning/bookmark-tags/{other_tag.id}", headers=auth_headers)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_cascade_removes_links(client, auth_headers, db_session, test_user, bookmark_for_user):
    """删 tag 时级联删除 bookmark_tag 关联 (ondelete=CASCADE)"""
    tag = UserTag(user_id=test_user.id, name="级联测试")
    db_session.add(tag)
    await db_session.flush()
    link = BookmarkTag(bookmark_id=bookmark_for_user.id, user_tag_id=tag.id)
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(tag)

    res = await client.delete(f"/api/learning/bookmark-tags/{tag.id}", headers=auth_headers)
    assert res.status_code == 200

    # 验证 bookmark_tag 关联已删
    from sqlalchemy import select
    leftover = await db_session.execute(
        select(BookmarkTag).where(BookmarkTag.user_tag_id == tag.id)
    )
    assert leftover.scalars().first() is None


# ==================== Set bookmark tags ====================

@pytest.mark.asyncio
async def test_set_bookmark_tags_auto_create(client, auth_headers, bookmark_for_user):
    """PUT /bookmarks/{id}/tags 自动创建不存在的 tag"""
    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["生词", "语法", "重点"]},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # 验证 tag 创建
    res2 = await client.get("/api/learning/bookmark-tags", headers=auth_headers)
    names = {t["name"] for t in res2.json()}
    assert {"生词", "语法", "重点"}.issubset(names)


@pytest.mark.asyncio
async def test_set_bookmark_tags_usage_count(client, auth_headers, bookmark_for_user):
    """设置后 GET /bookmark-tags usage_count 正确"""
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["数一数"]},
        headers=auth_headers
    )
    res = await client.get("/api/learning/bookmark-tags", headers=auth_headers)
    tag = next(t for t in res.json() if t["name"] == "数一数")
    assert tag["usage_count"] == 1


@pytest.mark.asyncio
async def test_set_bookmark_tags_replace_all(client, auth_headers, bookmark_for_user):
    """第二次 PUT 替换 (replace-all 语义), 旧 tag 解除关联"""
    # 第一次: 加 "A" "B"
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["AAA", "BBB"]},
        headers=auth_headers
    )
    # 第二次: 只留 "A"
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["AAA"]},
        headers=auth_headers
    )
    # 验证 /bookmarks/all 响应里只有 AAA
    res = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    bm = next(b for b in res.json() if b["id"] == bookmark_for_user.id)
    names = {t["name"] for t in bm["tags"]}
    assert names == {"AAA"}


@pytest.mark.asyncio
async def test_set_bookmark_tags_empty_clears(client, auth_headers, bookmark_for_user):
    """PUT 空 tag_names 清空所有标签"""
    # 先加
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["要清空的"]},
        headers=auth_headers
    )
    # 再清空
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": []},
        headers=auth_headers
    )
    res = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    bm = next(b for b in res.json() if b["id"] == bookmark_for_user.id)
    assert bm["tags"] == []


@pytest.mark.asyncio
async def test_set_bookmark_tags_dedup(client, auth_headers, bookmark_for_user):
    """重复的 tag_names 自动去重"""
    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["重复", "重复", "重复"]},
        headers=auth_headers
    )
    assert res.status_code == 200

    res2 = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    bm = next(b for b in res2.json() if b["id"] == bookmark_for_user.id)
    assert len(bm["tags"]) == 1


@pytest.mark.asyncio
async def test_set_bookmark_tags_cross_user_404(client, auth_headers, bookmark_for_other_user):
    """PUT 别人的 bookmark → 404"""
    bm, _ = bookmark_for_other_user
    res = await client.put(
        f"/api/learning/bookmarks/{bm.id}/tags",
        json={"tag_names": ["越权"]},
        headers=auth_headers
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_set_bookmark_tags_strips_whitespace(client, auth_headers, bookmark_for_user):
    """tag_names 中的空白被 strip"""
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["  带空格  ", "正常"]},
        headers=auth_headers
    )
    res = await client.get("/api/learning/bookmark-tags", headers=auth_headers)
    names = {t["name"] for t in res.json()}
    assert "带空格" in names
    assert "正常" in names
    assert "  带空格  " not in names


# ==================== /bookmarks/all 含 tags ====================

@pytest.mark.asyncio
async def test_bookmarks_all_includes_tags(client, auth_headers, bookmark_for_user):
    """GET /bookmarks/all 响应含 tags 数组"""
    await client.put(
        f"/api/learning/bookmarks/{bookmark_for_user.id}/tags",
        json={"tag_names": ["验证"]},
        headers=auth_headers
    )
    res = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    bm = next(b for b in res.json() if b["id"] == bookmark_for_user.id)
    assert isinstance(bm["tags"], list)
    assert len(bm["tags"]) == 1
    assert bm["tags"][0]["name"] == "验证"
    assert "color" in bm["tags"][0]
