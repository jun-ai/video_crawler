"""
Whisper 本地语音识别服务
使用 OpenAI Whisper 模型进行语音识别
"""
import os
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import threading

# 线程池 - 限制为 1，避免低配服务器过载
_executor = ThreadPoolExecutor(max_workers=1)

# Whisper 模型缓存
_whisper_model = None
_model_lock = threading.Lock()

# 信号量 - 同一时间只处理一个语音请求
_whisper_semaphore = asyncio.Semaphore(1)


def _get_whisper_model():
    """懒加载 Whisper 模型（线程安全）"""
    global _whisper_model
    if _whisper_model is None:
        with _model_lock:
            if _whisper_model is None:  # 双重检查
                try:
                    import whisper
                    # 使用 tiny 模型 - 速度最快，CPU 占用最低
                    # tiny: ~39MB，最快，适合低配服务器
                    _whisper_model = whisper.load_model("tiny")
                except ImportError:
                    raise RuntimeError("请先安装 whisper: pip install openai-whisper")
    return _whisper_model


def _transcribe_sync(audio_data: bytes, language: str = "en") -> Dict[str, Any]:
    """同步方式进行语音识别"""
    try:
        model = _get_whisper_model()

        # 保存临时文件（whisper需要文件路径）
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            # 执行识别
            result = model.transcribe(
                temp_path,
                language=language,
                fp16=False  # CPU 模式下使用 fp32
            )

            text = result.get("text", "").strip()

            return {
                "success": True,
                "text": text,
                "confidence": 0.9,  # Whisper 不返回置信度，给个默认值
                "language": result.get("language", language)
            }
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "confidence": 0,
            "error": str(e)
        }


async def transcribe_with_whisper(
    audio_data: bytes,
    language: str = "en"
) -> Dict[str, Any]:
    """
    使用 Whisper 进行语音识别（限流，同一时间只处理一个请求）

    Args:
        audio_data: 音频数据（支持多种格式）
        language: 语言代码 (en, zh, etc.)

    Returns:
        {
            "success": bool,
            "text": str,
            "confidence": float,
            "error": str
        }
    """
    async with _whisper_semaphore:  # 限制并发
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            _transcribe_sync,
            audio_data,
            language
        )


def is_whisper_available() -> bool:
    """检查 Whisper 是否可用"""
    try:
        import whisper
        return True
    except ImportError:
        return False
