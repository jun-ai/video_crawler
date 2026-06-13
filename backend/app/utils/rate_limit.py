import starlette.config
from slowapi import Limiter
from slowapi.util import get_remote_address

# 修复 starlette Config 在 Windows 上用 GBK 读 UTF-8 .env 文件报错的问题
_orig_read = starlette.config.Config._read_file


def _read_file_safe(self, file_name):
    try:
        return _orig_read(self, file_name)
    except (UnicodeDecodeError, FileNotFoundError):
        return {}


starlette.config.Config._read_file = _read_file_safe

limiter = Limiter(key_func=get_remote_address)
