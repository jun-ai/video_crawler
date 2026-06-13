"""
SM-2 间隔重复算法

用于生词本复习调度
"""


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
