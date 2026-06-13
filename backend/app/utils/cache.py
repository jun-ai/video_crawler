import time
from typing import Any, Optional


class SimpleCache:
    """简单内存缓存，支持 TTL 过期和前缀失效"""

    def __init__(self):
        self._store: dict = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str):
        self._store.pop(key, None)

    def invalidate(self, prefix: str = ""):
        if not prefix:
            self._store.clear()
            return
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]


cache = SimpleCache()
