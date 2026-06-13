"""
语料导入脚本

将现有的视频语料导入数据库
"""
import asyncio
import sys
import os

# Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, init_db
from app.models.models import Material, Subtitle
from app.services.subtitle_parser import parse_srt_file


async def import_material(
    title: str,
    video_path: str,
    subtitle_path: str,
    cover_path: str,
    category: str = None,
    difficulty: int = 2,
    description: str = None
):
    """
    导入单个语料

    Args:
        title: 标题
        video_path: 视频文件路径
        subtitle_path: 字幕文件路径
        cover_path: 封面图片路径
        category: 场景分类
        difficulty: 难度等级 (1-5)
        description: 描述
    """
    async with async_session_maker() as db:
        # 检查文件是否存在
        if not os.path.exists(video_path):
            print(f"[ERROR] 视频文件不存在: {video_path}")
            return

        if not os.path.exists(subtitle_path):
            print(f"[ERROR] 字幕文件不存在: {subtitle_path}")
            return

        if not os.path.exists(cover_path):
            print(f"[ERROR] 封面图片不存在: {cover_path}")
            return

        # 创建语料记录
        material = Material(
            title=title,
            description=description,
            video_path=video_path,
            subtitle_path=subtitle_path,
            cover_path=cover_path,
            category=category,
            difficulty=difficulty
        )

        db.add(material)
        await db.flush()

        # 解析字幕
        try:
            subtitles = await parse_srt_file(subtitle_path, material.id)
            for sub in subtitles:
                db.add(Subtitle(**sub.model_dump()))
            print(f"[OK] 解析字幕成功: {len(subtitles)} 条")
        except Exception as e:
            print(f"[WARN] 字幕解析失败: {e}")

        await db.commit()
        await db.refresh(material)

        print(f"[OK] 语料导入成功: {title} (ID: {material.id})")
        return material.id


async def main():
    """主函数 - 导入示例语料"""
    print("[INFO] 开始导入语料...")

    # 初始化数据库
    await init_db()

    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 导入现有语料
    await import_material(
        title="Day in New York City",
        video_path=os.path.join(project_dir, "videoplayback.mp4"),
        subtitle_path=os.path.join(project_dir, "[English (auto-generated)] I went to NYC for a boy [DownSub.com].srt"),
        cover_path=os.path.join(project_dir, "PKOw-FbVXrc-SD.jpg"),
        category="travel",
        difficulty=2,
        description="跟随博主探索纽约的一天，学习旅行场景下的日常口语表达"
    )

    print("\n[DONE] 语料导入完成！")


if __name__ == "__main__":
    asyncio.run(main())
