from collections import deque
from copy import deepcopy
from threading import Lock
from typing import Any


class RequestHistory:
    """Thread-safe, bounded storage for request records."""

    def __init__(self, max_records=200):
        if max_records < 1:
            raise ValueError("max_records must be greater than zero")
        self._records = deque(maxlen=max_records)
        self._lock = Lock()

    def add(self, record):
        with self._lock:
            self._records.appendleft(deepcopy(record))

    def all(self):
        with self._lock:
            return deepcopy(list(self._records))

    def get(self, record_id):
        with self._lock:
            for record in self._records:
                if record["id"] == record_id:
                    return deepcopy(record)
        return None

    def query(self, method=None, status=None, url=None, limit=50):
        records = self.all()
        method = method.upper() if method else None
        url = url.lower() if url else None

        filtered = [
            record for record in records
            if (not method or record["method"] == method)
            and (status is None or record["status_code"] == status)
            and (not url or url in record["url"].lower())
        ]
        return filtered[:limit]

    def summary(self):
        records = self.all()
        durations = [record["duration_ms"] for record in records]
        successful = sum(200 <= record["status_code"] < 400 for record in records)
        errors = sum(record["status_code"] >= 400 for record in records)
        return {
            "total_requests": len(records),
            "successful_requests": successful,
            "error_requests": errors,
            "average_duration_ms": round(sum(durations) / len(durations), 2)
            if durations else 0,
        }

    def errors(self):
        return [record for record in self.all() if record["status_code"] >= 400]

    def performance(self):
        records = self.all()
        durations = [record["duration_ms"] for record in records]
        return {
            "count": len(durations),
            "average_duration_ms": round(sum(durations) / len(durations), 2)
            if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "durations": [
                {
                    "id": record["id"],
                    "timestamp": record["timestamp"],
                    "url": record["url"],
                    "duration_ms": record["duration_ms"],
                }
                for record in records
            ],
        }
