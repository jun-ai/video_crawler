"""
云存储服务
支持：阿里云OSS、腾讯云COS、本地存储
"""
import os
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path
from abc import ABC, abstractmethod

from app.config import settings


class StorageService(ABC):
    """存储服务抽象基类"""

    @abstractmethod
    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = None) -> str:
        """上传文件，返回文件URL"""
        pass

    @abstractmethod
    async def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """获取文件访问URL"""
        pass

    @abstractmethod
    async def delete_file(self, object_key: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    async def file_exists(self, object_key: str) -> bool:
        """检查文件是否存在"""
        pass


class LocalStorageService(StorageService):
    """本地存储服务（开发环境）"""

    def __init__(self, base_path: str, base_url: str):
        self.base_path = Path(base_path)
        self.base_url = base_url

    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = None) -> str:
        """保存文件到本地"""
        file_path = self.base_path / object_key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 异步写入文件
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write_file, file_path, file_data)

        return f"{self.base_url}/{object_key}"

    def _write_file(self, file_path: Path, data: bytes):
        with open(file_path, 'wb') as f:
            f.write(data)

    async def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """获取本地文件URL"""
        return f"{self.base_url}/{object_key}"

    async def delete_file(self, object_key: str) -> bool:
        """删除本地文件"""
        file_path = self.base_path / object_key
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def file_exists(self, object_key: str) -> bool:
        """检查本地文件是否存在"""
        return (self.base_path / object_key).exists()


class AliyunOSSService(StorageService):
    """阿里云OSS存储服务"""

    def __init__(self, access_key_id: str, access_key_secret: str,
                 endpoint: str, bucket_name: str, url_expire: int = 3600):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.url_expire = url_expire  # 签名URL有效期（秒）
        self._bucket = None

    def _get_bucket(self):
        """延迟初始化 OSS Bucket"""
        if self._bucket is None:
            try:
                import oss2
                auth = oss2.Auth(self.access_key_id, self.access_key_secret)
                self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            except ImportError:
                raise RuntimeError("请安装 oss2: pip install oss2")
        return self._bucket

    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = None) -> str:
        """上传文件到OSS，返回对象键（不是签名URL）"""
        bucket = self._get_bucket()

        # 设置文件头
        headers = {}
        if content_type:
            headers['Content-Type'] = content_type

        # 异步上传
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            bucket.put_object,
            object_key,
            file_data,
            headers
        )

        # 返回对象键，而不是签名URL
        return object_key

    async def get_file_url(self, object_key: str, expires: int = None) -> str:
        """
        生成签名访问URL（私有Bucket必须使用签名URL）

        Args:
            object_key: 对象键
            expires: URL有效期（秒），默认使用配置值

        Returns:
            带签名的临时访问URL
        """
        bucket = self._get_bucket()

        if expires is None:
            expires = self.url_expire

        # 生成签名URL（安全访问）
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            bucket.sign_url,
            'GET',
            object_key,
            expires
        )
        return url

    async def delete_file(self, object_key: str) -> bool:
        """删除OSS文件"""
        bucket = self._get_bucket()
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, bucket.delete_object, object_key)
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False

    async def file_exists(self, object_key: str) -> bool:
        """检查文件是否存在"""
        bucket = self._get_bucket()
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, bucket.object_exists, object_key)
            return True
        except:
            return False


class TencentCOSService(StorageService):
    """腾讯云COS存储服务"""

    def __init__(self, secret_id: str, secret_key: str,
                 region: str, bucket_name: str, cdn_domain: str = None):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.bucket_name = bucket_name
        self.cdn_domain = cdn_domain
        self._client = None

    def _get_client(self):
        """延迟初始化 COS Client"""
        if self._client is None:
            try:
                from qcloud_cos import CosConfig
                from qcloud_cos import CosS3Client

                config = CosConfig(
                    Region=self.region,
                    SecretId=self.secret_id,
                    SecretKey=self.secret_key
                )
                self._client = CosS3Client(config)
            except ImportError:
                raise RuntimeError("请安装 cos-python-sdk-v5: pip install cos-python-sdk-v5")
        return self._client

    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = None) -> str:
        """上传文件到COS"""
        client = self._get_client()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            client.put_object,
            self.bucket_name,
            object_key,
            file_data
        )

        return await self.get_file_url(object_key)

    async def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """生成签名访问URL"""
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{object_key}"

        client = self._get_client()
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            client.get_presigned_url,
            self.bucket_name,
            object_key,
            expires
        )
        return url

    async def delete_file(self, object_key: str) -> bool:
        """删除COS文件"""
        client = self._get_client()
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                client.delete_object,
                self.bucket_name,
                object_key
            )
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False

    async def file_exists(self, object_key: str) -> bool:
        """检查文件是否存在"""
        client = self._get_client()
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                client.head_object,
                self.bucket_name,
                object_key
            )
            return True
        except:
            return False


