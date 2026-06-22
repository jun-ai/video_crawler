"""
重建 MySQL 表结构

删除所有表并重新创建
"""
import asyncio
import pymysql
from sqlalchemy import text

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kb1324.*",
    "charset": "utf8mb4",
    "database": "english_learning"
}


def drop_all_tables():
    """删除所有表"""
    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 禁用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # 获取所有表名
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # 删除所有表
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                print(f"  删除表: {table_name}")

            # 启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        connection.commit()
        print("[OK] All tables dropped")
    finally:
        connection.close()


async def create_tables():
    """通过 SQLAlchemy 创建表"""
    import sys
    sys.path.insert(0, '.')

    from app.database import engine, Base, init_db

    # 导入所有模型
    from app.models.models import (
        User, Material, Subtitle, LearningRecord,
        Vocabulary, Favorite, VideoInterpretation,
        InterpretationLearning, DictationRecord, SubtitleAnnotation
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[OK] All tables created")


if __name__ == "__main__":
    print("[*] Rebuild MySQL tables...")
    print()

    print("1. Drop old tables...")
    drop_all_tables()

    print()
    print("2. Create new tables...")
    asyncio.run(create_tables())

    print()
    print("[OK] Done! You can start the backend service now.")
