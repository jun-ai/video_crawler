from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

# 获取 .env 文件的绝对路径
ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # 数据库 (MySQL)
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/english_learning"

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # ==================== 文件存储配置 ====================
    # 存储类型: local, aliyun_oss, tencent_cos
    storage_type: str = "local"

    # 本地存储配置
    upload_dir: str = "../data/materials"
    media_base_url: str = "/static"  # 本地存储时的基础URL

    # 阿里云OSS配置
    aliyun_oss_access_key_id: str = ""
    aliyun_oss_access_key_secret: str = ""
    aliyun_oss_endpoint: str = ""  # 如: oss-cn-hangzhou.aliyuncs.com
    aliyun_oss_bucket_name: str = ""
    aliyun_oss_url_expire: int = 3600  # 签名URL有效期（秒），默认1小时

    # 腾讯云COS配置
    tencent_cos_secret_id: str = ""
    tencent_cos_secret_key: str = ""
    tencent_cos_region: str = ""  # 如: ap-shanghai
    tencent_cos_bucket_name: str = ""

    # CDN域名（可选，用于加速访问）
    cdn_domain: str = ""  # 如: cdn.yourdomain.com

    # 视频流基础URL（生产环境使用 CDN 或域名，替代 localhost）
    video_base_url: str = ""  # 如: https://cdn.yourdomain.com 或留空自动检测

    # ==================== 服务配置 ====================
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: str = "*"  # 逗号分隔的域名，或 "*" 表示全部

    # ==================== AI API配置 ====================
    # 多个 provider,按优先级 fallback(OpenAI 兼容协议)
    # DeepSeek (默认)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 智谱 GLM — Anthropic 兼容协议(https://open.bigmodel.cn/api/anthropic)
    # 用 ccswitch 同款 5.1 key 直连也可(实测 200 OK)
    glm_api_key: str = ""
    glm_base_url: str = "https://open.bigmodel.cn/api/anthropic"
    glm_model: str = "glm-4.5"

    # 月之暗面 MiniMax / Moonshot — Anthropic 兼容协议(https://api.minimaxi.com/anthropic)
    # ccswitch 的 sk-cp- key 需要走 ccswitch 代理,直连 401
    # 留空此字段 = 自动跳过这个 provider
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimaxi.com/anthropic"
    minimax_model: str = "MiniMax-M3"

    # 讯飞语音识别 API
    xunfei_app_id: str = ""
    xunfei_api_key: str = ""
    xunfei_api_secret: str = ""

    class Config:
        env_file = str(ENV_FILE_PATH)
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# 确保上传目录存在（本地存储时）
if settings.storage_type == "local":
    os.makedirs(settings.upload_dir, exist_ok=True)
