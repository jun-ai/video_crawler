"""
视频抓取服务

支持平台:
- Bilibili (B站): 走官方 API(api.bilibili.com),绕过 anti-bot
- YouTube: GFW 拦截 ECS 直连,需要手动下载 + batch-upload 上传

GFW 限制:
- ECS(阿里云 中国) 无法访问 YouTube
- B站网页有 anti-bot(openresty X-BILI-SEC-TOKEN),但 API 不限
"""
import asyncio
import json
import logging
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List

import httpx

logger = logging.getLogger(__name__)

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class FetchResult:
    """抓取结果"""
    title: str = ""
    uploader: str = ""
    duration: int = 0
    description: str = ""
    video_path: str = ""
    subtitle_path: str = ""
    cover_path: str = ""
    video_url: str = ""
    thumbnail_url: str = ""
    file_size: int = 0
    subtitle_count: int = 0
    error: str = ""
    success: bool = False
    source_url: str = ""
    need_manual: bool = False   # 需要用户手动下载(如 YouTube)


def detect_platform(url: str) -> str:
    """检测视频平台"""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "bilibili.com" in url_lower or "b23.tv" in url_lower:
        return "bilibili"
    return "unknown"


# ========== B站(Bilibili) ==========

BV_PATTERN = re.compile(r"BV([A-Za-z0-9]+)")
AV_PATTERN = re.compile(r"/av(\d+)")


def extract_bvid(url: str) -> Optional[str]:
    """从 URL 提取 BV 号"""
    m = BV_PATTERN.search(url)
    if m:
        return "BV" + m.group(1)
    return None


async def _bili_get_info(client: httpx.AsyncClient, bvid: str) -> Dict[str, Any]:
    """获取 B站视频元数据"""
    resp = await client.get(
        "https://api.bilibili.com/x/web-interface/view",
        params={"bvid": bvid},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"B站 API 错误: {data.get('message', 'unknown')}")
    d = data["data"]
    return {
        "title": d.get("title", ""),
        "uploader": d.get("owner", {}).get("name", ""),
        "duration": d.get("duration", 0),
        "description": (d.get("desc") or "")[:1000],
        "thumbnail": d.get("pic", ""),
        "cid": d.get("cid"),
        "bvid": bvid,
        "aid": d.get("aid"),
    }


async def _bili_get_playurl(client: httpx.AsyncClient, bvid: str, cid: int, qn: int = 16) -> tuple[str, int]:
    """
    获取 B站视频播放 URL
    qn: 画质代码, 16=360p 流畅, 32=480p 清晰, 64=720p 高清, 80=1080p
    默认 16 (360p) 控制文件大小
    """
    resp = await client.get(
        "https://api.bilibili.com/x/player/playurl",
        params={
            "bvid": bvid,
            "cid": cid,
            "qn": qn,
            "fnval": 1,
            "fnver": 0,
            "fourk": 1,
            "platform": "html5",
            "high_quality": 1,
        },
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"B站 playurl API 错误: {data.get('message', 'unknown')}")
    durls = data["data"]["durl"]
    if not durls:
        raise RuntimeError("未找到视频流")
    return durls[0]["url"], durls[0].get("size", 0)


