"""Task 1.7: /bookmarks/all 单次 join 端点（修 N+1）"""
import pytest


@pytest.mark.asyncio
async def test_get_all_bookmarks_single_request(
    client, auth_headers, db_session, test_user
):
    """单次调用 /bookmarks/all 应返回所有收藏（join Subtitle）"""
    from app.models.models import Material, Subtitle, SubtitleBookmark

    # 3 个材料 × 2 句 = 6 个 bookmark
    for i in range(1, 4):
        mat = Material(
            id=99700 + i, title=f"M{i}", duration=10,
            video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
        )
        db_session.add(mat)
        for j in range(1, 3):
            sub = Subtitle(
                id=99700 + i * 10 + j, material_id=99700 + i, sequence=j,
                text_en=f"hello {i}-{j}", text_cn=f"你好 {i}-{j}",
                start_time=j * 1000, end_time=(j + 1) * 1000,
            )
            db_session.add(sub)
            bm = SubtitleBookmark(
                user_id=test_user.id,
                material_id=99700 + i,
                subtitle_id=99700 + i * 10 + j,
                practice_count=i,
            )
            db_session.add(bm)
    await db_session.commit()

    response = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers,
    )
    assert response.status_code == 200, f"got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 6, f"应 6 条，实际 {len(data)}"

    # 验证 join 字段
    first = data[0]
    assert "subtitle_text_en" in first
    assert "subtitle_text_cn" in first
    assert "subtitle_start_time" in first
    assert first["subtitle_text_en"].startswith("hello")


@pytest.mark.asyncio
async def test_get_all_bookmarks_empty(client, auth_headers, test_user):
    """无收藏应返回空列表"""
    response = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_all_bookmarks_only_own(
    client, auth_headers, db_session, test_user
):
    """只返回当前用户的收藏（不应看到其他用户的）"""
    from app.models.models import Material, Subtitle, SubtitleBookmark, User
    from app.services.auth import get_password_hash

    # 另一个用户
    other = User(
        username="other", phone="13911111111",
        password_hash=get_password_hash("p"), status="approved",
    )
    db_session.add(other)

    # 自己的 bookmark
    mat = Material(
        id=99800, title="M", duration=10,
        video_path="/x.mp4", subtitle_path="/x.srt", cover_path="/x.jpg",
    )
    db_session.add(mat)
    sub = Subtitle(
        id=99800, material_id=99800, sequence=1,
        text_en="mine", start_time=0, end_time=1000,
    )
    db_session.add(sub)
    db_session.add(SubtitleBookmark(
        user_id=test_user.id, material_id=99800, subtitle_id=99800,
    ))
    # 别人的 bookmark
    sub2 = Subtitle(
        id=99801, material_id=99800, sequence=2,
        text_en="others", start_time=1000, end_time=2000,
    )
    db_session.add(sub2)
    await db_session.flush()
    await db_session.refresh(other)
    db_session.add(SubtitleBookmark(
        user_id=other.id, material_id=99800, subtitle_id=99801,
    ))
    await db_session.commit()

    response = await client.get(
        "/api/learning/bookmarks/all",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1, f"应只 1 条（自己的），实际 {len(data)}"
    assert data[0]["subtitle_text_en"] == "mine"
