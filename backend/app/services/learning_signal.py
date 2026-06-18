"""
LearningSignalService - 三表联动核心

接收以下学习信号：
- dictation_result (DictationMode): score<60 触发入 Vocabulary
- interpretation_status (EnglishCards): status=unknown 触发入 Vocabulary
- vocabulary_review (VocabularyReview): 已有完整流程

统一调度 spaced_repetition（SM-2）
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User, Vocabulary


class LearningSignalService:
    """统一学习信号服务"""

    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def process_dictation_result(
        self,
        material_id: int,
        subtitle_id: int,
        score: int,
        user_input: str,
        correct_text: str,
    ) -> List[Vocabulary]:
        """
        处理听写结果。score<60 时把错词加入生词本。

        Returns:
            创建或重置的 Vocabulary 列表（可能为空）
        """
        if score >= 60:
            return []

        # 1. 抽取错词
        wrong_words = self._extract_wrong_words(user_input, correct_text)
        if not wrong_words:
            return []

        # 2. 去重入 Vocabulary
        created: List[Vocabulary] = []
        for word in wrong_words:
            vocab = await self._get_or_create_vocabulary(word, subtitle_id)
            created.append(vocab)
        await self.db.commit()
        return created

    async def process_interpretation_status(
        self,
        interpretation_id: int,
        status: str,
        content: str,
    ) -> Optional[Vocabulary]:
        """
        处理解读卡状态。status=unknown 时入生词本。

        Returns:
            创建或重置的 Vocabulary，未触发返回 None
        """
        if status != "unknown":
            return None
        vocab = await self._get_or_create_vocabulary(content, interpretation_id)
        await self.db.commit()
        return vocab

    def _extract_wrong_words(self, user_input: str, correct_text: str) -> List[str]:
        """
        抽取错词。简单实现：split 后 diff（位置敏感）。
        - 标点去除
        - 大小写不敏感
        - 仅返回 correct_text 里出现但 user_input 里没出现（或不同）的词
        """
        import re

        def normalize(text: str) -> List[str]:
            # 去标点，转小写
            cleaned = re.sub(r"[.,!?;:'\"\(\)\[\]]", "", text.lower())
            return cleaned.split()

        user_words = normalize(user_input)
        correct_words = normalize(correct_text)

        # 计算每个正确词是否在用户输入里
        wrong = []
        user_set = set(user_words)
        for word in correct_words:
            if word not in user_set:
                wrong.append(word)
        return wrong

    async def _get_or_create_vocabulary(self, word: str, source_id: int) -> Vocabulary:
        """查重入 Vocabulary。已存在则重置复习进度。"""
        result = await self.db.execute(
            select(Vocabulary)
            .where(Vocabulary.user_id == self.user.id, Vocabulary.word == word)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 重置复习进度（用户又忘了）
            existing.review_count = 0
            existing.next_review_at = None
            existing.interval_days = 0
            existing.mastered = False
            return existing

        vocab = Vocabulary(
            user_id=self.user.id,
            word=word,
            context=f"From source {source_id}",
            ease_factor=2.5,
            interval_days=0,
            review_count=0,
            next_review_at=None,
            mastered=False,
        )
        self.db.add(vocab)
        await self.db.flush()
        return vocab
