"""
视频 URL 抓取服务
支持: YouTube / Bilibili
底层: yt-dlp (覆盖 ~1800 个站点)
"""
import os
import re
import asyncio
import logging
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    success: bool
    error: str = ""
    title: str = ""
    description: str = ""
    video_path: str = ""          # 本地文件路径
    subtitle_path: str = ""       # 本地文件路径 (SRT)
    cover_path: str = ""          # 本地文件路径 (jpg/png)
    file_size: int = 0
    duration: int = 0
    video_url: str = ""           # 原始 URL


def detect_platform(url: str) -> str:
    """识别视频平台"""
    if not url:
        return "unknown"
    u = url.lower()
    if any(x in u for x in ["youtube.com", "youtu.be", "youtube-nocookie.com"]):
        return "youtube"
    if any(x in u for x in ["bilibili.com", "b23.tv", "bili2233.cn"]):
        return "bilibili"
    return "unknown"


async def fetch_from_url(
    url: str,
    output_dir: str,
    prefer_subtitle_langs: Optional[List[str]] = None,
) -> FetchResult:
    """
    用 yt-dlp 抓取视频 + 字幕 + 封面
    返回 FetchResult (success=False 表示失败, error 有信息)

    Args:
        url: 视频 URL
        output_dir: 输出目录 (必须存在)
        prefer_subtitle_langs: 字幕语言优先级, e.g. ['en', 'zh-Hans']
    """
    if not url:
        return FetchResult(success=False, error="URL 为空")

    if prefer_subtitle_langs is None:
        prefer_subtitle_langs = ["en", "zh-Hans", "zh-CN", "zh"]

    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp 同步调用,丢到 thread pool 跑
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(
            None, _fetch_sync, url, output_dir, prefer_subtitle_langs
        )
    except Exception as e:
        logger.exception("fetch_from_url 异常")
        return FetchResult(success=False, error=f"抓取异常: {type(e).__name__}: {str(e)[:300]}")


def _fetch_sync(url: str, output_dir: str, subtitle_langs: List[str]) -> FetchResult:
    """同步抓取,在线程池里跑"""
    try:
        import yt_dlp
    except ImportError:
        return FetchResult(success=False, error="yt-dlp 未安装")

    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")
    # 字幕和封面用更明确的命名
    sub_outtmpl = os.path.join(output_dir, "%(id)s.%(lang)s.%(ext)s")
    thumb_outtmpl = os.path.join(output_dir, "%(id)s_thumb.%(ext)s")

    # 字幕下载选项: 优先手动字幕, 没有再退到自动字幕
    write_subs = []
    for lang in subtitle_langs:
        write_subs.append(f"{lang}:subs/{lang}")  # 路径里有 lang 提示

    ydl_opts = {
        # 视频: 最高 720p mp4 优先, 避免太大
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]/best",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 2,
        "socket_timeout": 30,
        # 字幕: 手动优先, 退回自动
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": subtitle_langs,
        "subtitlesformat": "srt/best",
        "convert-subs": "srt",  # vtt → srt
        # 封面
        "writethumbnail": True,
        "thumbnail_format": "jpg",
        # 写元数据
        "writedescription": False,  # 单独拉 description, 避免文件污染
        "writeinfojson": False,
    }

    result = FetchResult(success=False, video_url=url)
    info = None
    downloaded_files = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                return FetchResult(success=False, error="yt-dlp 提取信息失败", video_url=url)

            result.title = (info.get("title") or "")[:500]
            result.description = (info.get("description") or "")[:5000]
            result.duration = int(info.get("duration") or 0)

            # 找实际下载的文件
            video_id = info.get("id", "unknown")
            # 视频文件: <output_dir>/<id>.<ext>
            for ext in ["mp4", "mkv", "webm", "flv"]:
                p = os.path.join(output_dir, f"{video_id}.{ext}")
                if os.path.exists(p):
                    result.video_path = p
                    result.file_size = os.path.getsize(p)
                    break

            # 字幕: <output_dir>/<id>.<lang>.<ext>
            for lang in subtitle_langs:
                for ext in ["srt", "vtt"]:
                    p = os.path.join(output_dir, f"{video_id}.{lang}.{ext}")
                    if os.path.exists(p):
                        result.subtitle_path = p
                        break
                if result.subtitle_path:
                    break

            # 兜底: 找任何 .srt 文件
            if not result.subtitle_path:
                for fname in os.listdir(output_dir):
                    if fname.endswith(".srt"):
                        result.subtitle_path = os.path.join(output_dir, fname)
                        break

            # 封面: <output_dir>/<id>_thumb.<ext>
            for ext in ["jpg", "jpeg", "png", "webp"]:
                p = os.path.join(output_dir, f"{video_id}_thumb.{ext}")
                if os.path.exists(p):
                    result.cover_path = p
                    break

            # 兜底: 找最大图片
            if not result.cover_path:
                for fname in os.listdir(output_dir):
                    if fname.endswith((".jpg", ".jpeg", ".png", ".webp")):
                        p = os.path.join(output_dir, fname)
                        if not result.cover_path or os.path.getsize(p) > os.path.getsize(result.cover_path):
                            result.cover_path = p

        if not result.video_path:
            return FetchResult(
                success=False,
                error="视频文件下载失败,可能是地区限制 / 需要登录 / 链接已失效",
                title=result.title,
                description=result.description,
                duration=result.duration,
                video_url=url,
            )

        result.success = True
        return result

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)[:500]
        # 友好错误信息
        if "Sign in" in msg or "confirm your age" in msg:
            msg = "需要登录/年龄验证,暂不支持此类视频"
        elif "Video unavailable" in msg:
            msg = "视频不可用 (可能已删除 / 地区限制)"
        elif "HTTP Error 404" in msg:
            msg = "视频不存在 (404)"
        elif "HTTP Error 403" in msg:
            msg = "访问被拒绝 (403,可能是地区限制)"
        elif "Unable to extract" in msg:
            msg = "无法解析视频 (yt-dlp 不支持此链接)"
        logger.warning(f"yt-dlp DownloadError: {msg}")
        return FetchResult(success=False, error=f"下载失败: {msg}", title=info.get("title", "") if info else "", video_url=url)
    except Exception as e:
        logger.exception("yt-dlp 未捕获异常")
        return FetchResult(success=False, error=f"未知错误: {type(e).__name__}: {str(e)[:300]}", video_url=url)
