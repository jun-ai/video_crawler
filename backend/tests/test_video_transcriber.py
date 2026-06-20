"""视频转字幕服务单元测试。

测试 SRT 时间戳格式化和 segments → SRT 转换。
这些是纯函数，测试快速，无外部依赖（不加载 faster-whisper 模型）。
"""
import pytest

from app.services.video_transcriber import _format_timestamp, _segments_to_srt


class TestFormatTimestamp:
    """_format_timestamp: 秒数 → SRT 时间格式 HH:MM:SS,mmm"""

    def test_zero(self):
        assert _format_timestamp(0.0) == "00:00:00,000"

    def test_sub_second(self):
        assert _format_timestamp(0.5) == "00:00:00,500"

    def test_seconds_only(self):
        assert _format_timestamp(5.5) == "00:00:05,500"

    def test_minutes(self):
        assert _format_timestamp(125.123) == "00:02:05,123"

    def test_one_hour(self):
        assert _format_timestamp(3600.0) == "01:00:00,000"

    def test_complex(self):
        # 1h 2m 5.5s = 3725.5s
        assert _format_timestamp(3725.5) == "01:02:05,500"

    def test_millisecond_boundary(self):
        # 注意: 1.999 应该 round down 到 999 而不是 1.999 * 1000 = 1999
        assert _format_timestamp(1.999) == "00:00:01,999"


class TestSegmentsToSrt:
    """_segments_to_srt: faster-whisper segments → SRT 字符串"""

    def test_empty(self):
        assert _segments_to_srt([]) == ""

    def test_one_segment(self):
        segs = [{"start": 0.0, "end": 2.5, "text": "Hello world"}]
        srt = _segments_to_srt(segs)
        lines = srt.split("\n")
        # 应: "1\n00:00:00,000 --> 00:00:02,500\nHello world\n"
        assert lines[0] == "1"
        assert lines[1] == "00:00:00,000 --> 00:00:02,500"
        assert lines[2] == "Hello world"
        assert lines[3] == ""  # 末尾空行

    def test_multiple_segments(self):
        segs = [
            {"start": 0.0, "end": 1.0, "text": "First"},
            {"start": 1.5, "end": 3.0, "text": "Second"},
            {"start": 3.5, "end": 5.0, "text": "Third"}
        ]
        srt = _segments_to_srt(segs)
        # 验证序号
        assert "1\n" in srt
        assert "2\n" in srt
        assert "3\n" in srt
        # 验证时间戳
        assert "00:00:00,000 --> 00:00:01,000" in srt
        assert "00:00:01,500 --> 00:00:03,000" in srt
        assert "00:00:03,500 --> 00:00:05,000" in srt
        # 验证文本
        assert "First" in srt
        assert "Second" in srt
        assert "Third" in srt

    def test_text_whitespace_stripped(self):
        segs = [{"start": 0.0, "end": 1.0, "text": "  hello world  \n"}]
        srt = _segments_to_srt(segs)
        assert "  hello world  " not in srt
        assert "hello world" in srt

    def test_empty_text(self):
        segs = [{"start": 0.0, "end": 1.0, "text": ""}]
        srt = _segments_to_srt(segs)
        # 即使 text 为空也应输出 SRT 格式
        assert "00:00:00,000 --> 00:00:01,000" in srt