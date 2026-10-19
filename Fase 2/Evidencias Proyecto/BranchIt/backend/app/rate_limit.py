"""Single-process development limiter. Use a shared gateway for multiple workers."""
from collections import deque
from threading import Lock
from time import monotonic
from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, limit=20, seconds=60):
        self.limit, self.seconds = limit, seconds
        self.entries = {}
        self.lock = Lock()

    def check(self, key, now=None):
        now = monotonic() if now is None else now
        with self.lock:
            # Bound memory and expire old IP buckets without trusting forwarded headers.
            self.entries = {k: v for k, v in self.entries.items() if v and v[-1] > now - self.seconds}
            if key not in self.entries and len(self.entries) >= 10000:
                raise HTTPException(429, 'Demasiados intentos. Inténtalo más tarde.', headers={'Retry-After': str(self.seconds)})
            bucket = self.entries.setdefault(key, deque())
            while bucket and bucket[0] <= now - self.seconds:
                bucket.popleft()
            if len(bucket) >= self.limit:
                raise HTTPException(429, 'Demasiados intentos. Espera un minuto e inténtalo nuevamente.', headers={'Retry-After': str(self.seconds)})
            bucket.append(now)


limiter = RateLimiter()


def limit_auth(request: Request):
    limiter.check(request.client.host if request.client else 'unknown')
