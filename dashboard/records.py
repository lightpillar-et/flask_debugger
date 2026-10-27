from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode
from uuid import uuid4

from werkzeug.wrappers import Request


SENSITIVE_NAMES = {"authorization", "cookie", "proxy-authorization", "set-cookie"}
SENSITIVE_FIELDS = {"password", "passwd", "secret", "token", "api_key", "apikey"}


def _redact_mapping(values):
    if not hasattr(values, "items"):
        return values
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_FIELDS else value
        for key, value in values.items()
    }


def _safe_query(query):
    pairs = parse_qsl(query, keep_blank_values=True)
    return urlencode([
        (key, "[REDACTED]" if key.lower() in SENSITIVE_FIELDS else value)
        for key, value in pairs
    ])


def redact_headers(headers):
    return {
        name: "[REDACTED]" if name.lower() in SENSITIVE_NAMES else value
        for name, value in headers
    }


def _safe_body(request):
    if not request.get_data(cache=True):
        return None
    if request.is_json:
        try:
            return _redact_mapping(request.get_json(silent=True) or {})
        except (TypeError, ValueError):
            return "[UNREADABLE JSON]"
    if request.mimetype == "application/x-www-form-urlencoded":
        return _redact_mapping(request.form.to_dict())
    return f"[{request.content_length or 0} bytes omitted]"


def build_request_record(environ):
    request = Request(environ)
    query = _safe_query(request.query_string.decode("utf-8", errors="replace"))
    url = request.path + (f"?{query}" if query else "")
    headers = redact_headers(request.headers.items())
    return {
        "id": uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": request.method,
        "url": url,
        "path": request.path,
        "query": _redact_mapping(request.args.to_dict()),
        "request_headers": headers,
        "request_body": _safe_body(request),
        "status_code": 500,
        "status": "500 INTERNAL SERVER ERROR",
        "response_headers": {},
        "duration_ms": 0,
        "error": None,
    }
