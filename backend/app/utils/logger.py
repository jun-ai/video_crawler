"""
日志配置模块
支持按级别分离日志文件，自动日志轮转
"""
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
import os
import traceback


class SafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Windows 安全的日志轮转处理器，避免多进程锁文件导致崩溃"""

    def doRollover(self):
        try:
            super().doRollover()
        except PermissionError:
            # Windows 上多进程写同一日志文件时，轮转 rename 可能被锁
            # 关闭旧流，重新打开当前日志文件继续写入
            if self.stream:
                self.stream.close()
                self.stream = self._open()
            # 用 print 而非 logging，避免递归触发 handler
            print(f"[Logger] 日志轮转跳过（文件被占用）: {self.baseFilename}", flush=True)
        except Exception:
            if self.stream:
                self.stream.close()
                self.stream = self._open()
            print(f"[Logger] 日志轮转异常: {self.baseFilename}", flush=True)

# 日志目录
LOG_DIR = Path("/app/logs")

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)


class LogLevelFilter(logging.Filter):
    """日志级别过滤器，用于分离不同级别的日志"""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器（终端输出用）"""

    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(app_name: str = "english-learning", debug: bool = False):
    """
    配置日志系统

    Args:
        app_name: 应用名称
        debug: 是否开启调试模式
    """
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 日志格式
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ========== 控制台处理器 ==========
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(colored_formatter)
    root_logger.addHandler(console_handler)

    # ========== 全量日志文件（info 及以上）==========
    all_log_file = LOG_DIR / "app.log"
    all_handler = SafeTimedRotatingFileHandler(
        filename=str(all_log_file),
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天
        encoding='utf-8'
    )
    all_handler.setLevel(logging.INFO)
    all_handler.setFormatter(detailed_formatter)
    all_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(all_handler)

    # ========== INFO 日志文件 ==========
    info_log_file = LOG_DIR / "info.log"
    info_handler = SafeTimedRotatingFileHandler(
        filename=str(info_log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(LogLevelFilter(logging.INFO))
    info_handler.setFormatter(detailed_formatter)
    info_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(info_handler)

    # ========== ERROR 日志文件 ==========
    error_log_file = LOG_DIR / "error.log"
    error_handler = SafeTimedRotatingFileHandler(
        filename=str(error_log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    error_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(error_handler)

    # ========== WARNING 日志文件 ==========
    warning_log_file = LOG_DIR / "warning.log"
    warning_handler = SafeTimedRotatingFileHandler(
        filename=str(warning_log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.addFilter(LogLevelFilter(logging.WARNING))
    warning_handler.setFormatter(detailed_formatter)
    warning_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(warning_handler)

    # 降低第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)
    # SQLAlchemy 引擎日志：echo=False 时仍可能输出，统一压制到 WARNING
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


# 请求日志中间件
class RequestLoggingMiddleware:
    """请求日志中间件"""

    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger or get_logger("request")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            method = scope["method"]
            path = scope["path"]
            client = scope.get("client", ("unknown", 0))[0]

            # 记录请求
            self.logger.info(f"Request: {client} -> {method} {path}")

        await self.app(scope, receive, send)