# ==================== 存储服务工厂 ====================

_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """获取存储服务实例（单例）"""
    global _storage_service

    if _storage_service is not None:
        return _storage_service

    storage_type = getattr(settings, 'storage_type', 'local')

    if storage_type == 'aliyun_oss':
        _storage_service = AliyunOSSService(
            access_key_id=settings.aliyun_oss_access_key_id,
            access_key_secret=settings.aliyun_oss_access_key_secret,
            endpoint=settings.aliyun_oss_endpoint,
            bucket_name=settings.aliyun_oss_bucket_name,
            url_expire=getattr(settings, 'aliyun_oss_url_expire', 3600)
        )
    elif storage_type == 'tencent_cos':
        _storage_service = TencentCOSService(
            secret_id=settings.tencent_cos_secret_id,
            secret_key=settings.tencent_cos_secret_key,
            region=settings.tencent_cos_region,
            bucket_name=settings.tencent_cos_bucket_name,
            cdn_domain=getattr(settings, 'cdn_domain', None)
        )
    else:
        # 默认使用本地存储
        _storage_service = LocalStorageService(
            base_path=getattr(settings, 'media_path', 'media'),
            base_url=getattr(settings, 'media_base_url', '/static/media')
        )

    return _storage_service


# ==================== 工具函数 ====================

def generate_object_key(file_type: str, original_filename: str, material_id: int = None) -> str:
    """
    生成云存储对象键

    Args:
        file_type: 文件类型 (video, subtitle, cover)
        original_filename: 原始文件名
        material_id: 语料ID（可选）

    Returns:
        对象键，如: videos/2024/01/abc123.mp4
    """
    # 获取文件扩展名
    ext = Path(original_filename).suffix.lower() or ''

    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = hashlib.md5(f"{original_filename}{timestamp}".encode()).hexdigest()[:8]
    new_filename = f"{timestamp}_{random_str}{ext}"

    # 按类型和日期组织目录
    date_path = datetime.now().strftime('%Y/%m')

    if file_type == 'video':
        return f"videos/{date_path}/{new_filename}"
    elif file_type == 'subtitle':
        return f"subtitles/{date_path}/{new_filename}"
    elif file_type == 'cover':
        return f"covers/{date_path}/{new_filename}"
    elif file_type == 'audio':
        return f"audio/{date_path}/{new_filename}"
    else:
        return f"others/{date_path}/{new_filename}"


async def upload_material_files(
    video_data: bytes,
    video_filename: str,
    subtitle_data: bytes,
    subtitle_filename: str,
    cover_data: bytes,
    cover_filename: str
) -> Tuple[str, str, str]:
    """
    上传语料的所有文件

    Returns:
        (video_url, subtitle_url, cover_url)
    """
    storage = get_storage_service()

    # 生成对象键
    video_key = generate_object_key('video', video_filename)
    subtitle_key = generate_object_key('subtitle', subtitle_filename)
    cover_key = generate_object_key('cover', cover_filename)

    # 并行上传
    video_url, subtitle_url, cover_url = await asyncio.gather(
        storage.upload_file(video_data, video_key, 'video/mp4'),
        storage.upload_file(subtitle_data, subtitle_key, 'text/plain'),
        storage.upload_file(cover_data, cover_key, 'image/jpeg')
    )

    return video_url, subtitle_url, cover_url
