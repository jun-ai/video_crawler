"""
素材接口测试
"""
import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "英语口语学习" in data["message"]


@pytest.mark.asyncio
async def test_health_check(client):
    """测试健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_materials(client):
    """测试获取素材列表"""
    response = await client.get("/api/materials")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_material_not_found(client):
    """测试获取不存在的素材"""
    response = await client.get("/api/materials/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_categories(client):
    """测试获取分类列表"""
    response = await client.get("/api/materials/categories")
    assert response.status_code == 200
