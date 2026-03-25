from collections import defaultdict, deque
from collections.abc import Hashable
import asyncio
import hashlib
import json
import time

from mdrfc.backend.db import check_and_record_signup_rate_limit_in_db


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


def _split_scope_and_key_hash(key: Hashable) -> tuple[str, str]:
    if isinstance(key, tuple) and len(key) > 1 and isinstance(key[0], str):
        scope = key[0]
        raw_key = key[1:]
    else:
        scope = "default"
        raw_key = (key,)

    key_hash = hashlib.sha256(
        json.dumps(
            [str(part) for part in raw_key],
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return scope, key_hash


class PersistentSlidingWindowRateLimiter:
    """
    Postgres-backed sliding window rate limiter for signup attempts.
    """

    async def check_and_record(
        self,
        key: Hashable,
        *,
        limit: int,
        window_seconds: int,
    ) -> int | None:
        scope, key_hash = _split_scope_and_key_hash(key)
        return await check_and_record_signup_rate_limit_in_db(
            scope=scope,
            key_hash=key_hash,
            limit=limit,
            window_seconds=window_seconds,
        )
