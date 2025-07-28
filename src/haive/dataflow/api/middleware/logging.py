"""Logging core module.

This module provides logging functionality for the Haive framework.

Classes:
    RequestLoggingMiddleware: RequestLoggingMiddleware implementation.

Functions:
    dispatch: Dispatch functionality.
"""

# haive_dataflow/api/middleware/logging.py
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all API requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with detailed logging."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get user ID if authenticated
        user_id = getattr(request.state, "user_id", None)

        # Log start of request
        start_time = time.time()
        logger.info(
            f"Request {request_id} started: {request.method} {request.url.path} "
            f"(User: {user_id or 'anonymous'})"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log completion
            logger.info(
                f"Request {request_id} completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Time: {process_time:.4f}s"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.6f}"

            return response
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request {request_id} failed: {request.method} {request.url.path} "
                f"- Error: {e!s} - Time: {process_time:.4f}s"
            )
            raise
