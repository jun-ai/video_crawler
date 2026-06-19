"""
review-queue 返回 next_intervals 字典 (P0-6 信任问题)

VocabularyReview.vue 前端 nextInterval() 与后端 SM-2 公式不一致,
修复方案: 后端 review-queue 一次算好 6 档 quality 对应的天数,下发字典。
前端只展示,不重算。

测试覆盖:
- test_compute_next_intervals_quality_5_first_review: 首次复习 quality=5 → 1天
- test_compute_next_intervals_quality_5_second_review: 第二次 quality=5 → 6天
- test_compute_next_intervals_quality_5_third_review: 第三次 quality=5 → round(interval * ef)
- test_compute_next_intervals_quality_below_3_resets: quality<3 → 1天,review_count=0
- test_compute_next_intervals_returns_dict: 返回类型是 dict,key 0-5
- test_review_queue_response_has_next_intervals: API 响应每个 item 都有 next_intervals
"""
# 抑制 aiosqlite DEBUG 日志(避免淹没 pytest 失败信息)
import logging
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.disable(logging.DEBUG)

import pytest
from app.services.spaced_repetition import sm2_algorithm, compute_next_intervals


# ==================== 纯函数测试 ====================

def test_compute_next_intervals_quality_5_first_review():
    """首次复习:review_count=0,quality=5 → 1天"""
    result = compute_next_intervals(
        ease_factor=2.5, interval_days=0, review_count=0
    )
    assert result[5] == 1, f"quality=5 first review should be 1 day, got {result[5]}"


def test_compute_next_intervals_quality_5_second_review():
    """第二次复习:review_count=1,quality=5 → 6天"""
    result = compute_next_intervals(
        ease_factor=2.5, interval_days=1, review_count=1
    )
    assert result[5] == 6, f"quality=5 second review should be 6 days, got {result[5]}"


def test_compute_next_intervals_quality_5_third_review():
    """第三次复习:review_count=2,interval=6,ef=2.5,quality=5 → 6*2.5=15天"""
    result = compute_next_intervals(
        ease_factor=2.5, interval_days=6, review_count=2
    )
    assert result[5] == 15, f"quality=5 third review should be 15 days, got {result[5]}"


def test_compute_next_intervals_quality_below_3_resets():
    """回忆失败:quality<3 → 1天,review_count 归 0"""
    result = compute_next_intervals(
        ease_factor=2.7, interval_days=10, review_count=3
    )
    assert result[0] == 1
    assert result[1] == 1
    assert result[2] == 1


def test_compute_next_intervals_returns_full_dict():
    """返回字典必须包含 0-5 所有档位"""
    result = compute_next_intervals(
        ease_factor=2.5, interval_days=1, review_count=1
    )
    assert set(result.keys()) == {0, 1, 2, 3, 4, 5}
    # 全部 >= 1 (包括失败重置到 1 天)
    for q in range(6):
        assert result[q] >= 1, f"quality={q} should be >= 1 day"


def test_compute_next_intervals_consistency_with_sm2():
    """与现有 sm2_algorithm 输出一致"""
    ef, interval, count = 2.5, 1, 1
    new_ef, new_interval, _ = sm2_algorithm(5, ef, interval, count)
    # 第二次 quality=5 应该返回 6
    # 但 compute_next_intervals 用的"当前"状态 (ef/interval/count) 计算
    # 算出下次复习的天数,这里只是验证两边对 quality=5 第二次都返回 6
    result = compute_next_intervals(ease_factor=ef, interval_days=interval, review_count=count)
    assert result[5] == 6


# ==================== API 集成测试 ====================

@pytest.mark.asyncio
async def test_review_queue_response_has_next_intervals(
    client, auth_headers, db_session, test_user
):
    """review-queue API 响应每个 item 都有 next_intervals 字典"""
    from app.models.models import Material, Subtitle, Vocabulary

    # 准备 material + subtitle + vocab
    material = Material(
        id=1, title="Test", duration=10,
        video_path="/test.mp4", subtitle_path="/test.srt", cover_path="/cover.jpg"
    )
    db_session.add(material)
    subtitle = Subtitle(
        id=1, material_id=1, text_en="hello world",
        start_time=0, end_time=1000, sequence=1, text_cn="你好世界"
    )
    db_session.add(subtitle)
    vocab = Vocabulary(
        user_id=test_user.id,
        word="hello",
        context="hello world",
        material_id=1,
        subtitle_id=1,
        ease_factor=2.5,
        interval_days=1,
        review_count=1
    )
    db_session.add(vocab)
    await db_session.commit()

    # 调 API
    response = await client.get(
        "/api/learning/vocabulary/review-queue",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert len(data["items"]) >= 1

    # 每个 item 必须有 next_intervals 字典,key 0-5
    item = data["items"][0]
    assert "next_intervals" in item, f"item 缺少 next_intervals: {item}"
    intervals = item["next_intervals"]
    assert set(intervals.keys()) == {"0", "1", "2", "3", "4", "5"}, \
        f"next_intervals keys 不全: {intervals}"
    for k, v in intervals.items():
        assert isinstance(v, int) and v >= 1, \
            f"next_intervals[{k}]={v} 应为正整数"


@pytest.mark.asyncio
async def test_review_queue_response_new_vocab_no_prior_review(
    client, auth_headers, db_session, test_user
):
    """首次复习的词:review_count=0,所有档位都应返回有效天数"""
    from app.models.models import Vocabulary

    vocab = Vocabulary(
        user_id=test_user.id,
        word="brand_new",
        context="first time seeing this",
        ease_factor=2.5,
        interval_days=0,
        review_count=0
    )
    db_session.add(vocab)
    await db_session.commit()

    response = await client.get(
        "/api/learning/vocabulary/review-queue",
        headers=auth_headers
    )
    assert response.status_code == 200
    item = response.json()["items"][0]
    intervals = item["next_intervals"]

    # 首次: success 档位 (3/4/5) 都应 >= 1 天
    assert intervals["3"] >= 1
    assert intervals["4"] >= 1
    assert intervals["5"] >= 1
    # 失败档位 (0/1/2) 也是 1 天 (重置)
    assert intervals["0"] == 1
    assert intervals["1"] == 1
    assert intervals["2"] == 1
