from collections import defaultdict
from datetime import UTC, datetime
from threading import Lock
from time import time

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import ApiError


class InMemoryUsageGuard:
    def __init__(self) -> None:
        self._lock = Lock()
        self._daily_counts: dict[str, int] = defaultdict(int)
        self._minute_windows: dict[str, tuple[int, int]] = {}

    def check(self, endpoint: str, daily_limit: int, per_minute_limit: int) -> None:
        if daily_limit <= 0 and per_minute_limit <= 0:
            return

        today = datetime.now(UTC).date().isoformat()
        minute = int(time() // 60)
        daily_key = today

        with self._lock:
            if daily_limit > 0 and self._daily_counts[daily_key] >= daily_limit:
                raise ApiError(
                    429,
                    "AI_DAILY_USAGE_LIMIT_EXCEEDED",
                    "AI 서버의 일일 처리 한도를 초과했습니다.",
                )

            current_minute, count = self._minute_windows.get(endpoint, (minute, 0))
            if current_minute != minute:
                current_minute, count = minute, 0
            if per_minute_limit > 0 and count >= per_minute_limit:
                raise ApiError(
                    429,
                    "AI_RATE_LIMIT_EXCEEDED",
                    "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
                )

            self._daily_counts[daily_key] += 1
            self._minute_windows[endpoint] = (current_minute, count + 1)

    def reset(self) -> None:
        with self._lock:
            self._daily_counts.clear()
            self._minute_windows.clear()


usage_guard = InMemoryUsageGuard()


async def verify_ai_usage_limit(request: Request) -> None:
    settings = get_settings()
    usage_guard.check(
        endpoint=request.url.path,
        daily_limit=settings.ai_daily_request_limit,
        per_minute_limit=settings.ai_rate_limit_per_minute,
    )
