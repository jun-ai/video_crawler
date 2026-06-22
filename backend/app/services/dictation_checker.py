"""
听写答案校验服务
支持多种校验模式：精确匹配、宽松匹配
"""
import re
import difflib
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class WordResult:
    """单词校验结果"""
    word: str
    status: str  # 'correct', 'missing', 'extra', 'wrong'


class DictationChecker:
    """听写校验器"""

    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: 严格模式（区分大小写和标点）
        """
        self.strict_mode = strict_mode

    def normalize_text(self, text: str) -> str:
        """文本标准化"""
        if self.strict_mode:
            return text.strip()

        # 宽松模式：忽略大小写和多余空格
        text = text.lower().strip()
        # 保留基本标点，但允许一定灵活性
        text = re.sub(r'[^\w\s\'.?!,-]', '', text)
        # 多空格合并
        text = re.sub(r'\s+', ' ', text)
        return text

    def compare_texts(
        self,
        user_input: str,
        correct_text: str
    ) -> Tuple[int, List[WordResult], str]:
        """
        比较用户输入和正确答案

        Args:
            user_input: 用户输入的文本
            correct_text: 正确答案

        Returns:
            (score, word_results, feedback)
        """
        # 标准化
        user_normalized = self.normalize_text(user_input)
        correct_normalized = self.normalize_text(correct_text)

        user_words = user_normalized.split()
        correct_words = correct_normalized.split()

        # 使用 difflib 进行序列比较
        matcher = difflib.SequenceMatcher(None, correct_words, user_words)

        word_results = []
        correct_count = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 正确的部分
                for word in correct_words[i1:i2]:
                    word_results.append(WordResult(word, 'correct'))
                    correct_count += 1
            elif tag == 'replace':
                # 错误替换
                for word in correct_words[i1:i2]:
                    word_results.append(WordResult(word, 'wrong'))
                # 用户多余的词
                for word in user_words[j1:j2]:
                    word_results.append(WordResult(word, 'extra'))
            elif tag == 'delete':
                # 缺少的词
                for word in correct_words[i1:i2]:
                    word_results.append(WordResult(word, 'missing'))
            elif tag == 'insert':
                # 用户多输入的词
                for word in user_words[j1:j2]:
                    word_results.append(WordResult(word, 'extra'))

        # 计算得分
        total_words = len(correct_words)
        if total_words == 0:
            score = 100
        else:
            # 基础得分 = 正确词数 / 总词数
            base_score = (correct_count / total_words) * 100

            # 惩罚多余词
            extra_penalty = len([r for r in word_results if r.status == 'extra']) * 2

            score = max(0, min(100, int(base_score - extra_penalty)))

        # 生成反馈
        feedback = self._generate_feedback(word_results, score)

        return score, word_results, feedback

    def _generate_feedback(
        self,
        word_results: List[WordResult],
        score: int
    ) -> str:
        """生成反馈文本"""
        missing = [r.word for r in word_results if r.status == 'missing']
        wrong = [r.word for r in word_results if r.status == 'wrong']
        extra = [r.word for r in word_results if r.status == 'extra']

        parts = []

        if score >= 90:
            parts.append("太棒了！几乎完美！")
        elif score >= 70:
            parts.append("不错，继续努力！")
        elif score >= 50:
            parts.append("还需要多练习哦~")
        else:
            parts.append("建议多听几遍再试一次。")

        if missing:
            parts.append(f"缺少的词：{', '.join(missing[:3])}")
        if wrong:
            parts.append(f"错误的词：{', '.join(wrong[:3])}")

        return ' '.join(parts)

    def check_partial_correct(
        self,
        user_input: str,
        correct_text: str
    ) -> Dict[str, Any]:
        """
        检查部分正确情况
        返回更详细的分析结果

        Args:
            user_input: 用户输入
            correct_text: 正确答案

        Returns:
            {
                "score": int,
                "details": List[Dict],
                "feedback": str,
                "passed": bool
            }
        """
        score, word_results, feedback = self.compare_texts(user_input, correct_text)

        # 转换为前端友好的格式
        details = []
        for r in word_results:
            details.append({
                "text": r.word,
                "correct": r.status == 'correct',
                "type": r.status
            })

        return {
            "score": score,
            "details": details,
            "feedback": feedback,
            "passed": score >= 60
        }


# 默认宽松模式校验器
dictation_checker = DictationChecker(strict_mode=False)

# 严格模式校验器
strict_checker = DictationChecker(strict_mode=True)
