"""
SM-2 间隔重复算法

用于生词本复习调度
"""
from typing import Dict


def sm2_algorithm(quality: int, ease_factor: float, interval_days: int, review_count: int):
    """
    SM-2 算法

    Args:
        quality: 回忆质量 0-5
            0 = 完全不记得
            1 = 错误，但看到答案后觉得眼熟
            2 = 错误，但看到答案后想起来了
            3 = 正确，但很费力
            4 = 正确，稍有犹豫
            5 = 完美回忆
        ease_factor: 当前易度因子 (默认 2.5)
        interval_days: 当前间隔天数
        review_count: 当前复习次数

    Returns:
        (new_ease_factor, new_interval_days, new_review_count)
    """
    if quality >= 3:
        # 回忆成功
        if review_count == 0:
            new_interval = 1
        elif review_count == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * ease_factor)
        new_review_count = review_count + 1
    else:
        # 回忆失败 - 重置
        new_interval = 1
        new_review_count = 0

    # 更新易度因子
    new_ease_factor = max(
        1.3,
        ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )

    return new_ease_factor, new_interval, new_review_count


def compute_next_intervals(
    ease_factor: float, interval_days: int, review_count: int
) -> Dict[int, int]:
    """
    计算 6 档 quality 对应的下次复习间隔天数

    用于 review-queue API 一次下发,前端只展示不重算。
    解决 VR.vue nextInterval() 与后端 SM-2 公式不一致的 P0-6 信任问题。

    Args:
        ease_factor: 当前易度因子 (默认 2.5)
        interval_days: 当前间隔天数
        review_count: 当前复习次数

    Returns:
        {quality(0-5): 下次间隔天数}, 所有值 >= 1
    """
    result: Dict[int, int] = {}
    for q in range(6):
        _, new_interval, _ = sm2_algorithm(
            quality=q,
            ease_factor=ease_factor,
            interval_days=interval_days,
            review_count=review_count,
        )
        # SM-2 返回可能 < 1 (防御性兜底)
        result[q] = max(1, new_interval)
    return result
