"""
英语口语学习网站 - 后端 API
"""
import asyncio
from typing import Annotated
from fastapi import FastAPI, Request, Response, Depends
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
from app.models.models import User
from app.routers import auth, materials, learning, favorites, admin, tags, announcements
from app.routers.auth import get_current_user
from app.utils.logger import setup_logging, get_logger
from app.utils.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware

# P0 商业化安全: 生产环境关闭 /docs /openapi.json /redoc
# (任何人都能看到完整 API schema = 把后门图纸公开)
# 用 ENV 控制: ENABLE_API_DOCS=true 才开 (开发环境)
_enable_docs = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"
_docs_url = "/docs" if _enable_docs else None
_redoc_url = "/redoc" if _enable_docs else None
_openapi_url = "/openapi.json" if _enable_docs else None

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

    # Phase 30 P0-5: secret_key 必须从环境变量注入, 不允许默认值
    if settings.secret_key in ("", "dev-secret-key-change-in-production"):
        raise RuntimeError(
            "SECRET_KEY 未设置或仍为默认值. "
            "生产环境必须从环境变量注入高熵密钥, 否则 JWT 可被伪造."
        )
    logger.info(f"secret_key 校验通过 (长度={len(settings.secret_key)})")

    logger.info(f"服务启动成功，监听 {settings.host}:{settings.port}")
    yield
    # 关闭时清理资源
    logger.info("应用正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="英语口语学习 API",
    description="基于真实视频语料库的英语口语学习平台",
    version="1.0.0",
    lifespan=lifespan,
    # P0 商业化安全: 生产环境关闭 API 文档 (由上面 _enable_docs 决定)
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url
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

# 静态文件服务 - 限定到 materials 目录 (避免把整个项目根暴露给公网)
# Phase 30 P0-1 (7-19 二次修复): 之前用 settings.upload_dir 拼路径, 容器内 resolve 错位
# 容器内 bind mount 路径固定 /app/data/materials (compose yml: ./data/materials:/app/data/materials)
# 本地开发也走 /app/data/materials (跟容器一致, 行为统一)
PROJECT_ROOT = Path(__file__).parent.parent.parent
MATERIALS_ROOT = Path("/app/data/materials").resolve()

if not MATERIALS_ROOT.is_dir():
    # 本地开发时 /app 不存在, fallback 到 PROJECT_ROOT/data/materials
    _local_fallback = (PROJECT_ROOT / "data" / "materials").resolve()
    if _local_fallback.is_dir():
        MATERIALS_ROOT = _local_fallback
    else:
        logger.warning(f"[P0-1] /app/data/materials 不存在且本地 fallback 也不存在, 当前={MATERIALS_ROOT}")


def _safe_resolve_under_materials(filename: str) -> Path | None:
    """P0-3: 路径穿越防御。返回 resolved abs path, 若超出 MATERIALS_ROOT 则 None"""
    try:
        candidate = (PROJECT_ROOT / filename).resolve()
        candidate.relative_to(MATERIALS_ROOT)  # 越界即抛 ValueError
        return candidate
    except (ValueError, OSError):
        return None


# 专门的视频流端点，支持 Range 请求
@app.get("/video/{filename:path}")
async def stream_video(filename: str, request: Request):
    """视频流端点，支持 Range 请求

    Phase 30 P0-3: 加 resolve() 校验, 拒绝 ../etc/passwd 这类路径穿越
    """
    video_path = _safe_resolve_under_materials(filename)
    if video_path is None or not video_path.is_file():
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
async def proxy_oss(path: str, request: Request, current_user: Annotated[User, Depends(get_current_user)]):
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

    # Phase 30 P0-7: oss2 result.stream 是同步生成器, 直接 for 迭代会阻塞 event loop
    # 视频拖动时 Range 请求并发, oss2 socket 没释放 → 后续请求阻塞 (实测 1h+ 挂死)
    # 修法: 同步迭代器放进 run_in_executor, 加 wait_for 超时, try/finally 强制关 socket
    loop = asyncio.get_event_loop()
    _sentinel = object()

    def _next_chunk():
        """同步生成器 next, 阻塞调用, 放线程池执行. 无 chunk 返回 _sentinel."""
        try:
            return next(_stream_iter)
        except StopIteration:
            return _sentinel

    _stream_iter = result.stream(8192)
    # oss2 2.19: GetObjectResult.stream 实际是 resp.iter_content, 关闭走 result.resp.close()
    # oss2 0.14- 有 result.client (旧 API), 兜底 None 不报 AttributeError
    _oss_resp = getattr(result, "resp", None) or getattr(result, "client", None)

    async def stream_response():
        try:
            while True:
                chunk = await asyncio.wait_for(
                    loop.run_in_executor(None, _next_chunk),
                    timeout=60.0,  # 60s 内必须读出下一块, 否则断开防挂死
                )
                if chunk is _sentinel:
                    break
                yield chunk
        except asyncio.TimeoutError:
            logger.warning(f"[P0-7] oss-proxy stream 超时 (60s), 强制断开 path={path}")
        except Exception as e:
            logger.error(f"[P0-7] oss-proxy stream 异常: {e}")
        finally:
            # 显式关 oss2 socket, 防连接泄漏
            if _oss_resp is not None:
                try:
                    loop.run_in_executor(None, _oss_resp.close)
                except Exception:
                    pass

    return StreamingResponse(
        stream_response(),
        status_code=result.status,
        headers=filtered_headers,
        media_type=result.headers.get("content-type", "application/octet-stream"),
    )


_materials_mount = MATERIALS_ROOT if MATERIALS_ROOT.is_dir() else PROJECT_ROOT
if _materials_mount == PROJECT_ROOT:
    logger.warning(f"[P0-1] materials 目录不存在, fallback 到 PROJECT_ROOT: {_materials_mount}")
else:
    logger.info(f"[P0-1] /static 挂载到 MATERIALS_ROOT: {_materials_mount}")
app.mount("/static", StaticFiles(directory=str(_materials_mount)), name="static")

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
