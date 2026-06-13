"""
语音识别服务
支持多种语音识别方案：
1. Whisper（本地，免费，推荐）
2. 讯飞语音识别 API（云端，需配置）
"""
import base64
import hmac
import hashlib
import json
import asyncio
import websockets
from datetime import datetime
from urllib.parse import urlencode
from typing import Dict, Any, Optional
from app.config import settings

# 导入 Whisper 服务
try:
    from app.services.whisper_speech import transcribe_with_whisper, is_whisper_available
    WHISPER_AVAILABLE = is_whisper_available()
    print(f"[语音识别] Whisper 可用: {WHISPER_AVAILABLE}")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"[语音识别] Whisper 导入失败: {e}")


class XunfeiSpeechService:
    """讯飞语音识别服务 - 基于官方WebSocket API"""

    def __init__(self):
        self.app_id = settings.xunfei_app_id
        self.api_key = settings.xunfei_api_key
        self.api_secret = settings.xunfei_api_secret
        self.ws_url = "wss://iat-api.xfyun.cn/v2/iat"

    def _create_url(self) -> str:
        """生成带鉴权的 WebSocket URL"""
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

        signature_origin = f"host: ws-api.xfyun.cn\n" \
                          f"date: {date}\n" \
                          f"GET /v2/iat HTTP/1.1"

        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", ' \
                              f'algorithm="hmac-sha256", ' \
                              f'headers="host date request-line", ' \
                              f'signature="{signature}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        params = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }

        return self.ws_url + "?" + urlencode(params)

    async def recognize(self, audio_data: bytes, language: str = "en") -> Dict[str, Any]:
        """使用讯飞 API 进行语音识别"""
        if not self.app_id or not self.api_key or not self.api_secret:
            return {
                "success": False,
                "text": "",
                "confidence": 0,
                "error": "讯飞 API 未配置，请在 .env 中设置 XUNFEI_APP_ID, XUNFEI_API_KEY, XUNFEI_API_SECRET"
            }

        try:
            url = self._create_url()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            result_text = []

            async with websockets.connect(url, close_timeout=10) as ws:
                # 分帧发送音频数据
                frame_size = 1280
                audio_len = len(audio_base64)
                total_frames = max(1, (audio_len + frame_size - 1) // frame_size)

                for i in range(total_frames):
                    # 确定帧状态
                    if total_frames == 1:
                        status = 2  # 单帧情况，直接发送最后一帧
                    elif i == 0:
                        status = 0  # 首帧
                    elif i == total_frames - 1:
                        status = 2  # 最后一帧
                    else:
                        status = 1  # 中间帧

                    # 获取当前帧数据
                    start = i * frame_size
                    end = min(start + frame_size, audio_len)
                    frame_data = audio_base64[start:end]

                    # 构建请求
                    frame_payload = {
                        "common": {"app_id": self.app_id},
                        "business": {
                            "language": "en_us" if language == "en" else "zh_cn",
                            "domain": "iat",
                            "vad_eos": 2000,
                            "dwa": "wpgs"
                        },
                        "data": {
                            "status": status,
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": frame_data
                        }
                    }

                    await ws.send(json.dumps(frame_payload))

                    # 接收中间结果
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2)
                        data = json.loads(response)

                        if data.get("code", 0) != 0:
                            return {
                                "success": False,
                                "text": "",
                                "confidence": 0,
                                "error": f"讯飞API错误({data.get('code')}): {data.get('message', '未知错误')}"
                            }

                        # 提取识别文字
                        self._extract_text(data, result_text)

                    except asyncio.TimeoutError:
                        pass

                    # 帧间隔
                    if status != 2:
                        await asyncio.sleep(0.04)

                # 等待最终结果
                for _ in range(30):
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1)
                        data = json.loads(response)

                        if data.get("code", 0) != 0:
                            break

                        self._extract_text(data, result_text)

                        # 检查是否结束
                        result = data.get("data", {}).get("result", {})
                        if result.get("ls") or data.get("status") == 2:
                            break

                    except asyncio.TimeoutError:
                        break

            final_text = "".join(result_text).strip()

            if not final_text:
                return {
                    "success": False,
                    "text": "",
                    "confidence": 0,
                    "error": "未识别到语音内容"
                }

            return {
                "success": True,
                "text": final_text,
                "confidence": 0.9
            }

        except websockets.exceptions.WebSocketException as e:
            return {
                "success": False,
                "text": "",
                "confidence": 0,
                "error": f"WebSocket连接错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "confidence": 0,
                "error": f"讯飞识别失败: {str(e)}"
            }

    def _extract_text(self, data: dict, result_text: list):
        """从响应中提取识别文字"""
        try:
            result = data.get("data", {}).get("result", {})
            ws_list = result.get("ws", [])

            for ws_item in ws_list:
                for cw in ws_item.get("cw", []):
                    word = cw.get("w", "")
                    if word:
                        result_text.append(word)
        except Exception:
            pass


class SpeechRecognitionService:
    """语音识别服务类"""

    def __init__(self):
        self.xunfei = XunfeiSpeechService()
        self.use_whisper = WHISPER_AVAILABLE
        print(f"[语音识别] 服务初始化, 使用 Whisper: {self.use_whisper}")

    async def recognize_audio(
        self,
        audio_data: bytes,
        audio_format: str = "pcm",
        rate: int = 16000,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        语音识别主入口

        Args:
            audio_data: 音频二进制数据
            audio_format: 音频格式 (pcm, wav, amr, webm)
            rate: 采样率
            language: 语言 (en, zh)

        Returns:
            {
                "success": bool,
                "text": str,  # 识别结果
                "confidence": float,  # 置信度
                "error": str  # 错误信息
            }
        """
        # 优先使用 Whisper
        if self.use_whisper:
            return await transcribe_with_whisper(audio_data, language)

        # 回退到讯飞 API
        return await self.xunfei.recognize(audio_data, language)


# 单例
speech_service = SpeechRecognitionService()
