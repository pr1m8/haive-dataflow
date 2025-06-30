# haive_dataflow/api/middleware/auth.py
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from haive.dataflow.auth.supabase import SupabaseAuth
from haive.dataflow.config.environment import get_supabase_server_config

logger = logging.getLogger(__name__)


class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    """Global middleware for Supabase authentication."""

    def __init__(self, app):
        """Initialize the middleware."""
        super().__init__(app)
        self.auth = SupabaseAuth(get_supabase_server_config())

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request with auth verification."""
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        user_id = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            user_id = self.auth.get_user_id(token)

            if user_id:
                # Attach user_id to request state
                request.state.user_id = user_id
                logger.debug(f"Authenticated user: {user_id}")
            else:
                logger.debug("Invalid auth token provided")

        # Continue with request processing
        response = await call_next(request)
        return response
