"""
音频格式转换服务
将 webm 转换为 PCM/WAV 格式
"""
import subprocess
import tempfile
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

# 使用 imageio-ffmpeg 提供的 ffmpeg 二进制文件
# 这样不需要系统安装 ffmpeg，部署更方便
import imageio_ffmpeg

# 获取 ffmpeg 可执行文件路径
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# 线程池用于执行阻塞的 ffmpeg 命令
_executor = ThreadPoolExecutor(max_workers=2)


def _convert_webm_to_pcm_sync(webm_data: bytes, sample_rate: int = 16000) -> bytes:
    """
    同步方式将 webm 音频转换为 PCM 格式
    使用 ffmpeg 进行转换
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
        input_file.write(webm_data)
        input_path = input_file.name

    output_path = input_path.replace('.webm', '.pcm')

    try:
        # ffmpeg 转换命令
        cmd = [
            FFMPEG_PATH,
            '-y',  # 覆盖输出文件
            '-i', input_path,
            '-f', 's16le',  # PCM signed 16-bit little-endian
            '-acodec', 'pcm_s16le',
            '-ar', str(sample_rate),  # 采样率
            '-ac', '1',  # 单声道
            output_path
        ]

        process = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )

        if process.returncode != 0:
            error_msg = process.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"FFmpeg 转换失败: {error_msg}")

        with open(output_path, 'rb') as f:
            return f.read()

    finally:
        # 清理临时文件
        try:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass


def _convert_webm_to_wav_sync(webm_data: bytes, sample_rate: int = 16000) -> bytes:
    """
    同步方式将 webm 音频转换为 WAV 格式（Whisper推荐格式）
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
        input_file.write(webm_data)
        input_path = input_file.name

    output_path = input_path.replace('.webm', '.wav')

    try:
        cmd = [
            FFMPEG_PATH,
            '-y',
            '-i', input_path,
            '-ar', str(sample_rate),
            '-ac', '1',
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            output_path
        ]

        process = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )

        if process.returncode != 0:
            error_msg = process.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"FFmpeg 转换失败: {error_msg}")

        with open(output_path, 'rb') as f:
            return f.read()

    finally:
        try:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass


async def convert_webm_to_pcm(webm_data: bytes, sample_rate: int = 16000) -> bytes:
    """
    异步方式将 webm 音频转换为 PCM 格式

    Args:
        webm_data: webm 格式的音频数据
        sample_rate: 目标采样率，默认 16000

    Returns:
        PCM 格式的音频数据
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _convert_webm_to_pcm_sync,
        webm_data,
        sample_rate
    )


async def convert_webm_to_wav(webm_data: bytes, sample_rate: int = 16000) -> bytes:
    """
    异步方式将 webm 音频转换为 WAV 格式（Whisper推荐）

    Args:
        webm_data: webm 格式的音频数据
        sample_rate: 目标采样率，默认 16000

    Returns:
        WAV 格式的音频数据
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _convert_webm_to_wav_sync,
        webm_data,
        sample_rate
    )


def check_ffmpeg_available() -> bool:
    """检查 ffmpeg 是否可用"""
    try:
        result = subprocess.run(
            [FFMPEG_PATH, '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

