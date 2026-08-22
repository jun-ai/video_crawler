"""测试 admin/stats endpoint — 验证 5 个串行 db.execute 改动不破功能"""
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def _clear_user_cache():
    """每个测试前清 app.routers.auth._user_cache。

    该缓存按 token 字符串缓存 User 对象。测试场景下 SQLite 表 drop/create 后
    自增 id 重置,同秒内签出的 JWT(sub 相同 + exp 同秒)字符串完全一致,
    会命中上一个测试缓存的旧 User(可能是 USER role),导致 403 假失败。
    """
    from app.routers.auth import _user_cache
    _user_cache.clear()
    yield
    _user_cache.clear()


@pytest.mark.asyncio
async def test_admin_stats_returns_correct_structure(client, db_session):
    """/api/admin/stats 200 + 包含 materials/categories/storage/total_views 字段(独立建 admin)"""
    from app.models.models import User, UserRole
    from app.services.auth import get_password_hash, create_access_token

    admin = User(
        username="admin_struct",
        phone="13800138001",
        password_hash=get_password_hash("admin123456"),
        role=UserRole.ADMIN,
        status="approved"
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    token = create_access_token(data={"sub": str(admin.id)})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/admin/stats", headers=headers)
    assert resp.status_code == 200, f"got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "materials" in body
    assert "categories" in body
    assert "storage" in body
    assert "total_views" in body
    # 空库时,total=0,active=0
    assert body["materials"]["total"] == 0
    assert body["materials"]["active"] == 0
    assert body["categories"] == []
    assert body["storage"] == {}
    assert body["total_views"] == 0


@pytest.mark.asyncio
async def test_admin_stats_no_auth_401(client):
    """/api/admin/stats 无 token → 401"""
    resp = await client.get("/api/admin/stats")
    assert resp.status_code == 401, f"expected 401, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_admin_stats_non_admin_403(client, db_session):
    """/api/admin/stats 普通用户 → 403(独立创建 user,避免 fixture 顺序污染)"""
    from app.models.models import User, UserRole
    from app.services.auth import get_password_hash, create_access_token

    user = User(
        username="regular_user_stats",
        phone="13800138999",
        password_hash=get_password_hash("test123456"),
        role=UserRole.USER,
        status="approved"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/admin/stats", headers=headers)
    assert resp.status_code == 403, f"expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_admin_stats_with_data(client, db_session):
    """/api/admin/stats 有 material 数据时正确聚合(独立建 admin)"""
    from app.models.models import User, UserRole, Material
    from app.services.auth import get_password_hash, create_access_token

    admin = User(
        username="admin_with_data",
        phone="13800138002",
        password_hash=get_password_hash("admin123456"),
        role=UserRole.ADMIN,
        status="approved"
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    token = create_access_token(data={"sub": str(admin.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 插入3条 material:2 active, 1 inactive, 2 个 category
    materials = [
        Material(title="m1", video_path="/v1.mp4", subtitle_path="/s1.vtt", cover_path="/c1.jpg",
                 storage_type="oss", category="A", is_active=True, view_count=10),
        Material(title="m2", video_path="/v2.mp4", subtitle_path="/s2.vtt", cover_path="/c2.jpg",
                 storage_type="oss", category="A", is_active=True, view_count=20),
        Material(title="m3", video_path="/v3.mp4", subtitle_path="/s3.vtt", cover_path="/c3.jpg",
                 storage_type="local", category="B", is_active=False, view_count=5),
    ]
    for m in materials:
        db_session.add(m)
    await db_session.commit()

    resp = await client.get("/api/admin/stats", headers=headers)
    assert resp.status_code == 200, f"got {resp.status_code}: {resp.text}"
    body = resp.json()

    # 3 total, 2 active
    assert body["materials"]["total"] == 3, f"total: {body['materials']}"
    assert body["materials"]["active"] == 2, f"active: {body['materials']}"
    # total_views = 10+20+5 = 35
    assert body["total_views"] == 35, f"views: {body['total_views']}"
    # categories: A=2, B=1
    cats = {c["name"]: c["count"] for c in body["categories"]}
    assert cats == {"A": 2, "B": 1}, f"categories: {cats}"
    # storage: oss=2, local=1
    assert body["storage"] == {"oss": 2, "local": 1}, f"storage: {body['storage']}"


@pytest.mark.asyncio
async def test_admin_stats_concurrent(client, db_session):
    """/api/admin/stats 并发调用 — 验证串行化后不会出现 IllegalStateChangeError
    SQLite StaticPool 在串行模式下无 bug,但能验证多次调用不互相干扰"""
    import asyncio
    from app.models.models import User, UserRole
    from app.services.auth import get_password_hash, create_access_token

    admin = User(
        username="admin_concurrent",
        phone="13800138003",
        password_hash=get_password_hash("admin123456"),
        role=UserRole.ADMIN,
        status="approved"
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    token = create_access_token(data={"sub": str(admin.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 5 个并发请求
    coros = [client.get("/api/admin/stats", headers=headers) for _ in range(5)]
    results = await asyncio.gather(*coros, return_exceptions=True)

    # 所有都应该 200(没人失败)
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            pytest.fail(f"concurrent request {i} raised exception: {r}")
        assert r.status_code == 200, f"concurrent request {i} got {r.status_code}: {r.text}"
        body = r.json()
        assert "materials" in body