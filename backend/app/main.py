"""
英语口语学习网站 - 后端 API
"""
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os
import re
import httpx
import oss2
from urllib.parse import urlencode
import logging
import time

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import init_db
from app.routers import auth, materials, learning, favorites, admin, tags, announcements
from app.utils.logger import setup_logging, get_logger
from app.utils.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware

# 初始化日志系统
setup_logging(debug=settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    logger.info(f"服务启动成功，监听 {settings.host}:{settings.port}")
    yield
    # 关闭时清理资源
    logger.info("应用正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="英语口语学习 API",
    description="基于真实视频语料库的英语口语学习平台",
    version="1.0.0",
    lifespan=lifespan
)

# 限流配置
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 配置
cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流中间件（放在 CORS 之后）
app.add_middleware(SlowAPIMiddleware)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求的日志"""
    start_time = time.time()

    # 记录请求
    logger.info(f"Request: {request.client.host if request.client else 'unknown'} -> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")

        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}")
        raise

# 静态文件服务 - 挂载项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


# 专门的视频流端点，支持 Range 请求
@app.get("/video/{filename:path}")
async def stream_video(filename: str, request: Request):
    """视频流端点，支持 Range 请求"""
    video_path = PROJECT_ROOT / filename

    if not video_path.exists():
        return Response(status_code=404)

    file_size = video_path.stat().st_size
    range_header = request.headers.get("range")

    # MIME 类型
    content_type = "video/mp4"

    if range_header:
        # 解析 Range 头: bytes=start-end
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1

            # 确保范围有效
            if start >= file_size or end >= file_size:
                return Response(status_code=416)

            chunk_size = end - start + 1

            def iterfile():
                with open(video_path, "rb") as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        read_size = min(8192, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
            }

            return StreamingResponse(
                iterfile(),
                status_code=206,
                media_type=content_type,
                headers=headers
            )

    # 没有 Range 头，返回整个文件
    def iterfile():
        with open(video_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
        }
    )


# OSS 代理端点 - 解决跨域问题
# Lazy-init OSS bucket client for proxy (private bucket, use SDK signed request)
_oss_proxy_bucket = None


def _get_oss_proxy_bucket():
    """获取 OSS Bucket 客户端 (用于 proxy, 用 SDK 签名访问私有 bucket)"""
    global _oss_proxy_bucket
    if _oss_proxy_bucket is None:
        auth = oss2.Auth(
            settings.aliyun_oss_access_key_id,
            settings.aliyun_oss_access_key_secret,
        )
        _oss_proxy_bucket = oss2.Bucket(
            auth,
            settings.aliyun_oss_endpoint,
            settings.aliyun_oss_bucket_name,
        )
    return _oss_proxy_bucket


def _parse_range_header(range_header: str):
    """解析 Range 头 (e.g. 'bytes=0-1023') -> (start, end) 或 None"""
    try:
        if not range_header.startswith("bytes="):
            return None
        spec = range_header[6:].strip()
        if "," in spec:
            return None  # 多段 range, 不支持
        if "-" not in spec:
            return None
        start_s, end_s = spec.split("-", 1)
        start = int(start_s) if start_s else None
        end = int(end_s) if end_s else None
        if start is None and end is not None:
            # suffix 模式: last N bytes, oss2 不直接支持, 退化
            return None
        if start is not None and end is not None:
            return (start, end)
        if start is not None:
            return (start,)
    except Exception:
        return None
    return None


@app.api_route("/oss-proxy/{path:path}", methods=["GET", "HEAD"])
async def proxy_oss(path: str, request: Request):
    """
    代理 OSS 资源请求 (私有 bucket)
    - 使用 oss2 SDK 签名访问 (避免 CDN/匿名访问 403)
    - 支持 Range 请求 (视频拖动)
    - 流式返回
    """
    range_header = request.headers.get("range")
    byte_range = _parse_range_header(range_header) if range_header else None

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: _get_oss_proxy_bucket().get_object(path, byte_range=byte_range),
        )
    except oss2.exceptions.NoSuchKey:
        return Response(status_code=404)
    except Exception as e:
        logger.error(f"OSS proxy error: {e}")
        return Response(status_code=502, content=f"Failed to fetch from OSS: {e}")

    # 准备响应头
    allowed_headers = [
        "content-type", "content-length", "content-range",
        "accept-ranges", "etag", "last-modified", "cache-control",
    ]
    response_headers = dict(result.headers)
    filtered_headers = {
        k: v for k, v in response_headers.items() if k.lower() in allowed_headers
    }
    filtered_headers["Access-Control-Allow-Origin"] = "*"
    filtered_headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    filtered_headers["Access-Control-Allow-Headers"] = "Range, Content-Type"

    async def stream_response():
        # result.stream 是同步生成器; 每次读一块后让出 event loop
        for chunk in result.stream(8192):
            yield chunk
            await asyncio.sleep(0)

    return StreamingResponse(
        stream_response(),
        status_code=result.status,
        headers=filtered_headers,
        media_type=result.headers.get("content-type", "application/octet-stream"),
    )


app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT)), name="static")

# 注册路由
app.include_router(auth.router)
app.include_router(materials.router)
app.include_router(learning.router)
app.include_router(favorites.router)
app.include_router(admin.router)
app.include_router(tags.router)
app.include_router(announcements.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "英语口语学习 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
