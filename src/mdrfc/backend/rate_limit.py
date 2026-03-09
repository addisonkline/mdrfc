from collections import defaultdict, deque
from collections.abc import Hashable
import asyncio
import time


class SlidingWindowRateLimiter:
    """
    Simple in-process sliding window rate limiter.
    """

    def __init__(self) -> None:
        self._attempts: dict[Hashable, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check_and_record(
        self,
        key: Hashable,
        *,
        limit: int,
        window_seconds: int,
    ) -> int | None:
        now = time.monotonic()
        async with self._lock:
            attempts = self._attempts[key]
            window_start = now - window_seconds
            while attempts and attempts[0] <= window_start:
                attempts.popleft()

            if len(attempts) >= limit:
                retry_after = int(attempts[0] + window_seconds - now)
                return max(retry_after, 1)

            attempts.append(now)
            return None
