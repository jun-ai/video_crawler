"""
认证接口测试
"""
import pytest


@pytest.mark.asyncio
async def test_register_success(client, db_session):
    """测试正常注册"""
    # 先创建激活码
    from app.models.models import ActivationCode
    code = ActivationCode(code="VALIDCODE", max_uses=10, use_count=0)
    db_session.add(code)
    await db_session.commit()

    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "phone": "13900139000",
        "password": "password123",
        "invite_code": "VALIDCODE"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "注册成功" in data["message"]


@pytest.mark.asyncio
async def test_register_invalid_phone(client):
    """测试无效手机号注册"""
    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "phone": "123",
        "password": "password123",
        "invite_code": "ANYCODE"
    })
    assert response.status_code == 400
    assert "手机号格式不正确" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_missing_activation_code(client):
    """测试缺少激活码注册"""
    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "phone": "13900139000",
        "password": "password123",
        "invite_code": ""
    })
    assert response.status_code == 400
    assert "激活码" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_phone(client, test_user):
    """测试重复手机号注册"""
    from app.models.models import ActivationCode
    from sqlalchemy import select

    # 创建激活码
    code = ActivationCode(code="DUPCODE", max_uses=10, use_count=0)
    db = client._transport.app.dependency_overrides
    # 需要通过新的请求测试
    response = await client.post("/api/auth/register", json={
        "username": "another",
        "phone": "13800138000",  # 与 test_user 相同
        "password": "password123",
        "invite_code": "ANYCODE"
    })
    assert response.status_code == 400
    assert "手机号已被注册" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """测试正常登录"""
    response = await client.post("/api/auth/login", json={
        "phone": "13800138000",
        "password": "test123456"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """测试错误密码登录"""
    response = await client.post("/api/auth/login", json={
        "phone": "13800138000",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "手机号或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """测试不存在的用户登录"""
    response = await client.post("/api/auth/login", json={
        "phone": "13999999999",
        "password": "test123456"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_authenticated(client, auth_headers):
    """测试已认证用户获取个人信息"""
    response = await client.get("/api/auth/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["phone"] == "13800138000"


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client):
    """测试未认证用户获取个人信息"""
    response = await client.get("/api/auth/profile")
    assert response.status_code == 401
