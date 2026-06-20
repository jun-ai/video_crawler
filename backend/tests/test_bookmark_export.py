"""
Batch 5 P2 (后缀): 字幕收藏导出

端点: GET /learning/bookmarks/export?format=csv|json
参数: search / material_id / folder_id / tag_id (跟 /bookmarks/all 一致)

设计:
- csv: 默认, UTF-8 BOM, 列: english, chinese, video, video_url, start_time_sec, folder, tags, note, practice_count, last_practiced_at, created_at
- json: 完整结构 (含 id/subtitle_id/material_id, 适合迁移)
- video_url 走 Learn 页 (带 start_time 跳转)
- tags 用逗号分隔 (csv) / 列表 (json)
"""
import csv
import io
import json
import pytest


@pytest.fixture
async def export_setup(db_session, test_user):
    """3 个 bookmark + 2 tag + 1 folder, 各种数据"""
    from app.models.models import (
        Material, Subtitle, SubtitleBookmark,
        UserTag, BookmarkTag, BookmarkFolder
    )
    mat = Material(
        id=99600, title="导出测试视频", duration=300,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)

    subtitles = []
    for i, en, cn, st in [
        (1, "first sentence", "第一句", 1000),
        (2, "second sentence", "第二句", 5000),
        (3, "third sentence", "第三句", 9000),
    ]:
        sub = Subtitle(
            id=99600 + i, material_id=99600, sequence=i,
            text_en=en, text_cn=cn, start_time=st, end_time=st + 2000
        )
        db_session.add(sub)
        subtitles.append(sub)

    folder = BookmarkFolder(user_id=test_user.id, name="导出文件夹", color="#22c55e")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    tag = UserTag(user_id=test_user.id, name="重点", color="#ef4444")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    bms = []
    # bm1: in folder, with tag, with note
    bm1 = SubtitleBookmark(
        user_id=test_user.id, material_id=99600, subtitle_id=99601,
        folder_id=folder.id, note="收藏的句子"
    )
    db_session.add(bm1)
    # bm2: in folder, no tag
    bm2 = SubtitleBookmark(
        user_id=test_user.id, material_id=99600, subtitle_id=99602,
        folder_id=folder.id
    )
    db_session.add(bm2)
    # bm3: no folder, with tag
    bm3 = SubtitleBookmark(
        user_id=test_user.id, material_id=99600, subtitle_id=99603
    )
    db_session.add(bm3)
    await db_session.commit()
    for bm in [bm1, bm2, bm3]:
        await db_session.refresh(bm)

    # 关联 tag
    db_session.add(BookmarkTag(bookmark_id=bm1.id, user_tag_id=tag.id))
    db_session.add(BookmarkTag(bookmark_id=bm3.id, user_tag_id=tag.id))
    await db_session.commit()

    return {"folder": folder, "tag": tag, "bms": [bm1, bm2, bm3]}


# ==================== CSV 导出 ====================

