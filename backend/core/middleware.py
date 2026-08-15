"""
Rate limiting middleware for API protection.
In-memory rate limiting using a simple sliding window algorithm.
"""

import time
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    Thread-safe implementation for single-process deployments.
    For multi-worker deployments, use Redis-based rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store: {ip_address: [(timestamp, path), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()

    def _cleanup_old_requests(self, ip: str, current_time: float):
        """Remove requests older than 1 hour."""
        cutoff = current_time - 3600
        self._requests[ip] = [
            (ts, path) for ts, path in self._requests[ip] if ts > cutoff
        ]

    def is_allowed(self, ip: str, path: str) -> Tuple[bool, Dict]:
        """
        Check if a request is allowed for the given IP.

        Returns:
            (is_allowed, rate_limit_info)
        """
        current_time = time.time()

        with self._lock:
            # Cleanup old requests
            self._cleanup_old_requests(ip, current_time)

            # Count requests in the last minute and hour
            minute_ago = current_time - 60
            hour_ago = current_time - 3600

            minute_count = sum(1 for ts, _ in self._requests[ip] if ts > minute_ago)
            hour_count = len(self._requests[ip])

            # Check limits
            if minute_count >= self.requests_per_minute:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_minute,
                    "window": "1 minute",
                    "retry_after": 60 - (current_time - minute_ago)
                }

            if hour_count >= self.requests_per_hour:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_hour,
                    "window": "1 hour",
                    "retry_after": 3600 - (current_time - hour_ago)
                }

            # Record this request
            self._requests[ip].append((current_time, path))

            return True, {
                "minute_remaining": self.requests_per_minute - minute_count - 1,
                "hour_remaining": self.requests_per_hour - hour_count - 1
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Adds rate limit headers to all responses:
        X-RateLimit-Limit: 60
        X-RateLimit-Remaining: 59
        X-RateLimit-Reset: 60
    """

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, requests_per_hour)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for:
        # - Frontend SPA entry point
        # - Health checks
        # - Static files (frontend assets)
        # - API documentation
        # - Localhost (development mode)
        skip_paths = [
            "/",
            "/api/system/health",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        if request.url.path in skip_paths:
            return await call_next(request)

        if request.url.path.startswith("/static") or request.url.path.startswith("/assets"):
            return await call_next(request)

        # Skip rate limiting for frontend files (dist folder)
        if request.url.path.startswith("/frontend") or ".js" in request.url.path or ".css" in request.url.path or ".ico" in request.url.path or ".png" in request.url.path or ".jpg" in request.url.path:
            return await call_next(request)

        # Skip rate limiting for localhost (development mode)
        client_ip = self._get_client_ip(request)
        if client_ip in ["127.0.0.1", "localhost", "::1", "::ffff:127.0.0.1"]:
            return await call_next(request)

        # Check rate limit for non-localhost requests
        is_allowed, info = self.limiter.is_allowed(client_ip, request.url.path)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=info,
                headers={"Retry-After": str(int(info.get("retry_after", 60)))}
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(info.get("minute_remaining", 0))
        response.headers["X-RateLimit-Reset"] = "60"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check X-Forwarded-For header (for reverse proxy deployments)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
