"""In-memory TTL cache for external API requests."""

import time
import hashlib
import json
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    """Thread-safe in-memory cache with Time-To-Live support."""
    def __init__(self, default_ttl_seconds: int = 3600):
        self._default_ttl = default_ttl_seconds
        self._store: Dict[str, Tuple[Any, float]] = {}

    def _make_key(self, namespace: str, params: Dict[str, Any]) -> str:
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_digest = hashlib.sha256(param_str.encode("utf-8")).hexdigest()[:16]
        return f"{namespace}:{hash_digest}"

    def get(self, namespace: str, params: Dict[str, Any]) -> Optional[Any]:
        key = self._make_key(namespace, params)
        if key in self._store:
            data, expiry = self._store[key]
            if time.time() < expiry:
                return data
            else:
                del self._store[key]
        return None

    def set(self, namespace: str, params: Dict[str, Any], data: Any, ttl: Optional[int] = None) -> None:
        key = self._make_key(namespace, params)
        expiry = time.time() + (ttl or self._default_ttl)
        self._store[key] = (data, expiry)

    def clear(self) -> None:
        self._store.clear()


# Global cache instance
api_cache = TTLCache(default_ttl_seconds=3600)
