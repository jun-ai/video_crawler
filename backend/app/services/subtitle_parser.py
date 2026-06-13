"""
SRT 字幕解析服务
"""
import re
from typing import List, Tuple
from app.schemas.schemas import SubtitleCreate


def parse_time(time_str: str) -> int:
    """
    解析 SRT 时间格式为毫秒
    格式: 00:00:01,079 -> 1079
    """
    pattern = r"(\d{2}):(\d{2}):(\d{2}),(\d{3})"
    match = re.match(pattern, time_str.strip())
    if not match:
        return 0

    hours, minutes, seconds, milliseconds = map(int, match.groups())
    total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
    return total_ms


def parse_srt(srt_content: str, material_id: int) -> List[SubtitleCreate]:
    """
    解析 SRT 字幕文件内容

    Args:
        srt_content: SRT 文件内容
        material_id: 关联的语料 ID

    Returns:
        字幕对象列表
    """
    subtitles = []

    # 按空行分割字幕块
    blocks = re.split(r"\n\s*\n", srt_content.strip())

    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # 第一行是序号
        try:
            sequence = int(lines[0].strip())
        except ValueError:
            continue

        # 第二行是时间轴
        time_line = lines[1].strip()
        time_parts = time_line.split("-->")
        if len(time_parts) != 2:
            continue

        start_time = parse_time(time_parts[0])
        end_time = parse_time(time_parts[1])

        # 剩余行是文本
        text_en = " ".join(lines[2:]).strip()

        if text_en:
            subtitle = SubtitleCreate(
                material_id=material_id,
                sequence=sequence,
                start_time=start_time,
                end_time=end_time,
                text_en=text_en,
                text_cn=None
            )
            subtitles.append(subtitle)

    return subtitles


async def parse_srt_file(file_path: str, material_id: int) -> List[SubtitleCreate]:
    """
    从文件解析 SRT 字幕

    Args:
        file_path: SRT 文件路径
        material_id: 关联的语料 ID

    Returns:
        字幕对象列表
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return parse_srt(content, material_id)
