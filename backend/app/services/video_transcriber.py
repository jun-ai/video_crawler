"""
视频转字幕服务
使用 faster-whisper 把视频转成 SRT 字幕
- 接收视频文件路径，先用 ffmpeg 抽音轨，再喂给 faster-whisper
- 输出 SRT 文本（含时间戳）
- 默认 base 模型（int8 量化），可指定 tiny / small
- 同一时间只处理一个任务（信号量控制）
"""
import os
import re
import asyncio
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import timedelta

# 线程池 - 限制为 1，避免低配服务器过载
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="whisper")

# 模型缓存（懒加载）
_models: Dict[str, Any] = {}
_model_lock = threading.Lock()

# 同一时间只处理一个转录任务（避免 OOM）
_transcribe_semaphore = asyncio.Semaphore(1)


def _get_model(model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
    """
    懒加载 faster-whisper 模型（线程安全）

    模型大小参考（CPU 内存占用）：
      tiny:  ~75MB   速度最快
      base:  ~140MB  平衡（默认）
      small: ~460MB  质量最好
    """
    key = f"{model_size}:{device}:{compute_type}"
    if key not in _models:
        with _model_lock:
            if key not in _models:
                from faster_whisper import WhisperModel
                _models[key] = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type,
                )
    return _models[key]


def _format_timestamp(seconds: float) -> str:
    """秒数 → SRT 时间戳格式 HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _segments_to_srt(segments: List[Dict[str, Any]]) -> str:
    """faster-whisper 的 segments 列表 → SRT 文本"""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _format_timestamp(seg["start"])
        end = _format_timestamp(seg["end"])
        text = seg["text"].strip()
        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")  # 空行分隔
    return "\n".join(lines)


def _extract_audio(video_path: str, audio_path: str) -> None:
    """
    用 ffmpeg 从视频抽音轨（16kHz mono wav，whisper 最佳输入）
    """
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",               # 不要视频流
        "-acodec", "pcm_s16le",
        "-ar", "16000",      # 16kHz
        "-ac", "1",          # mono
        audio_path,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=600
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 抽音失败: {result.stderr[-500:]}")


def _get_audio_duration(audio_path: str) -> float:
    """用 ffprobe 取音频时长（秒）"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _transcribe_sync(
    video_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    同步转录流程：抽音 → 转录 → 生成 SRT
    progress_callback(percent: int, message: str) 用于上报进度
    """
    tmpdir = tempfile.mkdtemp(prefix="whisper_")
    audio_path = os.path.join(tmpdir, "audio.wav")
    try:
        # 1) 抽音
        if progress_callback:
            progress_callback(5, "正在抽音轨...")
        _extract_audio(video_path, audio_path)

        duration = _get_audio_duration(audio_path)
        if duration <= 0:
            raise RuntimeError("无法获取音频时长")

        if progress_callback:
            progress_callback(15, f"音频时长 {duration:.0f}s，加载模型...")

        # 2) 加载模型
        model = _get_model(model_size)

        if progress_callback:
            progress_callback(25, f"开始转录（{model_size} 模型，预计 {duration * 0.5:.0f}s）...")

        # 3) 转录
        segments_iter, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,         # 静音段跳过，省时间
            vad_parameters={"min_silence_duration_ms": 500},
        )

        detected_language = info.language
        total_duration = info.duration

        # 收集 segments + 进度上报
        segments = []
        for seg in segments_iter:
            segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
            })
            if progress_callback and total_duration > 0:
                pct = 25 + int((seg.end / total_duration) * 70)
                pct = min(pct, 95)
                progress_callback(pct, f"转录中 {seg.end:.0f}s / {total_duration:.0f}s")

        if progress_callback:
            progress_callback(98, f"生成 SRT（{len(segments)} 条）...")

        srt_text = _segments_to_srt(segments)

        return {
            "success": True,
            "srt": srt_text,
            "segments": segments,
            "language": detected_language,
            "duration": total_duration,
            "segment_count": len(segments),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        # 清理临时文件
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            os.rmdir(tmpdir)
        except Exception:
            pass


async def transcribe_video(
    video_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    异步转录入口（带并发控制）

    Args:
        video_path: 视频文件路径
        model_size: tiny / base / small
        language: 语言代码（None=自动检测, "en" / "zh"）
        progress_callback: 进度回调

    Returns:
        {"success": bool, "srt": str, "segments": [...], "language": str,
         "duration": float, "segment_count": int, "error": str}
    """
    async with _transcribe_semaphore:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            _transcribe_sync,
            video_path,
            model_size,
            language,
            progress_callback,
        )


def is_faster_whisper_available() -> bool:
    """检查 faster-whisper 是否可用"""
    try:
        import faster_whisper
        return True
    except ImportError:
        return False
