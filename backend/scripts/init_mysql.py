"""
MySQL 数据库初始化脚本

首次运行前，需要先创建数据库
"""
import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kb1324.*",
    "charset": "utf8mb4"
}

DATABASE_NAME = "english_learning"


def create_database():
    """创建数据库"""
    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`
                DEFAULT CHARACTER SET utf8mb4
                DEFAULT COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ 数据库 '{DATABASE_NAME}' 创建成功（或已存在）")

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    print("🚀 初始化 MySQL 数据库...")
    create_database()
    print("✅ 完成！现在可以启动后端服务了")
