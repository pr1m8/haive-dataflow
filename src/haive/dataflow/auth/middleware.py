# haive/dataflow/auth/middleware.py
import logging

from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .auth.supabase import SupabaseAuth

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


# FastAPI Dependency for authentication
class AuthDependency:
    """FastAPI dependency for authentication."""

    def __init__(self, require: bool = True):
        """Initialize the auth dependency.

        Args:
            require: Whether authentication is required (will raise exception if True)
        """
        self.require = require
        self.auth = SupabaseAuth()

    async def __call__(
        self, credentials: HTTPAuthorizationCredentials | None = Depends(security)
    ) -> str | None:
        """Extract and verify user ID from request."""
        # No credentials provided
        if not credentials:
            if self.require:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        # Verify token
        user_id = self.auth.get_user_id(credentials.credentials)

        # Invalid token
        if not user_id and self.require:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id


# Starlette middleware for global auth handling
class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    """Global middleware for Supabase authentication."""

    def __init__(self, app, auth: SupabaseAuth | None = None):
        """Initialize the middleware."""
        super().__init__(app)
        self.auth = auth or SupabaseAuth()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request."""
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        user_id = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            user_id = self.auth.get_user_id(token)

            if user_id:
                # Attach user_id to request state
                request.state.user_id = user_id

        # Continue with request processing
        response = await call_next(request)
        return response


# Convenience dependencies
require_auth = AuthDependency(require=True)
optional_auth = AuthDependency(require=False)
