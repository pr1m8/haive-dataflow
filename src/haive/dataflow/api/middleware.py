"""Middleware core module.

This module provides middleware functionality for the Haive framework.

Classes:
    RequestLoggingMiddleware: RequestLoggingMiddleware implementation.
    RateLimitMiddleware: RateLimitMiddleware implementation.

Functions:
    dispatch: Dispatch functionality.
    dispatch: Dispatch functionality.
"""

# haive/dataflow/api/middleware.py
import json
import logging
import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all API requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with logging."""
        request_id = str(uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Extract user ID if available
        user_id = getattr(request.state, "user_id", None)

        # Log start of request
        start_time = time.time()
        logger.info(
            f"Request {request_id} started: {request.method} {request.url.path} (User: {user_id})"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log request completion
            logger.info(
                f"Request {request_id} completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Time: {process_time:.4f}s"
            )

            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request {request_id} failed: {request.method} {request.url.path} "
                f"- Error: {e!s} - Time: {process_time:.4f}s"
            )

            # Raise exception to be handled by FastAPI
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(
        self, app, rate_limit_per_minute: int = 60, rate_limit_window_seconds: int = 60
    ):
        """Initialize the middleware."""
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.window = rate_limit_window_seconds
        self.requests = {}  # user_id -> [(timestamp, request_count)]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with rate limiting."""
        # Get user ID if available
        user_id = getattr(request.state, "user_id", None) or request.client.host

        # Apply rate limiting
        current_time = time.time()

        # Clean up old records
        if user_id in self.requests:
            self.requests[user_id] = [
                (ts, count)
                for ts, count in self.requests[user_id]
                if current_time - ts < self.window
            ]
        else:
            self.requests[user_id] = []

        # Calculate current request count
        request_count = sum(count for _, count in self.requests[user_id])

        # Check rate limit
        if request_count >= self.rate_limit:
            # Rate limit exceeded
            response = Response(
                content=json.dumps(
                    {
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self.rate_limit} requests per {self.window} seconds",
                    }
                ),
                status_code=429,
                media_type="application/json",
            )
            return response

        # Add current request
        self.requests[user_id].append((current_time, 1))

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.rate_limit - request_count - 1
        )
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))

        return response
