"""
Batch 5 P1-4: 词汇导出

后端 /learning/vocabulary/export 端点:
- 支持 json / csv 格式
- 共享 filter (is_new / is_due / keyword / material_id)
- 只导出当前用户自己的生词 (user_id 隔离)

测试覆盖:
- JSON 格式: 完整结构 + Content-Disposition
- CSV 格式: UTF-8 BOM + 表头
- 跨用户隔离: B 用户的词不出现在 A 的导出
- filter 生效 (is_new / keyword)
"""
import csv
import io
import json
import pytest


@pytest.fixture
async def export_setup(db_session, test_user):
    """基础 fixture: 1 material + 3 词汇 (新词/学习中/已掌握)"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="TED演讲", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    v_new = Vocabulary(user_id=test_user.id, material_id=1, word="sprint",
                      context="running fast", review_count=0, next_review_at=None, mastered=False)
    v_learning = Vocabulary(user_id=test_user.id, material_id=1, word="marathon",
                           context="42km race", review_count=2, next_review_at=None, mastered=False)
    v_mastered = Vocabulary(user_id=test_user.id, material_id=1, word="jog",
                           context="slow run", review_count=5, next_review_at=None, mastered=True)
    db_session.add_all([v_new, v_learning, v_mastered])
    await db_session.commit()
    return {"new": v_new, "learning": v_learning, "mastered": v_mastered}


@pytest.mark.asyncio
async def test_export_json_returns_attachment(client, auth_headers, export_setup):
    """JSON 导出: 返回 attachment, 含 total + items + SM-2 字段"""
    response = await client.get(
        "/api/learning/vocabulary/export?format=json",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert ".json" in response.headers["content-disposition"]

    body = response.json()
    assert body["total"] == 3
    assert "exported_at" in body
    assert body["user_id"]

    # 验证所有词都导出
    words = {item["word"] for item in body["items"]}
    assert words == {"sprint", "marathon", "jog"}

    # 验证 SM-2 字段都在
    jog = next(i for i in body["items"] if i["word"] == "jog")
    assert jog["mastered"] is True
    assert jog["review_count"] == 5
    assert jog["ease_factor"] == 2.5
    assert jog["material_title"] == "TED演讲"
    assert jog["context"] == "slow run"


@pytest.mark.asyncio
async def test_export_csv_with_bom(client, auth_headers, export_setup):
    """CSV 导出: UTF-8 BOM + 表头 + 行数据"""
    response = await client.get(
        "/api/learning/vocabulary/export?format=csv",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert ".csv" in response.headers["content-disposition"]

    # 验证 BOM
    content = response.content
    assert content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM

    # 解析 CSV (跳过 BOM)
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    assert len(rows) == 3
    words = {row["word"] for row in rows}
    assert words == {"sprint", "marathon", "jog"}

    # 验证表头
    expected_headers = {"word", "phonetic", "translation", "context",
                        "material_title", "mastered", "starred", "review_count",
                        "next_review_at", "created_at"}
    assert set(reader.fieldnames) == expected_headers

    # 验证 mastered=true (字符串)
    jog = next(r for r in rows if r["word"] == "jog")
    assert jog["mastered"] == "true"
    assert jog["review_count"] == "5"
    assert jog["material_title"] == "TED演讲"


@pytest.mark.asyncio
async def test_export_filter_is_new(client, auth_headers, export_setup):
    """filter is_new=true: 只导新词"""
    response = await client.get(
        "/api/learning/vocabulary/export?format=json&is_new=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["word"] == "sprint"


@pytest.mark.asyncio
async def test_export_filter_keyword(client, auth_headers, export_setup):
    """filter keyword: 模糊匹配"""
    response = await client.get(
        "/api/learning/vocabulary/export?format=json&keyword=run",
        headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    # sprint, marathon, jog 都不含 'run' - 等等 marathon 不含, 但 "jog" 不含 run
    # 实际: sprint/marathon/jog 都不含 'run', 所以应该是 0
    # 改测: 用 'ar' 应该命中 marathon
    assert body["total"] == 0

    response2 = await client.get(
        "/api/learning/vocabulary/export?format=json&keyword=ar",
        headers=auth_headers
    )
    body2 = response2.json()
    assert body2["total"] == 1
    assert body2["items"][0]["word"] == "marathon"


@pytest.mark.asyncio
async def test_export_cross_user_isolation(
    client, auth_headers, db_session, test_user, export_setup
):
    """跨用户隔离: B 用户的词不出现在 A 的导出"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="otherexport",
        phone="13800139933",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=2, title="V2", duration=10,
                            video_path="/v2.mp4", subtitle_path="/s2.srt", cover_path="/c2.jpg"))

    db_session.add(Vocabulary(
        user_id=other_user.id, material_id=2, word="secret_word",
        review_count=0, next_review_at=None, mastered=False
    ))
    await db_session.commit()

    # A 的导出不应含 secret_word
    response = await client.get(
        "/api/learning/vocabulary/export?format=json",
        headers=auth_headers
    )
    body = response.json()
    words = {item["word"] for item in body["items"]}
    assert "secret_word" not in words
    assert body["user_id"] != other_user.id  # user_id 是 A 的


@pytest.mark.asyncio
async def test_export_default_format_is_json(client, auth_headers, export_setup):
    """不指定 format: 默认 JSON"""
    response = await client.get(
        "/api/learning/vocabulary/export",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert ".json" in response.headers["content-disposition"]