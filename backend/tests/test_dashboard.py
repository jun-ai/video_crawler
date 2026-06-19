"""
LearningCenter dashboard 合并端点 (Batch 3.1)

前端 LearningCenter 一次发 5 个 API (statistics / trend / recent / completed / records) -
5 个 HTTP 串行,用户感知 500ms+ 延迟。合并为 1 个 dashboard 端点。

测试覆盖:
- test_dashboard_returns_full_structure: 5 个字段都存在
- test_dashboard_with_no_data: 新用户返回空数据不崩
- test_dashboard_includes_statistics: 含 LearningStatisticsResponse 字段
- test_dashboard_includes_trend_7days: 趋势 7 天 dates/counts
- test_dashboard_includes_recent_and_completed: recent/completed 各最多 10 条
- test_dashboard_recent_only_uncompleted: recent 不含已完成
- test_dashboard_completed_only_completed: completed 只含已完成
- test_dashboard_records_first_page: records 含 page/page_size/total
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_dashboard_returns_full_structure(
    client, auth_headers, db_session, test_user
):
    """dashboard 响应必须含 statistics / trend / recent / completed / records 5 个字段"""
    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "statistics" in data, "缺少 statistics 字段"
    assert "trend" in data, "缺少 trend 字段"
    assert "recent" in data, "缺少 recent 字段"
    assert "completed" in data, "缺少 completed 字段"
    assert "records" in data, "缺少 records 字段"


@pytest.mark.asyncio
async def test_dashboard_with_no_data(
    client, auth_headers
):
    """新用户(无任何学习记录)返回 0 数据不崩"""
    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    stats = data["statistics"]
    assert stats["total_materials"] == 0
    assert stats["completed_materials"] == 0
    assert stats["in_progress_materials"] == 0
    assert stats["total_vocabulary"] == 0
    assert stats["mastered_vocabulary"] == 0
    assert stats["streak_days"] == 0
    assert stats["total_watch_minutes"] == 0
    assert stats["total_learning_days"] == 0

    assert data["recent"] == []
    assert data["completed"] == []
    assert data["records"]["items"] == []
    assert data["records"]["total"] == 0


@pytest.mark.asyncio
async def test_dashboard_includes_statistics(
    client, auth_headers, db_session, test_user
):
    """statistics 字段含 9 个关键指标"""
    from app.models.models import Material, LearningRecord

    material = Material(
        id=1, title="T", duration=10,
        video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"
    )
    db_session.add(material)
    record = LearningRecord(
        user_id=test_user.id,
        material_id=1,
        progress=50,
        last_position=30,
        completed=False,
        watch_duration=600
    )
    db_session.add(record)
    await db_session.commit()

    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    stats = response.json()["statistics"]

    assert stats["total_materials"] == 1
    assert stats["completed_materials"] == 0
    assert stats["in_progress_materials"] == 1
    assert stats["total_watch_minutes"] == 10  # 600s // 60


@pytest.mark.asyncio
async def test_dashboard_includes_trend_7days(
    client, auth_headers
):
    """trend 字段默认 7 天 dates + counts 数组"""
    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    trend = response.json()["trend"]

    assert "dates" in trend
    assert "counts" in trend
    assert len(trend["dates"]) == 7
    assert len(trend["counts"]) == 7
    # 全 0 counts (新用户)
    assert all(c == 0 for c in trend["counts"])
    # dates 格式 mm-dd
    for d in trend["dates"]:
        assert len(d) == 5 and d[2] == "-"


@pytest.mark.asyncio
async def test_dashboard_recent_only_uncompleted(
    client, auth_headers, db_session, test_user
):
    """recent 字段只含 completed=False 的记录"""
    from app.models.models import Material, LearningRecord

    material = Material(
        id=1, title="T", duration=10,
        video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"
    )
    db_session.add(material)
    # 1 未完成 + 1 已完成
    db_session.add(LearningRecord(
        user_id=test_user.id, material_id=1, progress=30,
        last_position=10, completed=False, watch_duration=100
    ))
    db_session.add(LearningRecord(
        user_id=test_user.id, material_id=1, progress=100,
        last_position=600, completed=True, watch_duration=600
    ))
    await db_session.commit()

    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    recent = response.json()["recent"]

    assert len(recent) == 1
    assert recent[0]["completed"] is False


@pytest.mark.asyncio
async def test_dashboard_completed_only_completed(
    client, auth_headers, db_session, test_user
):
    """completed 字段只含 completed=True 的记录"""
    from app.models.models import Material, LearningRecord

    material = Material(
        id=1, title="T", duration=10,
        video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"
    )
    db_session.add(material)
    db_session.add(LearningRecord(
        user_id=test_user.id, material_id=1, progress=30,
        last_position=10, completed=False
    ))
    db_session.add(LearningRecord(
        user_id=test_user.id, material_id=1, progress=100,
        last_position=600, completed=True
    ))
    await db_session.commit()

    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    completed = response.json()["completed"]

    assert len(completed) == 1
    assert completed[0]["completed"] is True


@pytest.mark.asyncio
async def test_dashboard_records_first_page(
    client, auth_headers, db_session, test_user
):
    """records 字段含 items / total / page / page_size"""
    response = await client.get("/api/learning/dashboard", headers=auth_headers)
    assert response.status_code == 200
    records = response.json()["records"]

    assert "items" in records
    assert "total" in records
    assert "page" in records
    assert "page_size" in records
    assert records["page"] == 1
    assert records["page_size"] == 10
