"""Supabase core module.

This module provides supabase functionality for the Haive framework.

Classes:
    SupabaseAuth: SupabaseAuth implementation.

Functions:
    verify_token: Verify Token functionality.
    get_user_id: Get User Id functionality.
"""

# haive/dataflow/auth/supabase.py
import logging
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config.environment import SupabaseServerConfig

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class SupabaseAuth:
    """Authentication provider using Supabase JWT."""

    def __init__(self, server_config: SupabaseServerConfig | None = None):
        """Initialize with server-side config (for backend operations)."""
        self.config = server_config or SupabaseServerConfig()

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify Supabase JWT token and return payload if valid."""
        if not token:
            return None

        try:
            # For debugging only - remove in production!
            secret = self.config.jwt_secret.get_secret_value()
            logger.warning(
                f"JWT Secret (first/last 3 chars): {secret[:3]}...{secret[-3:]}"
            )

            # Try to parse the token header to check algorithm
            token_parts = token.split(".")
            if len(token_parts) >= 1:
                import base64
                import json

                header_bytes = base64.urlsafe_b64decode(
                    token_parts[0] + "=" * (4 - len(token_parts[0]) % 4)
                )
                header = json.loads(header_bytes)
                logger.warning(f"Token header: {header}")

            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                audience="authenticated",  # Explicitly set the expected audience
            )
            return payload
        except Exception as e:
            logger.warning(f"Token verification failed: {e!s}")
            # For more detailed debugging
            import traceback

            logger.warning(f"Traceback: {traceback.format_exc()}")
            return None

    def get_user_id(self, token: str) -> str | None:
        """Extract user ID from token."""
        payload = self.verify_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
        return None


# Frontend auth middleware (used in API routes)
def get_auth_instance():
    """Get the auth instance for dependency injection."""
    return SupabaseAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth: SupabaseAuth = Depends(get_auth_instance),
) -> str | None:
    """Verify the token and return the user ID.

    This is for frontend API routes - can be used with FastAPI Depends.
    """
    if not credentials:
        return None

    user_id = auth.get_user_id(credentials.credentials)
    if not user_id:
        return None

    return user_id


# Required auth middleware that raises an exception for unauthorized access
async def require_auth(user_id: str | None = Depends(get_current_user)) -> str:
    """Require authentication for a route.

    Raises HTTPException if not authenticated.
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