@pytest.mark.asyncio
async def test_export_csv_default(client, auth_headers, export_setup):
    """GET /bookmarks/export 默认 csv, 含所有列"""
    res = await client.get("/api/learning/bookmarks/export", headers=auth_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment" in res.headers["content-disposition"]
    assert "filename=subtitle-bookmarks-" in res.headers["content-disposition"]
    assert ".csv" in res.headers["content-disposition"]

    # 解析 CSV (BOM 会被自动 strip, 但需要 utf-8-sig)
    content = res.content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # header + 3 个 bookmark
    assert len(rows) == 4
    header = rows[0]
    assert "english" in header
    assert "chinese" in header
    assert "video" in header
    assert "folder" in header
    assert "tags" in header
    assert "note" in header

    # 按 created_at desc 排序: bm3, bm1, bm2 (或反过来, 看 commit 时间)
    # 验证数据正确性: 找包含 "first sentence" 的行
    first_row = next(r for r in rows[1:] if "first sentence" in r[header.index("english")])
    assert "第一句" in first_row[header.index("chinese")]
    assert "导出测试视频" == first_row[header.index("video")]
    assert "导出文件夹" == first_row[header.index("folder")]
    assert "重点" == first_row[header.index("tags")]
    assert "收藏的句子" == first_row[header.index("note")]

    # video_url 含 start_time 跳转
    video_url = first_row[header.index("video_url")]
    assert "/learn/99600" in video_url
    assert "start_time=1000" in video_url

    # start_time_sec: 1000ms → 1s
    assert "1" == first_row[header.index("start_time_sec")]


@pytest.mark.asyncio
async def test_export_csv_no_folder_field_when_no_folder(client, auth_headers, export_setup):
    """无 folder 的 bookmark → folder 列空字符串"""
    res = await client.get("/api/learning/bookmarks/export", headers=auth_headers)
    content = res.content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    header = rows[0]

    # 找 third sentence (无 folder)
    third_row = next(r for r in rows[1:] if "third sentence" in r[header.index("english")])
    assert "" == third_row[header.index("folder")]
    # 但有 tag
    assert "重点" == third_row[header.index("tags")]


# ==================== JSON 导出 ====================

@pytest.mark.asyncio
async def test_export_json(client, auth_headers, export_setup):
    """?format=json 完整结构"""
    res = await client.get(
        "/api/learning/bookmarks/export?format=json",
        headers=auth_headers
    )
    assert res.status_code == 200
    assert "application/json" in res.headers["content-type"]
    data = res.json()

    assert "exported_at" in data
    assert "user_id" in data
    assert data["total"] == 3
    assert "filters" in data
    assert "items" in data
    assert len(data["items"]) == 3

    # 验证 item 结构
    item = next(i for i in data["items"] if i["english"] == "first sentence")
    assert item["material_id"] == 99600
    assert item["material_title"] == "导出测试视频"
    assert item["chinese"] == "第一句"
    assert item["start_time_sec"] == 1  # 1000ms / 1000
    assert item["note"] == "收藏的句子"
    assert item["folder_name"] == "导出文件夹"
    assert "重点" in item["tags"]


# ==================== 过滤 ====================

@pytest.mark.asyncio
async def test_export_with_folder_filter(client, auth_headers, export_setup):
    """?folder_id=N 只导该 folder"""
    folder = export_setup["folder"]
    res = await client.get(
        f"/api/learning/bookmarks/export?folder_id={folder.id}&format=json",
        headers=auth_headers
    )
    data = res.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["folder_name"] == "导出文件夹"


@pytest.mark.asyncio
async def test_export_with_tag_filter(client, auth_headers, export_setup):
    """?tag_id=N 只导含该 tag"""
    tag = export_setup["tag"]
    res = await client.get(
        f"/api/learning/bookmarks/export?tag_id={tag.id}&format=json",
        headers=auth_headers
    )
    data = res.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert "重点" in item["tags"]


@pytest.mark.asyncio
async def test_export_with_search_filter(client, auth_headers, export_setup):
    """?search= 模糊搜索"""
    res = await client.get(
        "/api/learning/bookmarks/export?search=second&format=json",
        headers=auth_headers
    )
    data = res.json()
    assert data["total"] == 1
    assert "second" in data["items"][0]["english"]


@pytest.mark.asyncio
async def test_export_with_combined_filters(client, auth_headers, export_setup):
    """多过滤组合: folder + tag"""
    folder = export_setup["folder"]
    tag = export_setup["tag"]
    res = await client.get(
        f"/api/learning/bookmarks/export?folder_id={folder.id}&tag_id={tag.id}&format=json",
        headers=auth_headers
    )
    data = res.json()
    # bm1 是 folder 内 + 有 tag
    assert data["total"] == 1
    assert "first sentence" in data["items"][0]["english"]


@pytest.mark.asyncio
async def test_export_empty(client, auth_headers, db_session, test_user):
    """空用户导出 → header + 0 行"""
    res = await client.get("/api/learning/bookmarks/export", headers=auth_headers)
    content = res.content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    # 只有 header
    assert len(rows) == 1


# ==================== 用户隔离 ====================

@pytest.mark.asyncio
async def test_export_isolated_by_user(client, auth_headers, export_setup, db_session):
    """只导出当前用户, 别人 bm 不出现"""
    from app.models.models import User, Material, Subtitle, SubtitleBookmark
    other = User(username="export_other", phone="13900000040", password_hash="x")
    db_session.add(other)
    await db_session.flush()
    mat2 = Material(id=99650, title="别人的视频", duration=60, video_path="/x", subtitle_path="/x", cover_path="/x")
    sub2 = Subtitle(id=99650, material_id=99650, sequence=1, text_en="secret", text_cn="秘密", start_time=1, end_time=2)
    db_session.add_all([mat2, sub2])
    other_bm = SubtitleBookmark(user_id=other.id, material_id=99650, subtitle_id=99650)
    db_session.add(other_bm)
    await db_session.commit()

    res = await client.get(
        "/api/learning/bookmarks/export?format=json",
        headers=auth_headers
    )
    data = res.json()
    for item in data["items"]:
        assert item["material_id"] != 99650
        assert "secret" not in item["english"]
