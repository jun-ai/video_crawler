"""
添加视频解读测试数据
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
from app.models.models import VideoInterpretation


async def add_interpretation_data(material_id: int):
    """添加视频解读测试数据"""
    async with async_session_maker() as db:
        # 单词数据
        words = [
            {"content_en": "spontaneous", "content_cn": "adj. 自发的，自然的", "example_sentence": "I took a spontaneous trip to New York City.", "difficulty": 3},
            {"content_en": "filmer", "content_cn": "n. 摄影师，摄像师", "example_sentence": "He's a filmer for YouTubers here.", "difficulty": 2},
            {"content_en": "bonded", "content_cn": "v. 建立关系，结交 (bond的过去式)", "example_sentence": "We quickly bonded over our love for videos.", "difficulty": 3},
            {"content_en": "lens", "content_cn": "n. 镜头", "example_sentence": "Dude what a cool lens so cool!", "difficulty": 2},
            {"content_en": "subscribe", "content_cn": "v. 订阅", "example_sentence": "Guys go subscribe we need to make this YouTube money.", "difficulty": 2},
        ]

        # 短语数据
        phrases = [
            {"content_en": "bond over", "content_cn": "因...而建立友谊", "example_sentence": "We quickly bonded over our love for videos and YouTube.", "difficulty": 3},
            {"content_en": "every now and then", "content_cn": "偶尔，有时", "example_sentence": "You may or may not have seen us in each other's videos every now and then.", "difficulty": 2},
            {"content_en": "full circle", "content_cn": "圆满，回到原点", "example_sentence": "Full circle now she's down bad for me in bnh.", "difficulty": 3},
            {"content_en": "check it out", "content_cn": "去看看，查看一下", "example_sentence": "I'm gonna go check it out and see if there's a spot for me to work.", "difficulty": 2},
            {"content_en": "hang out", "content_cn": "闲逛，待在一起", "example_sentence": "We bonded and now hang out all the time.", "difficulty": 2},
        ]

        # 语法数据
        grammar = [
            {"content_en": "Present Perfect Tense", "content_cn": "现在完成时", "explanation": "表示过去发生的动作对现在造成的影响或结果，结构为 have/has + 过去分词", "example_sentence": "I've never been to what is probably his favorite place on planet Earth.", "difficulty": 3},
            {"content_en": "Modal Verbs", "content_cn": "情态动词", "explanation": "表示可能、必要、许可等意义，如 may, might, should, must 等", "example_sentence": "You may or may not have seen us in each other's videos.", "difficulty": 2},
            {"content_en": "Infinitive of Purpose", "content_cn": "目的不定式", "explanation": "用不定式表示动作的目的，结构为 to + 动词原形", "example_sentence": "I decided it was finally time to go to Every camera leopard's playground.", "difficulty": 2},
        ]

        # 添加单词
        for i, word in enumerate(words):
            item = VideoInterpretation(
                material_id=material_id,
                category='word',
                content_en=word['content_en'],
                content_cn=word['content_cn'],
                example_sentence=word.get('example_sentence'),
                difficulty=word.get('difficulty', 2),
                sequence=i
            )
            db.add(item)

        # 添加短语
        for i, phrase in enumerate(phrases):
            item = VideoInterpretation(
                material_id=material_id,
                category='phrase',
                content_en=phrase['content_en'],
                content_cn=phrase['content_cn'],
                example_sentence=phrase.get('example_sentence'),
                difficulty=phrase.get('difficulty', 2),
                sequence=i
            )
            db.add(item)

        # 添加语法
        for i, g in enumerate(grammar):
            item = VideoInterpretation(
                material_id=material_id,
                category='grammar',
                content_en=g['content_en'],
                content_cn=g['content_cn'],
                explanation=g.get('explanation'),
                example_sentence=g.get('example_sentence'),
                difficulty=g.get('difficulty', 2),
                sequence=i
            )
            db.add(item)

        await db.commit()
        print(f"[OK] 已添加 {len(words)} 个单词, {len(phrases)} 个短语, {len(grammar)} 个语法点")


async def main():
    """主函数"""
    print("[INFO] 开始添加视频解读数据...")

    # 初始化数据库
    await init_db()

    # 为 material_id=1 添加测试数据
    await add_interpretation_data(1)

    print("[DONE] 数据添加完成！")


if __name__ == "__main__":
    asyncio.run(main())
