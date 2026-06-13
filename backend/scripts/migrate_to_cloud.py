"""
数据迁移脚本：将本地文件迁移到云存储

使用方法：
1. 配置 .env 文件中的云存储参数
2. 设置 STORAGE_TYPE=aliyun_oss 或 tencent_cos
3. 运行: python scripts/migrate_to_cloud.py
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from sqlalchemy import select, update
from app.database import async_session_maker, init_db
from app.models.models import Material
from app.services.storage import get_storage_service, generate_object_key
from app.config import settings


async def migrate_materials():
    """迁移所有语料文件到云存储"""
    print("=" * 60)
    print("开始迁移语料文件到云存储")
    print(f"存储类型: {settings.storage_type}")
    print("=" * 60)

    if settings.storage_type == 'local':
        print("错误: 当前存储类型为 local，请先配置云存储")
        return

    storage = get_storage_service()
    project_root = Path(__file__).parent.parent.parent

    async with async_session_maker() as db:
        # 获取所有语料
        result = await db.execute(select(Material))
        materials = result.scalars().all()

        print(f"共找到 {len(materials)} 个语料需要迁移")

        success_count = 0
        error_count = 0

        for i, material in enumerate(materials, 1):
            print(f"\n[{i}/{len(materials)}] 迁移: {material.title}")

            try:
                # 迁移视频文件
                if material.video_path and not material.video_path.startswith('http'):
                    video_url = await migrate_file(
                        storage, project_root, material.video_path, 'video'
                    )
                    if video_url:
                        material.video_path = video_url
                        print(f"  ✓ 视频已上传: {video_url[:50]}...")

                # 迁移字幕文件
                if material.subtitle_path and not material.subtitle_path.startswith('http'):
                    subtitle_url = await migrate_file(
                        storage, project_root, material.subtitle_path, 'subtitle'
                    )
                    if subtitle_url:
                        material.subtitle_path = subtitle_url
                        print(f"  ✓ 字幕已上传: {subtitle_url}")

                # 迁移封面文件
                if material.cover_path and not material.cover_path.startswith('http'):
                    cover_url = await migrate_file(
                        storage, project_root, material.cover_path, 'cover'
                    )
                    if cover_url:
                        material.cover_path = cover_url
                        print(f"  ✓ 封面已上传: {cover_url}")

                await db.commit()
                success_count += 1
                print(f"  ✓ 迁移成功")

            except Exception as e:
                error_count += 1
                print(f"  ✗ 迁移失败: {e}")
                await db.rollback()

        print("\n" + "=" * 60)
        print(f"迁移完成: 成功 {success_count}, 失败 {error_count}")
        print("=" * 60)


async def migrate_file(storage, project_root: Path, local_path: str, file_type: str) -> str:
    """迁移单个文件到云存储"""
    # 构建完整路径
    if local_path.startswith('/'):
        file_path = Path(local_path)
    else:
        file_path = project_root / local_path

    if not file_path.exists():
        print(f"  ! 文件不存在: {file_path}")
        return None

    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # 生成云存储键
    object_key = generate_object_key(file_type, file_path.name)

    # 确定内容类型
    content_types = {
        'video': 'video/mp4',
        'subtitle': 'text/plain',
        'cover': 'image/jpeg'
    }

    # 上传到云存储
    url = await storage.upload_file(
        file_data,
        object_key,
        content_types.get(file_type)
    )

    return url


async def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")

    async with async_session_maker() as db:
        result = await db.execute(select(Material))
        materials = result.scalars().all()

        local_count = 0
        cloud_count = 0

        for material in materials:
            if material.video_path and material.video_path.startswith('http'):
                cloud_count += 1
            else:
                local_count += 1

        print(f"云存储文件: {cloud_count}")
        print(f"本地文件: {local_count}")


async def main():
    """主函数"""
    # 初始化数据库
    await init_db()

    # 执行迁移
    await migrate_materials()

    # 验证结果
    await verify_migration()


if __name__ == '__main__':
    asyncio.run(main())
