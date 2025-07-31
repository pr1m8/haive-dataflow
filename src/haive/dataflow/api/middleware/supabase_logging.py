# haive/dataflow/api/middleware/supabase_logging.py

import asyncio
import json
import logging
import time
import traceback
import uuid
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from supabase import create_client

from .config.environment import get_supabase_server_config

# Import Supabase client


logger = logging.getLogger(__name__)


class SupabaseLogger:
    """Class for logging to Supabase database."""

    def __init__(self):
        """Initialize with server-side config."""
        self.config = get_supabase_server_config()
        self._client = None

    @property
    def client(self):
        """Lazy-loaded Supabase admin client."""
        if self._client is None:
            self._client = create_client(
                self.config.url, self.config.service_role_key.get_secret_value()
            )
        return self._client

    async def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        user_id: str | None,
        status_code: int,
        duration: float,
        request_data: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Log an API request to Supabase.

        Args:
            request_id: Unique request identifier
            method: HTTP method (GET, POST, etc.)
            path: Request path
            user_id: User ID if authenticated
            status_code: HTTP status code
            duration: Request processing time in seconds
            request_data: Request body data (optional)
            response_data: Response data (optional)
            error: Error message if request failed (optional)
            metadata: Additional metadata (optional)

        Returns:
            True if logging successful, False otherwise
        """
        try:
            # Prepare log data
            log_entry = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "path": path,
                "user_id": user_id,
                "status_code": status_code,
                "duration_ms": round(duration * 1000),
                "request_data": (
                    self._sanitize_data(request_data) if request_data else None
                ),
                "response_data": (
                    self._sanitize_data(response_data) if response_data else None
                ),
                "error": error,
                "metadata": metadata,
                "ip_address": (
                    getattr(request_data, "client", {}).get("host", None)
                    if request_data
                    else None
                ),
            }

            # Insert into Supabase
            response = (
                await self.client.from_("system_logs.api_requests")
                .insert(log_entry)
                .execute()
            )

            return bool(response.data)
        except Exception as e:
            # Log error but don't fail the request
            logger.exception(f"Error logging to Supabase: {e!s}")
            logger.exception(traceback.format_exc())
            return False

    async def log_llm_request(
        self,
        request_id: str,
        user_id: str | None,
        provider: str,
        model: str,
        query: str,
        response_text: str | None,
        duration: float,
        token_count: int,
        cost: float,
        success: bool,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Log an LLM API request to Supabase.

        Args:
            request_id: Unique request identifier
            user_id: User ID if authenticated
            provider: LLM provider (e.g., "azure", "anthropic")
            model: Model name
            query: User query
            response_text: Generated text (optional)
            duration: Request processing time in seconds
            token_count: Number of tokens processed
            cost: Cost in credits
            success: Whether the request succeeded
            error: Error message if request failed (optional)
            metadata: Additional metadata (optional)

        Returns:
            True if logging successful, False otherwise
        """
        try:
            # Prepare log data
            log_entry = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "provider": provider,
                "model": model,
                "query": query,
                "response": response_text,
                "duration_ms": round(duration * 1000),
                "token_count": token_count,
                "cost": cost,
                "success": success,
                "error": error,
                "metadata": metadata,
            }

            # Insert into Supabase
            response = (
                await self.client.from_("system_logs.llm_requests")
                .insert(log_entry)
                .execute()
            )

            return bool(response.data)
        except Exception as e:
            # Log error but don't fail the request
            logger.exception(f"Error logging LLM request to Supabase: {e!s}")
            logger.exception(traceback.format_exc())
            return False

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive fields, truncate large
        values).

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data
        """
        if data is None:
            return None

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Skip sensitive fields
                if key.lower() in [
                    "password",
                    "secret",
                    "token",
                    "api_key",
                    "key",
                    "authorization",
                ]:
                    result[key] = "***REDACTED***"
                # Truncate large string values
                elif isinstance(value, str) and len(value) > 1000:
                    result[key] = value[:1000] + "... [truncated]"
                # Recurse into nested dictionaries
                elif isinstance(value, dict):
                    result[key] = self._sanitize_data(value)
                # Recurse into lists
                elif isinstance(value, list):
                    result[key] = [
                        (
                            self._sanitize_data(item)
                            if isinstance(item, dict | list)
                            else item
                        )
                        for item in value
                    ]
                else:
                    result[key] = value
            return result
        if isinstance(data, list):
            return [
                self._sanitize_data(item) if isinstance(item, dict | list) else item
                for item in data
            ]
        return data


class SupabaseLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all API requests to Supabase."""

    def __init__(self, app, supabase_logger: SupabaseLogger | None = None):
        """Initialize the middleware."""
        super().__init__(app)
        self.logger = supabase_logger or SupabaseLogger()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with detailed logging to Supabase."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get user ID if authenticated
        user_id = getattr(request.state, "user_id", None)

        # Log start of request to console
        start_time = time.time()
        logger.info(
            f"Request {request_id} started: {request.method} {request.url.path} "
            f"(User: {user_id or 'anonymous'})"
        )

        # Try to get request body
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()

                # Store original body for later use
                async def get_body():
                    return body_bytes

                request._body = body_bytes
                request.body = get_body

                # Try to parse as JSON
                try:
                    request_body = json.loads(body_bytes.decode())
                except BaseException:
                    # Not valid JSON, store as string
                    body_str = body_bytes.decode()
                    if len(body_str) > 1000:
                        body_str = body_str[:1000] + "... [truncated]"
                    request_body = {"raw": body_str}
            except Exception as e:
                logger.warning(f"Error accessing request body: {e!s}")

        # Add client info
        client_info = {
            "host": request.client.host if request.client else None,
            "headers": dict(request.headers),
            "params": dict(request.query_params),
        }

        # Process request
        response_body = None
        error_msg = None

        try:
            # Create a custom response class to capture the response body
            original_response = await call_next(request)

            # Get response body
            response_body_bytes = b""
            async for chunk in original_response.body_iterator:
                response_body_bytes += chunk

            # Try to decode and parse the response body
            try:
                response_body_str = response_body_bytes.decode()
                try:
                    response_body = json.loads(response_body_str)
                except BaseException:
                    if len(response_body_str) > 1000:
                        response_body_str = response_body_str[:1000] + "... [truncated]"
                    response_body = {"raw": response_body_str}
            except BaseException:
                response_body = {"binary": "[binary data]"}

            # Create a new response with the same data
            response = Response(
                content=response_body_bytes,
                status_code=original_response.status_code,
                headers=dict(original_response.headers),
                media_type=original_response.media_type,
            )

            # Calculate processing time
            process_time = time.time() - start_time

            # Log completion to console
            logger.info(
                f"Request {request_id} completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Time: {process_time:.4f}s"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.6f}"

            status_code = response.status_code

        except Exception as e:
            # Log error to console
            process_time = time.time() - start_time
            error_msg = str(e)
            logger.exception(
                f"Request {request_id} failed: {request.method} {request.url.path} "
                f"- Error: {error_msg} - Time: {process_time:.4f}s"
            )
            logger.exception(traceback.format_exc())

            # Set status code for log entry
            status_code = 500

            # Re-raise the exception
            raise

        finally:
            # Log to Supabase in the background
            # This ensures that logging doesn't block the response
            metadata = {
                "client": client_info,
                "headers": {
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() not in ["authorization", "cookie"]
                },
            }

            asyncio.create_task(
                self.logger.log_request(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    user_id=user_id,
                    status_code=status_code,
                    duration=process_time,
                    request_data=request_body,
                    response_data=response_body,
                    error=error_msg,
                    metadata=metadata,
                )
            )

        return response


