"""API Audit Logger for tracking all external HTTP requests and verification queries."""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

_GLOBAL_AUDIT_LOG: List[Dict[str, Any]] = []


def sanitize_url(url: str) -> str:
    """Removes API keys and secrets from URLs."""
    if not url:
        return ""
    sanitized = re.sub(r'([?&](?:api_?key|key|token|auth|secret)=)[^&]+', r'\1[REDACTED]', url, flags=re.IGNORECASE)
    return sanitized


def record_api_call(
    provider: str,
    endpoint: str,
    url: str,
    method: str = "GET",
    status_code: int = 200,
    response_summary: str = "",
    cached: bool = False,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Records an external API query into the audit trail."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "endpoint": endpoint,
        "url": sanitize_url(url),
        "method": method.upper(),
        "status_code": status_code,
        "cached": cached,
        "response_summary": response_summary,
        "extra": extra or {}
    }
    _GLOBAL_AUDIT_LOG.append(entry)
    return entry


def get_global_audit_log() -> List[Dict[str, Any]]:
    """Returns a copy of the global API audit log."""
    return list(_GLOBAL_AUDIT_LOG)


def clear_global_audit_log() -> None:
    """Clears the global audit log."""
    _GLOBAL_AUDIT_LOG.clear()
