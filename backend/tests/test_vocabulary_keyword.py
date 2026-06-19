"""
Batch 5 P0-3: 词汇 keyword 单词模糊搜索

后端 /learning/vocabulary 加 keyword 参数:
- keyword="run" → WHERE word ILIKE '%run%' (case-insensitive)
- 空 keyword 或全空格 → 不过滤
- 与 is_new / is_due / material_id 可组合

测试覆盖:
- 单词中间模糊匹配 (run → running/sunrun)
- 大小写不敏感 (Run = run)
- 空 keyword 不影响结果 (返回所有)
- 跨用户隔离
"""
from datetime import datetime, timezone, timedelta
import pytest


@pytest.mark.asyncio
async def test_vocabulary_keyword_partial_match(
    client, auth_headers, db_session, test_user
):
    """keyword='run' 应匹配 running/sunrun/runner 等含 'run' 的单词"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    db_session.add_all([
        Vocabulary(user_id=test_user.id, material_id=1, word="run",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="running",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="sunrunner",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="banana",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="rune",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?keyword=run",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    words = sorted([item["word"] for item in data["items"]])
    # run / running / sunrunner / rune 都含 'run'，banana 不含
    assert words == ["run", "rune", "running", "sunrunner"]
    assert "banana" not in words


@pytest.mark.asyncio
async def test_vocabulary_keyword_case_insensitive(
    client, auth_headers, db_session, test_user
):
    """keyword='RUN' / 'Run' / 'rUn' 都应匹配 (ilike 大小写不敏感)"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    db_session.add_all([
        Vocabulary(user_id=test_user.id, material_id=1, word="Hello",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="HELLO",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="heLLoWorld",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="world",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    for kw in ["RUN", "Run", "rUn", "run"]:
        # 上面测试里没 HELLO 的，这里测 HELLO 才是 case-insensitive 主战场
        pass

    response = await client.get(
        "/api/learning/vocabulary?keyword=HELLO",
        headers=auth_headers
    )
    assert response.status_code == 200
    words = sorted([item["word"] for item in response.json()["items"]])
    # 大写关键词 HELLO 应匹配 Hello / HELLO / heLLoWorld (都含 hello)
    assert words == ["HELLO", "Hello", "heLLoWorld"]
    assert "world" not in words


@pytest.mark.asyncio
async def test_vocabulary_keyword_empty_returns_all(
    client, auth_headers, db_session, test_user
):
    """keyword 为空 / 全空格 / 不传 → 不过滤, 返回所有"""
    from app.models.models import Material, Vocabulary

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    db_session.add_all([
        Vocabulary(user_id=test_user.id, material_id=1, word="apple",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="banana",
                   review_count=0, next_review_at=None, mastered=False),
        Vocabulary(user_id=test_user.id, material_id=1, word="cherry",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    # 1. 不传 keyword
    r1 = await client.get("/api/learning/vocabulary", headers=auth_headers)
    assert r1.status_code == 200
    assert len(r1.json()["items"]) == 3

    # 2. keyword 空字符串
    r2 = await client.get("/api/learning/vocabulary?keyword=", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()["items"]) == 3

    # 3. keyword 全空格 (后端 strip 后视为空, 不过滤)
    r3 = await client.get("/api/learning/vocabulary?keyword=%20%20", headers=auth_headers)
    assert r3.status_code == 200
    assert len(r3.json()["items"]) == 3


@pytest.mark.asyncio
async def test_vocabulary_keyword_cross_user_isolation(
    client, auth_headers, db_session, test_user
):
    """其他用户的单词不应出现在搜索结果里 (即使 keyword 匹配)"""
    from app.models.models import Material, Vocabulary, User
    from app.services.auth import get_password_hash

    other_user = User(
        username="otherkw",
        phone="13800139977",
        password_hash=get_password_hash("hashed"),
        status='approved'
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    db_session.add(Material(id=1, title="V", duration=10,
                            video_path="/v.mp4", subtitle_path="/s.srt", cover_path="/c.jpg"))

    db_session.add_all([
        # test_user 的词
        Vocabulary(user_id=test_user.id, material_id=1, word="runner",
                   review_count=0, next_review_at=None, mastered=False),
        # other_user 的词 (keyword 同样匹配, 但不该泄露)
        Vocabulary(user_id=other_user.id, material_id=1, word="rundown",
                   review_count=0, next_review_at=None, mastered=False),
    ])
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary?keyword=run",
        headers=auth_headers
    )
    assert response.status_code == 200
    words = [item["word"] for item in response.json()["items"]]
    assert "runner" in words
    assert "rundown" not in words