# LLM-specific logging functions for the router
class LLMLogger:
    """Utility class for logging LLM requests."""

    def __init__(self):
        """Initialize the logger."""
        self.supabase_logger = SupabaseLogger()

    async def log_llm_request(
        self,
        user_id: str,
        provider: str,
        model: str,
        query: str,
        response_text: str | None = None,
        token_count: int = 0,
        cost: float = 0.0,
        duration: float = 0.0,
        success: bool = True,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Log an LLM request to both console and Supabase.

        Args:
            user_id: User ID
            provider: LLM provider
            model: Model name
            query: User query
            response_text: Generated text (optional)
            token_count: Number of tokens processed
            cost: Cost in credits
            duration: Request processing time in seconds
            success: Whether the request succeeded
            error: Error message if request failed (optional)
            metadata: Additional metadata (optional)
        """
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Log to console
        log_msg = (
            f"LLM Request {request_id}: {provider}/{model} - "
            f"User: {user_id} - Tokens: {token_count} - "
            f"Cost: {cost:.4f} - Time: {duration:.4f}s - "
            f"Success: {success}"
        )

        if success:
            logger.info(log_msg)
        else:
            logger.error(f"{log_msg} - Error: {error}")

        # Log to Supabase in the background
        asyncio.create_task(
            self.supabase_logger.log_llm_request(
                request_id=request_id,
                user_id=user_id,
                provider=provider,
                model=model,
                query=query,
                response_text=response_text,
                duration=duration,
                token_count=token_count,
                cost=cost,
                success=success,
                error=error,
                metadata=metadata,
            )
        )
