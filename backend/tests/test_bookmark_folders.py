"""
Batch 5 P1-2 (后缀): 字幕收藏文件夹 (Favorites-analysis.md P1-2 文件夹)

后端:
- 新增 BookmarkFolder model (user_id + name 唯一, color, icon, sort_order)
- subtitle_bookmarks 加 folder_id 列 (nullable FK, ondelete=SET NULL)
- alembic migration: d7a8e2f_bookmarkfolders
- GET /learning/bookmark-folders — 列出当前用户所有文件夹 + bookmark_count
- POST /learning/bookmark-folders — 创建文件夹 (409 重名)
- PATCH /learning/bookmark-folders/{id} — 更新 (重命名/换色/调排序)
- DELETE /learning/bookmark-folders/{id} — 删除 (级联 SET NULL 保留 bookmark)
- PUT /learning/bookmarks/{id}/folder — 移动单个 bookmark 到文件夹 (folder_id=null 移出)
- POST /learning/bookmarks/batch-move-folder — 批量移动
- /bookmarks/all 响应含 folder_id/folder_name/folder_color + folder_id 过滤

设计:
- 与 UserTag (多对多标签) 区分, BookmarkFolder 是 1:N 容器
- 一个 bookmark 只能属于一个 folder (或不属于)
- 删 folder 时 bookmark 变 "未分类" (SET NULL), 不级联删 bookmark
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import BookmarkFolder, SubtitleBookmark, User


@pytest.fixture
async def bookmark_for_folder_user(client, auth_headers, db_session, test_user):
    """创建测试用的 bookmark (当前用户, 带 Material + Subtitle 让 /all JOIN 能命中)"""
    from app.models.models import Material, Subtitle
    mat = Material(
        id=99900, title="文件夹测试视频", duration=60,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99900, material_id=99900, sequence=1,
        text_en="folder test english", text_cn="文件夹测试中文",
        start_time=1000, end_time=2000,
    )
    db_session.add(sub)
    bm = SubtitleBookmark(
        user_id=test_user.id,
        material_id=99900,
        subtitle_id=99900,
        note="folder test note"
    )
    db_session.add(bm)
    await db_session.commit()
    await db_session.refresh(bm)
    return bm


@pytest.fixture
async def other_user_folder(db_session):
    """创建另一个用户的文件夹 (用于隔离测试)"""
    other = User(username="other_folder_user", phone="13900000080", password_hash="x")
    db_session.add(other)
    await db_session.flush()
    folder = BookmarkFolder(user_id=other.id, name="别人的文件夹")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)
    return folder, other


# ==================== Folder CRUD ====================

@pytest.mark.asyncio
async def test_list_folders_empty(client, auth_headers):
    """空用户 GET /bookmark-folders 返回空数组"""
    res = await client.get("/api/learning/bookmark-folders", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_create_folder_success(client, auth_headers):
    """POST /bookmark-folders 创建成功 → 201"""
    res = await client.post(
        "/api/learning/bookmark-folders",
        json={"name": "商务英语", "color": "#ff6b6b"},
        headers=auth_headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "商务英语"
    assert data["color"] == "#ff6b6b"
    assert data["icon"] == "folder"
    assert data["bookmark_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_folder_default_color(client, auth_headers):
    """不传 color → 默认 #5c6ef5"""
    res = await client.post(
        "/api/learning/bookmark-folders",
        json={"name": "日常口语"},
        headers=auth_headers
    )
    assert res.status_code == 201
    assert res.json()["color"] == "#5c6ef5"


