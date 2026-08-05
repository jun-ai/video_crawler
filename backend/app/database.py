from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 创建异步引擎
# echo=False: SQL 日志改由 logging 控制（setup_logging 里设 level），
# 避免 echo=True 导致每条 SQL 打印两遍
# pool_pre_ping=True: 借连接前先 SELECT 1 探活, 死了就重连
# pool_recycle=3600: 1 小时强制回收 (< MySQL wait_timeout 8h, 避免被服务端单方面 kill)
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
