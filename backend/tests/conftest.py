"""
测试配置和 fixtures
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.models.models import Base
from app.services.auth import get_password_hash, create_access_token


# 使用 SQLite 内存数据库 + StaticPool 确保所有连接共享同一个数据库
test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """每个测试前后创建和清理数据库表"""
    # 禁用限流，避免测试间互相触发 429
    from app.utils.rate_limit import limiter
    limiter.enabled = False

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    limiter.enabled = True


@pytest_asyncio.fixture
async def db_session():
    """提供测试数据库会话"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """提供 HTTP 测试客户端"""
    from app.main import app
    from app.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
    from app.models.models import User, UserRole

    user = User(
        username="testuser",
        phone="13800138000",
        password_hash=get_password_hash("test123456"),
        status="approved"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """提供认证请求头"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(db_session):
    """创建管理员用户"""
    from app.models.models import User, UserRole

    user = User(
        username="admin",
        phone="13800138001",
        password_hash=get_password_hash("admin123456"),
        role=UserRole.ADMIN,
        status="approved"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_headers(admin_user):
    """提供管理员认证请求头"""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_activation_code(db_session):
    """创建测试激活码"""
    from app.models.models import ActivationCode

    code = ActivationCode(
        code="TESTCODE123",
        max_uses=10,
        use_count=0
    )
    db_session.add(code)
    await db_session.commit()
    await db_session.refresh(code)
    return code
