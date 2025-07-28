"""Rate_Limit core module.

This module provides rate limit functionality for the Haive framework.

Classes:
    RateLimitMiddleware: RateLimitMiddleware implementation.

Functions:
    dispatch: Dispatch functionality.
"""

# haive_dataflow/api/middleware/rate_limit.py
import json
import logging
import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

    def __init__(self, app, rate_limit_per_minute: int = 60, window_seconds: int = 60):
        """Initialize the rate limiting middleware.

        Args:
            app: FastAPI application
            rate_limit_per_minute: Maximum requests per minute
            window_seconds: Time window for rate limiting in seconds
        """
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.window = window_seconds
        # Dict of user_id -> [(timestamp, count)]
        self.request_history: dict[str, list[tuple[float, int]]] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with rate limiting."""
        # Get identifier for rate limiting (user_id or IP)
        user_id = getattr(request.state, "user_id", None)
        identifier = user_id or request.client.host

        # Current time
        current_time = time.time()

        # Clean old records
        self.request_history[identifier] = [
            (ts, count)
            for ts, count in self.request_history[identifier]
            if current_time - ts < self.window
        ]

        # Calculate current request count
        request_count = sum(count for _, count in self.request_history[identifier])

        # Check if rate limit exceeded
        if request_count >= self.rate_limit:
            # Return rate limit error
            return Response(
                content=json.dumps(
                    {
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self.rate_limit} requests per {self.window} seconds",
                    }
                ),
                status_code=429,
                media_type="application/json",
            )

        # Record this request
        self.request_history[identifier].append((current_time, 1))

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.rate_limit - request_count - 1
        )
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))

        return response
