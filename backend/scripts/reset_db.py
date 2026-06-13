"""
重置数据库表结构

注意：这会删除所有数据！
"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kb1324.*",
    "charset": "utf8mb4"
}

DATABASE_NAME = "english_learning"


def reset_tables():
    """重置表结构"""
    connection = pymysql.connect(**DB_CONFIG, database=DATABASE_NAME)

    try:
        with connection.cursor() as cursor:
            # 删除所有表（注意顺序，先删除有外键依赖的表）
            tables = [
                "favorites",
                "vocabularies",
                "learning_records",
                "subtitles",
                "materials",
                "users"
            ]

            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"[OK] 删除表: {table}")

            connection.commit()
            print("\n[DONE] 所有表已删除，重启后端服务将自动创建新表")

    finally:
        connection.close()


if __name__ == "__main__":
    print("[WARN] 警告：这将删除所有数据！")
    confirm = input("确定要继续吗？(y/n): ")
    if confirm.lower() == 'y':
        reset_tables()
    else:
        print("[INFO] 已取消")
