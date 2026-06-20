"""
Batch 5 P2 (后缀): 字幕收藏标签筛选

后端:
- /bookmarks/all 加 tag_id 查询参数
  - tag_id=0: 仅无标签 (NOT EXISTS BookmarkTag)
  - tag_id=N: 含该标签 (EXISTS BookmarkTag WHERE user_tag_id=N)
- 与 search/material_id/folder_id 可组合

测试:
- 无标签筛选 (bookmark 无 BookmarkTag 关联)
- 指定标签筛选
- 标签筛选 + 其他筛选组合
"""
import pytest
from sqlalchemy import select
from app.models.models import UserTag, BookmarkTag, SubtitleBookmark


@pytest.fixture
async def tag_test_setup(db_session, test_user):
    """3 个 bookmark, 2 个 tag, 各种组合:
    - bm1: 含 tag_A
    - bm2: 含 tag_A + tag_B
    - bm3: 无任何 tag
    - 其他用户的 tag (用于隔离测试)
    """
    from app.models.models import Material, Subtitle, User
    mat = Material(
        id=99700, title="标签筛选视频", duration=60,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    subtitles = []
    for i, en in enumerate(["first", "second", "third"], start=99700):
        sub = Subtitle(
            id=i, material_id=99700, sequence=i - 99700,
            text_en=f"text {en}", text_cn=f"中文 {en}",
            start_time=(i - 99700) * 1000 + 1000, end_time=(i - 99700) * 1000 + 2000,
        )
        db_session.add(sub)
        subtitles.append(sub)

    bms = []
    for i in range(1, 4):
        bm = SubtitleBookmark(
            user_id=test_user.id,
            material_id=99700,
            subtitle_id=99700 + i - 1,
        )
        db_session.add(bm)
        bms.append(bm)
    await db_session.commit()
    for bm in bms:
        await db_session.refresh(bm)

    # 创建 2 个 tag
    tag_a = UserTag(user_id=test_user.id, name="A标签", color="#5c6ef5")
    tag_b = UserTag(user_id=test_user.id, name="B标签", color="#ef4444")
    db_session.add_all([tag_a, tag_b])
    await db_session.commit()
    await db_session.refresh(tag_a)
    await db_session.refresh(tag_b)

    # bm1: A, bm2: A+B, bm3: 无
    db_session.add(BookmarkTag(bookmark_id=bms[0].id, user_tag_id=tag_a.id))
    db_session.add(BookmarkTag(bookmark_id=bms[1].id, user_tag_id=tag_a.id))
    db_session.add(BookmarkTag(bookmark_id=bms[1].id, user_tag_id=tag_b.id))
    await db_session.commit()

    return {
        "bms": bms,
        "tag_a": tag_a,
        "tag_b": tag_b,
    }


@pytest.mark.asyncio
async def test_filter_by_tag_id(client, auth_headers, db_session, test_user, tag_test_setup):
    """?tag_id=N 筛选含某标签的 bookmark"""
    tag_a = tag_test_setup["tag_a"]
    res = await client.get(
        f"/api/learning/bookmarks/all?tag_id={tag_a.id}",
        headers=auth_headers
    )
    assert res.status_code == 200
    items = res.json()
    # bm1 + bm2 (都有 A)
    assert len(items) == 2
    # 验证响应里 tags 字段包含 A
    for item in items:
        tag_names = {t["name"] for t in item["tags"]}
        assert "A标签" in tag_names


@pytest.mark.asyncio
async def test_filter_by_tag_id_zero_means_untagged(client, auth_headers, db_session, test_user, tag_test_setup):
    """?tag_id=0 筛选无标签的 bookmark (NOT EXISTS)"""
    res = await client.get(
        "/api/learning/bookmarks/all?tag_id=0",
        headers=auth_headers
    )
    assert res.status_code == 200
    items = res.json()
    # 只有 bm3 无标签
    assert len(items) == 1
    assert items[0]["tags"] == []


@pytest.mark.asyncio
async def test_filter_by_tag_combines_with_other_filters(client, auth_headers, db_session, test_user, tag_test_setup):
    """?tag_id + ?folder_id 组合"""
    from app.models.models import BookmarkFolder
    folder = BookmarkFolder(user_id=test_user.id, name="我的文件夹")
    db_session.add(folder)
    await db_session.commit()
    await db_session.refresh(folder)

    # 把 bm1 移入 folder
    bm1 = tag_test_setup["bms"][0]
    bm1.folder_id = folder.id
    await db_session.commit()

    # 筛选: tag=A + folder=我的文件夹 → 只 bm1
    tag_a = tag_test_setup["tag_a"]
    res = await client.get(
        f"/api/learning/bookmarks/all?tag_id={tag_a.id}&folder_id={folder.id}",
        headers=auth_headers
    )
    items = res.json()
    assert len(items) == 1
    assert items[0]["folder_name"] == "我的文件夹"


@pytest.mark.asyncio
async def test_filter_by_nonexistent_tag_returns_empty(client, auth_headers, db_session, test_user, tag_test_setup):
    """?tag_id=不存在的 ID → 空"""
    res = await client.get(
        "/api/learning/bookmarks/all?tag_id=99999",
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_filter_by_tag_isolated_by_user(client, auth_headers, db_session, test_user, tag_test_setup):
    """别人的 tag 不会影响当前用户"""
    # 创建另一个用户的 tag + bookmark 关联
    from app.models.models import Material, Subtitle, User
    other = User(username="tag_filter_other", phone="13900000050", password_hash="x")
    db_session.add(other)
    await db_session.flush()
    other_mat = Material(id=99750, title="x", duration=60, video_path="/x", subtitle_path="/x", cover_path="/x")
    other_sub = Subtitle(id=99750, material_id=99750, sequence=1, text_en="x", text_cn="x", start_time=1, end_time=2)
    db_session.add_all([other_mat, other_sub])
    other_bm = SubtitleBookmark(user_id=other.id, material_id=99750, subtitle_id=99750)
    db_session.add(other_bm)
    other_tag = UserTag(user_id=other.id, name="别人A", color="#000000")
    db_session.add(other_tag)
    await db_session.commit()
    await db_session.refresh(other_bm)
    await db_session.refresh(other_tag)
    db_session.add(BookmarkTag(bookmark_id=other_bm.id, user_tag_id=other_tag.id))
    await db_session.commit()

    # 当前用户用 别人A 的 id 筛选 → 空 (隔离)
    res = await client.get(
        f"/api/learning/bookmarks/all?tag_id={other_tag.id}",
        headers=auth_headers
    )
    items = res.json()
    # 只看到当前用户的, 不该有别人的 bm
    for item in items:
        assert item["id"] != other_bm.id


@pytest.mark.asyncio
async def test_no_tag_filter_returns_all(client, auth_headers, db_session, test_user, tag_test_setup):
    """不带 tag_id → 返回全部 (有/无标签都返回)"""
    res = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers
    )
    items = res.json()
    # 3 个 bookmark 都在
    assert len(items) == 3
