"""
创建测试用户脚本

用于测试登录功能
"""
import asyncio
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session_maker, init_db
from app.models.models import User
from app.services.auth import get_password_hash
from sqlalchemy import select


async def create_test_user():
    """创建测试用户"""
    print("[INFO] 初始化数据库...")
    await init_db()

    async with async_session_maker() as db:
        # 检查用户是否已存在
        result = await db.execute(select(User).where(User.phone == "13800138000"))
        if result.scalar_one_or_none():
            print("[INFO] 测试用户已存在")
            return

        # 创建测试用户
        user = User(
            username="testuser",
            phone="13800138000",
            password_hash=get_password_hash("123456")
        )

        db.add(user)
        await db.commit()

        print("[OK] 测试用户创建成功!")
        print("-" * 40)
        print("手机号: 13800138000")
        print("密码: 123456")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(create_test_user())