async def _bili_get_subtitles(client: httpx.AsyncClient, bvid: str, cid: int) -> List[Dict[str, Any]]:
    """
    获取 B站字幕列表(返回 [{lan_doc, url}])
    """
    resp = await client.get(
        "https://api.bilibili.com/x/player/v2",
        params={"bvid": bvid, "cid": cid},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        return []
    subtitles_info = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
    return [
        {
            "lan": s.get("lan", ""),
            "lan_doc": s.get("lan_doc", ""),
            "url": "https:" + s["subtitle_url"] if s.get("subtitle_url", "").startswith("//") else s.get("subtitle_url", ""),
        }
        for s in subtitles_info
    ]


def _json_subtitle_to_srt(json_content: str) -> str:
    """B站字幕 JSON 转 SRT 格式"""
    data = json.loads(json_content)
    lines = []
    for i, item in enumerate(data.get("body", []), 1):
        start = item.get("from", 0)
        end = item.get("to", 0)
        content = item.get("content", "")
        # SRT 时间格式: HH:MM:SS,mmm
        def fmt_time(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec - int(sec)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines.append(str(i))
        lines.append(f"{fmt_time(start)} --> {fmt_time(end)}")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


async def fetch_bilibili(
    url: str,
    output_dir: str,
    prefer_subtitle_langs: List[str] = None,
    max_quality: int = 32,
) -> FetchResult:
    """
    通过 B站官方 API 抓取视频 + 字幕 + 封面

    Args:
        url: B站视频 URL
        output_dir: 本地存储目录
        prefer_subtitle_langs: 优先字幕语言,默认 ['ai-zh', 'zh-CN', 'en']
        max_quality: 画质上限 16/32/64/80, 默认 32 (480p)
    """
    if prefer_subtitle_langs is None:
        prefer_subtitle_langs = ["en", "en-US", "zh-CN", "zh-Hans", "ai-zh"]

    bvid = extract_bvid(url)
    if not bvid:
        return FetchResult(
            error="无法从 URL 提取 BV 号,请确认是 B站视频链接",
            source_url=url,
        )

    os.makedirs(output_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:12]

    async with httpx.AsyncClient(headers=API_HEADERS, follow_redirects=True, timeout=60) as client:
        # 1. 元数据
        try:
            info = await _bili_get_info(client, bvid)
        except Exception as e:
            return FetchResult(error=f"获取视频信息失败: {e}", source_url=url)

        result = FetchResult(
            title=info["title"],
            uploader=info["uploader"],
            duration=info["duration"],
            description=info["description"],
            thumbnail_url=info["thumbnail"],
            video_url=url,
            source_url=url,
        )

        # 2. 视频下载
        try:
            video_url, file_size = await _bili_get_playurl(client, bvid, info["cid"], qn=max_quality)
            result.video_path = os.path.join(output_dir, f"{unique_id}.mp4")
            if file_size and file_size > 0:
                result.file_size = int(file_size)

            async with client.stream("GET", video_url) as resp:
                resp.raise_for_status()
                with open(result.video_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                        f.write(chunk)
                        if result.file_size == 0:
                            result.file_size = file_size
                        # 安全限制 500MB
                        if os.path.getsize(result.video_path) > 500 * 1024 * 1024:
                            f.close()
                            os.unlink(result.video_path)
                            return FetchResult(
                                error="视频文件超过 500MB 限制,请用 batch-upload 手动上传",
                                source_url=url,
                            )
        except Exception as e:
            return FetchResult(
                title=info["title"], uploader=info["uploader"],
                error=f"下载视频失败: {type(e).__name__}: {e}",
                source_url=url,
            )

        # 3. 封面
        try:
            cover_resp = await client.get(info["thumbnail"])
            cover_resp.raise_for_status()
            ext = ".jpg"
            if ".png" in info["thumbnail"]:
                ext = ".png"
            result.cover_path = os.path.join(output_dir, f"{unique_id}{ext}")
            with open(result.cover_path, "wb") as f:
                f.write(cover_resp.content)
        except Exception as e:
            logger.warning(f"[Bilibili] 封面下载失败: {e}")

        # 4. 字幕
        try:
            subtitles = await _bili_get_subtitles(client, bvid, info["cid"])
            # 按优先级找
            chosen = None
            for lang in prefer_subtitle_langs:
                for s in subtitles:
                    if s["lan"] == lang or s["lan_doc"].lower() == lang.lower():
                        chosen = s
                        break
                if chosen:
                    break
            if not chosen and subtitles:
                chosen = subtitles[0]

            if chosen:
                sub_url = chosen["url"]
                sub_resp = await client.get(sub_url)
                sub_resp.raise_for_status()
                sub_content = sub_resp.text

                # B站字幕是 JSON, 转 SRT
                try:
                    srt_content = _json_subtitle_to_srt(sub_content)
                except Exception:
                    srt_content = sub_content

                result.subtitle_path = os.path.join(output_dir, f"{unique_id}_{chosen['lan']}.srt")
                with open(result.subtitle_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)

                # 统计条目数
                result.subtitle_count = sum(
                    1 for line in srt_content.split("\n") if line.strip().isdigit()
                )
        except Exception as e:
            logger.warning(f"[Bilibili] 字幕获取失败: {e}")

    if not result.video_path:
        result.error = "未获取到视频文件"
        return result

    result.success = True
    return result


# ========== YouTube ==========

async def fetch_youtube(url: str, output_dir: str, **kwargs) -> FetchResult:
    """
    YouTube 占位 - GFW 拦截 ECS,返回手动下载提示

    用户可用工具:
    - cobalt.tools / cobalt (开源)
    - y2mate.com / ssyoutube.com / savefrom.net 等
    - yt-dlp 本地 + cookies

    然后用现有的 POST /api/admin/materials/batch-upload 上传
    """
    return FetchResult(
        error=(
            "YouTube 视频 ECS 无法直接抓取(GFW 拦截)。\n"
            "请用浏览器(可访问 YouTube)下载后,使用批量上传功能:\n"
            "  POST /api/admin/materials/batch-upload\n"
            "推荐工具:\n"
            "  - cobalt.tools (在线 API,无需登录)\n"
            "  - savefrom.net / y2mate.com (网页下载)\n"
            "  - yt-dlp + cookies (本地)"
        ),
        source_url=url,
        need_manual=True,
    )


# ========== 统一入口 ==========

async def fetch_from_url(
    url: str,
    output_dir: str,
    prefer_subtitle_langs: List[str] = None,
    **kwargs,
) -> FetchResult:
    """统一抓取入口 - 根据平台分发"""
    platform = detect_platform(url)
    if platform == "bilibili":
        return await fetch_bilibili(url, output_dir, prefer_subtitle_langs, **kwargs)
    elif platform == "youtube":
        return await fetch_youtube(url, output_dir, **kwargs)
    else:
        return FetchResult(
            error="不支持的 URL,目前支持 YouTube(手动) / Bilibili(自动)",
            source_url=url,
        )