@pytest.mark.asyncio
async def test_create_folder_duplicate_409(client, auth_headers):
    """同名 folder 重复创建 → 409"""
    await client.post("/api/learning/bookmark-folders", json={"name": "重名"}, headers=auth_headers)
    res = await client.post("/api/learning/bookmark-folders", json={"name": "重名"}, headers=auth_headers)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_create_folder_empty_name_400(client, auth_headers):
    """空 name → 400"""
    res = await client.post(
        "/api/learning/bookmark-folders",
        json={"name": "  "},
        headers=auth_headers
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_folder_name_too_long_400(client, auth_headers):
    """name > 50 字符 → 400"""
    res = await client.post(
        "/api/learning/bookmark-folders",
        json={"name": "x" * 51},
        headers=auth_headers
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_create_folder_cross_user_same_name_ok(client, auth_headers, other_user_folder):
    """跨用户同名允许"""
    res = await client.post(
        "/api/learning/bookmark-folders",
        json={"name": "别人的文件夹"},
        headers=auth_headers
    )
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_list_folders_with_bookmark_count(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """GET /bookmark-folders 返回正确的 bookmark_count"""
    folder = BookmarkFolder(user_id=test_user.id, name="高数")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    # 把 bookmark 移到 folder
    bookmark_for_folder_user.folder_id = folder.id
    await db_session.commit()

    res = await client.get("/api/learning/bookmark-folders", headers=auth_headers)
    assert res.status_code == 200
    folders = res.json()
    assert len(folders) == 1
    assert folders[0]["name"] == "高数"
    assert folders[0]["bookmark_count"] == 1


@pytest.mark.asyncio
async def test_list_folders_isolated_by_user(client, auth_headers, other_user_folder):
    """别人的文件夹不返回"""
    res = await client.get("/api/learning/bookmark-folders", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


# ==================== Folder Update ====================

@pytest.mark.asyncio
async def test_update_folder_rename(client, auth_headers, db_session, test_user):
    """PATCH /bookmark-folders/{id} 改名字"""
    folder = BookmarkFolder(user_id=test_user.id, name="旧名")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    res = await client.patch(
        f"/api/learning/bookmark-folders/{folder.id}",
        json={"name": "新名"},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "新名"


@pytest.mark.asyncio
async def test_update_folder_color_icon(client, auth_headers, db_session, test_user):
    """PATCH 改 color + icon"""
    folder = BookmarkFolder(user_id=test_user.id, name="测试")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    res = await client.patch(
        f"/api/learning/bookmark-folders/{folder.id}",
        json={"color": "#22c55e", "icon": "star"},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["color"] == "#22c55e"
    assert data["icon"] == "star"


@pytest.mark.asyncio
async def test_update_folder_rename_duplicate_409(client, auth_headers, db_session, test_user):
    """改名为已存在的名字 → 409"""
    f1 = BookmarkFolder(user_id=test_user.id, name="A")
    f2 = BookmarkFolder(user_id=test_user.id, name="B")
    db_session.add_all([f1, f2])
    await db_session.commit()
    await db_session.refresh(f1)
    await db_session.refresh(f2)

    res = await client.patch(
        f"/api/learning/bookmark-folders/{f1.id}",
        json={"name": "B"},
        headers=auth_headers
    )
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_update_folder_cross_user_404(client, auth_headers, other_user_folder):
    """改别人的 folder → 404"""
    folder, _ = other_user_folder
    res = await client.patch(
        f"/api/learning/bookmark-folders/{folder.id}",
        json={"name": "hacked"},
        headers=auth_headers
    )
    assert res.status_code == 404


# ==================== Folder Delete ====================

@pytest.mark.asyncio
async def test_delete_folder_success(client, auth_headers, db_session, test_user):
    """DELETE 成功"""
    folder = BookmarkFolder(user_id=test_user.id, name="待删")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    res = await client.delete(f"/api/learning/bookmark-folders/{folder.id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_delete_folder_cascade_set_null(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """删 folder 时 bookmark.folder_id SET NULL (保留 bookmark)"""
    folder = BookmarkFolder(user_id=test_user.id, name="级联测试")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    bookmark_for_folder_user.folder_id = folder.id
    await db_session.commit()
    bookmark_id = bookmark_for_folder_user.id

    res = await client.delete(f"/api/learning/bookmark-folders/{folder.id}", headers=auth_headers)
    assert res.status_code == 200

    # 验证: bookmark 还在, folder_id 变成 null
    bm_result = await db_session.execute(
        select(SubtitleBookmark).where(SubtitleBookmark.id == bookmark_id)
    )
    bm = bm_result.scalar_one()
    assert bm is not None
    assert bm.folder_id is None


@pytest.mark.asyncio
async def test_delete_folder_cross_user_404(client, auth_headers, other_user_folder):
    """删别人的 folder → 404"""
    folder, _ = other_user_folder
    res = await client.delete(f"/api/learning/bookmark-folders/{folder.id}", headers=auth_headers)
    assert res.status_code == 404


# ==================== Move bookmark to folder ====================

@pytest.mark.asyncio
async def test_move_bookmark_to_folder(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """PUT /bookmarks/{id}/folder 移动到 folder"""
    folder = BookmarkFolder(user_id=test_user.id, name="目标文件夹")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_folder_user.id}/folder",
        json={"folder_id": folder.id},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # 验证 DB
    await db_session.refresh(bookmark_for_folder_user)
    assert bookmark_for_folder_user.folder_id == folder.id


@pytest.mark.asyncio
async def test_move_bookmark_out_of_folder(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """folder_id=null → 移出文件夹"""
    folder = BookmarkFolder(user_id=test_user.id, name="待移出")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)
    bookmark_for_folder_user.folder_id = folder.id
    await db_session.commit()

    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_folder_user.id}/folder",
        json={"folder_id": None},
        headers=auth_headers
    )
    assert res.status_code == 200

    await db_session.refresh(bookmark_for_folder_user)
    assert bookmark_for_folder_user.folder_id is None


@pytest.mark.asyncio
async def test_move_bookmark_to_invalid_folder_404(client, auth_headers, bookmark_for_folder_user):
    """移动到不存在的 folder → 404"""
    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_folder_user.id}/folder",
        json={"folder_id": 99999},
        headers=auth_headers
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_move_bookmark_cross_user_folder_404(client, auth_headers, bookmark_for_folder_user, other_user_folder):
    """移动到别人的 folder → 404 (安全)"""
    folder, _ = other_user_folder
    res = await client.put(
        f"/api/learning/bookmarks/{bookmark_for_folder_user.id}/folder",
        json={"folder_id": folder.id},
        headers=auth_headers
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_move_bookmark_cross_user_404(client, auth_headers, db_session, test_user):
    """移动别人的 bookmark → 404"""
    other = User(username="move_bm_other", phone="13900000070", password_hash="x")
    db_session.add(other)
    await db_session.flush()
    from app.models.models import Material, Subtitle
    mat = Material(id=99950, title="x", duration=60, video_path="/x", subtitle_path="/x", cover_path="/x")
    sub = Subtitle(id=99950, material_id=99950, sequence=1, text_en="x", text_cn="x", start_time=1, end_time=2)
    db_session.add_all([mat, sub])
    other_bm = SubtitleBookmark(user_id=other.id, material_id=99950, subtitle_id=99950)
    db_session.add(other_bm)
    await db_session.commit()
    await db_session.refresh(other_bm)

    res = await client.put(
        f"/api/learning/bookmarks/{other_bm.id}/folder",
        json={"folder_id": None},
        headers=auth_headers
    )
    assert res.status_code == 404


# ==================== Batch move ====================

@pytest.mark.asyncio
async def test_batch_move_success(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """POST /bookmarks/batch-move-folder 批量移动"""
    folder = BookmarkFolder(user_id=test_user.id, name="批量目标")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    # 第二个 bookmark
    from app.models.models import Material, Subtitle
    sub2 = Subtitle(id=99901, material_id=99900, sequence=2, text_en="second", text_cn="第二", start_time=3000, end_time=4000)
    db_session.add(sub2)
    bm2 = SubtitleBookmark(user_id=test_user.id, material_id=99900, subtitle_id=99901)
    db_session.add(bm2)
    await db_session.commit()
    await db_session.refresh(bm2)

    ids = [bookmark_for_folder_user.id, bm2.id]
    res = await client.post(
        "/api/learning/bookmarks/batch-move-folder",
        json={"ids": ids, "folder_id": folder.id},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "已移动 2 项" in data["message"]

    # 验证
    await db_session.refresh(bookmark_for_folder_user)
    await db_session.refresh(bm2)
    assert bookmark_for_folder_user.folder_id == folder.id
    assert bm2.folder_id == folder.id


@pytest.mark.asyncio
async def test_batch_move_out_of_folder(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """folder_id=null → 批量移出"""
    folder = BookmarkFolder(user_id=test_user.id, name="批量移出")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)
    bookmark_for_folder_user.folder_id = folder.id
    await db_session.commit()

    res = await client.post(
        "/api/learning/bookmarks/batch-move-folder",
        json={"ids": [bookmark_for_folder_user.id], "folder_id": None},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert "未分类" in res.json()["message"]

    await db_session.refresh(bookmark_for_folder_user)
    assert bookmark_for_folder_user.folder_id is None


@pytest.mark.asyncio
async def test_batch_move_empty_ids(client, auth_headers):
    """空 ids 数组 → 200 + success=False"""
    res = await client.post(
        "/api/learning/bookmarks/batch-move-folder",
        json={"ids": [], "folder_id": 1},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["success"] is False


@pytest.mark.asyncio
async def test_batch_move_isolated_by_user(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """只移动自己的 bookmark, 别人的跳过"""
    other = User(username="bm_batch_other", phone="13900000060", password_hash="x")
    db_session.add(other)
    await db_session.flush()
    from app.models.models import Material, Subtitle
    mat = Material(id=99960, title="x", duration=60, video_path="/x", subtitle_path="/x", cover_path="/x")
    sub = Subtitle(id=99960, material_id=99960, sequence=1, text_en="x", text_cn="x", start_time=1, end_time=2)
    db_session.add_all([mat, sub])
    other_bm = SubtitleBookmark(user_id=other.id, material_id=99960, subtitle_id=99960)
    db_session.add(other_bm)
    await db_session.commit()
    await db_session.refresh(other_bm)

    # 试图移动自己的 + 别人的 (应只移动自己的)
    res = await client.post(
        "/api/learning/bookmarks/batch-move-folder",
        json={"ids": [bookmark_for_folder_user.id, other_bm.id], "folder_id": None},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert "已移动 1 项" in res.json()["message"]  # 只移动 1 个


# ==================== /bookmarks/all 集成 ====================

@pytest.mark.asyncio
async def test_bookmarks_all_includes_folder_info(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """GET /bookmarks/all 响应含 folder_id/folder_name/folder_color"""
    folder = BookmarkFolder(user_id=test_user.id, name="口语积累", color="#22c55e")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)
    bookmark_for_folder_user.folder_id = folder.id
    await db_session.commit()

    res = await client.get("/api/learning/bookmarks/all", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["folder_id"] == folder.id
    assert items[0]["folder_name"] == "口语积累"
    assert items[0]["folder_color"] == "#22c55e"


@pytest.mark.asyncio
async def test_bookmarks_all_filter_by_folder(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """GET /bookmarks/all?folder_id=N 按文件夹过滤"""
    f1 = BookmarkFolder(user_id=test_user.id, name="A")
    f2 = BookmarkFolder(user_id=test_user.id, name="B")
    db_session.add_all([f1, f2])
    await db_session.commit()
    await db_session.refresh(f1)
    await db_session.refresh(f2)

    # 第二个 bookmark 放 B
    from app.models.models import Subtitle
    sub2 = Subtitle(id=99902, material_id=99900, sequence=2, text_en="b-only", text_cn="B独有的", start_time=5000, end_time=6000)
    db_session.add(sub2)
    bm2 = SubtitleBookmark(user_id=test_user.id, material_id=99900, subtitle_id=99902, folder_id=f2.id)
    db_session.add(bm2)
    bookmark_for_folder_user.folder_id = f1.id
    await db_session.commit()

    # 过滤 f1
    res = await client.get(f"/api/learning/bookmarks/all?folder_id={f1.id}", headers=auth_headers)
    items = res.json()
    assert len(items) == 1
    assert items[0]["folder_name"] == "A"

    # 过滤 f2
    res = await client.get(f"/api/learning/bookmarks/all?folder_id={f2.id}", headers=auth_headers)
    items = res.json()
    assert len(items) == 1
    assert items[0]["folder_name"] == "B"


@pytest.mark.asyncio
async def test_bookmarks_all_filter_uncategorized(client, auth_headers, db_session, test_user, bookmark_for_folder_user):
    """GET /bookmarks/all?folder_id=0 仅显示未分类 (folder_id=0 哨兵值)"""
    f1 = BookmarkFolder(user_id=test_user.id, name="已分类")
    db_session.add(f1)
    await db_session.commit()
    await db_session.refresh(f1)

    # 第一个 bookmark 放文件夹
    from app.models.models import Subtitle
    sub_categorized = Subtitle(id=99903, material_id=99900, sequence=2, text_en="cat", text_cn="已分类的", start_time=7000, end_time=8000)
    db_session.add(sub_categorized)
    bm_categorized = SubtitleBookmark(user_id=test_user.id, material_id=99900, subtitle_id=99903, folder_id=f1.id)
    db_session.add(bm_categorized)
    # bookmark_for_folder_user 保持 folder_id=None
    await db_session.commit()

    res = await client.get("/api/learning/bookmarks/all?folder_id=0", headers=auth_headers)
    items = res.json()
    assert len(items) == 1
    assert items[0]["folder_id"] is None
    assert "folder test english" in items[0]["subtitle_text_en"]
