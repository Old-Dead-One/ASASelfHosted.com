"""
Rate limiting middleware and utilities.

Scaffold for rate limiting with in-memory dev limiter.
TODO: Replace with Redis-based limiter in production.
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import APIError


class RateLimiter:
    """
    In-memory rate limiter for development.

    Uses a simple sliding window approach.
    Not suitable for production (use Redis instead).
    """

    def __init__(self):
        # Store: {key: [(timestamp, count), ...]}
        self._windows: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._cleanup_interval = 300  # Clean up old entries every 5 minutes
        self._last_cleanup = time.time()

    def _cleanup_old_entries(self, window_sec: int):
        """Remove entries older than the window."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        cutoff = now - window_sec
        for key in list(self._windows.keys()):
            self._windows[key] = [
                (ts, count) for ts, count in self._windows[key] if ts > cutoff
            ]
            if not self._windows[key]:
                del self._windows[key]

        self._last_cleanup = now

    def check(self, key: str, limit: int, window_sec: int) -> bool:
        """
        Check if request is within rate limit.

        Returns True if allowed, False if rate limited.
        """
        if not settings.DEBUG:  # Only enable in non-debug mode
            # In debug/local, rate limiting is optional
            if not getattr(settings, "RATE_LIMIT_ENABLED", False):
                return True

        now = time.time()
        cutoff = now - window_sec

        # Clean up old entries periodically
        self._cleanup_old_entries(window_sec)

        # Get current window for this key
        window = self._windows[key]

        # Remove old entries
        window = [(ts, count) for ts, count in window if ts > cutoff]
        self._windows[key] = window

        # Count requests in window
        total_count = sum(count for _, count in window)

        if total_count >= limit:
            return False

        # Add current request
        window.append((now, 1))
        self._windows[key] = window

        return True


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limit_key(request: Request, identifier: str | None = None) -> str:
    """
    Generate rate limit key from request.

    Uses IP address by default, or custom identifier if provided.
    """
    if identifier:
        return f"rate_limit:{identifier}"

    # Use client IP
    client_ip = request.client.host if request.client else "unknown"
    return f"rate_limit:ip:{client_ip}"


def rate_limit(
    limit: int,
    window_sec: int,
    key_func: Callable[[Request], str] | None = None,
) -> Callable:
    """
    Rate limit decorator/dependency factory.

    Usage:
        @router.post("/endpoint")
        async def endpoint(request: Request):
            if not rate_limit_check(request, limit=60, window_sec=60):
                raise RateLimitError()
            ...

    Or as dependency:
        @router.post("/endpoint", dependencies=[Depends(rate_limit(60, 60))])
    """
    async def rate_limit_dependency(request: Request):
        if key_func:
            key = key_func(request)
        else:
            key = get_rate_limit_key(request)

        if not _rate_limiter.check(key, limit, window_sec):
            raise APIError(
                message="Rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error_code="RATE_LIMIT_EXCEEDED",
            )

    return rate_limit_dependency


# Pre-configured rate limiters for common use cases
def public_get_rate_limit(request: Request):
    """120 requests per minute per IP for public GET endpoints."""
    key = get_rate_limit_key(request)
    if not _rate_limiter.check(key, limit=120, window_sec=60):
        raise APIError(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


def auth_user_rate_limit(request: Request):
    """60 requests per minute per user for authenticated endpoints."""
    from app.core.security import get_user_from_request

    user = get_user_from_request(request)
    if not user:
        # Fall back to IP if no user
        key = get_rate_limit_key(request)
    else:
        key = f"rate_limit:user:{user.user_id}"

    if not _rate_limiter.check(key, limit=60, window_sec=60):
        raise APIError(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


def heartbeat_rate_limit(request: Request, server_id: str):
    """12 requests per minute per server for heartbeat ingestion."""
    key = f"rate_limit:heartbeat:server:{server_id}"
    if not _rate_limiter.check(key, limit=12, window_sec=60):
        raise APIError(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


# TODO: Replace in-memory limiter with Redis-based solution for production
# Example Redis implementation:
# - Use Redis sorted sets with timestamps as scores
# - ZREMRANGEBYSCORE to remove old entries
# - ZCARD to count current requests
# - Set TTL on keys for automatic cleanup
