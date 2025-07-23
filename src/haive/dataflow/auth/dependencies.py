"""Authentication dependencies for FastAPI routes.

This module provides FastAPI dependency functions for authentication in the
Haive API. It includes dependencies for both optional and required authentication,
supporting different levels of access control for API endpoints.

The authentication system uses JWT tokens provided through the Authorization
header, which are validated against the Supabase authentication service.

Typical usage example:

    ```python
    from fastapi import APIRouter, Depends
    from haive.dataflow.auth.dependencies import require_auth, get_current_user

    router = APIRouter()

    # Endpoint requiring authentication
    @router.get("/secure")
    async def secure_endpoint(user_id: str = Depends(require_auth)):
        return {"message": f"Hello, {user_id}!"}

    # Endpoint with optional authentication
    @router.get("/public")
    async def public_endpoint(user_id: Optional[str] = Depends(get_current_user)):
        if user_id:
            return {"message": f"Hello, {user_id}!"}
        return {"message": "Hello, anonymous user!"}
    ```
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth.supabase import SupabaseAuth
from .config.environment import get_supabase_server_config

# Security scheme for auth header
security = HTTPBearer(auto_error=False)


# Get auth instance for dependency injection
def get_auth_instance():
    """Get the Supabase authentication instance for dependency injection.

    This function creates and returns a SupabaseAuth instance configured with
    the server settings from environment variables. It's used as a FastAPI
    dependency to provide the authentication service to route handlers.

    Returns:
        SupabaseAuth: An initialized authentication service instance

    Example:
        >>> from fastapi import Depends
        >>> from haive.dataflow.auth.dependencies import get_auth_instance
        >>>
        >>> async def custom_auth(auth = Depends(get_auth_instance)):
        ...     # Use auth instance for custom authentication logic
        ...     return auth.validate_token(token)
    """
    config = get_supabase_server_config()
    return SupabaseAuth(config)


# Optional auth - returns user_id if authenticated, None otherwise
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth: SupabaseAuth = Depends(get_auth_instance),
) -> str | None:
    """Verify the token and return the user ID if valid (optional authentication).

    This dependency function provides optional authentication for routes.
    It extracts the JWT token from the Authorization header if present,
    validates it with Supabase, and returns the user ID if valid.
    If no token is provided or the token is invalid, it returns None
    instead of raising an exception.

    Args:
        credentials: HTTP Bearer token credentials from the Authorization header
        auth: Supabase authentication service instance

    Returns:
        Optional[str]: The authenticated user ID if valid, None otherwise

    Example:
        >>> @router.get("/profile")
        >>> async def get_profile(user_id: Optional[str] = Depends(get_current_user)):
        ...     if user_id:
        ...         return {"user_id": user_id, "premium": True}
        ...     else:
        ...         return {"premium": False}
    """
    if not credentials:
        return None

    user_id = auth.get_user_id(credentials.credentials)
    return user_id  # Will be None if invalid


# Required auth - raises exception if not authenticated
async def require_auth(user_id: str | None = Depends(get_current_user)) -> str:
    """Require authentication for a route (required authentication).

    This dependency function provides required authentication for routes.
    It builds on the optional authentication dependency but raises an
    HTTP exception if no valid authentication is provided, ensuring that
    the route can only be accessed by authenticated users.

    Args:
        user_id: The user ID from the get_current_user dependency

    Returns:
        str: The authenticated user ID

    Raises:
        HTTPException: 401 Unauthorized if no valid authentication is provided

    Example:
        >>> @router.post("/secure-endpoint")
        >>> async def secure_endpoint(user_id: str = Depends(require_auth)):
        ...     return {"message": f"Hello, {user_id}!", "status": "authenticated"}
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
