"""Authentication routes for the Haive API.

This module provides routes for authentication operations such as
login, token refresh, and user information retrieval.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field

from haive.dataflow.api.auth.dependencies import CurrentUser, require_auth
from haive.dataflow.supabase.auth import get_auth_manager
from haive.dataflow.supabase.persistence import get_persistence_integration

# Create router
router = APIRouter()

# Models
class UserCredentials(BaseModel):
    """User credentials for login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")

class TokenResponse(BaseModel):
    """Token response."""
    access_token: str = Field(..., description="Access token")
    refresh_token: str | None = Field(None, description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int | None = Field(None, description="Token expiration time in seconds")

class UserResponse(BaseModel):
    """User information response."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str | None = Field(None, description="Username")
    roles: list[str] = Field(default_factory=list, description="User roles")
    permissions: list[str] = Field(default_factory=list, description="User permissions")

# Routes
@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    credentials: UserCredentials,
):
    """Login with email and password.
    
    Args:
        response: FastAPI response
        credentials: User credentials
        
    Returns:
        Access token and refresh token
        
    Raises:
        HTTPException: If login fails
    """
    try:
        # Get auth manager
        auth_manager = get_auth_manager()

        # Get Supabase client
        supabase = auth_manager.supabase

        # Sign in with password
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        # Get session
        session = auth_response.session

        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=session.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=session.expires_in,
            path="/auth"
        )

        # Return access token
        return TokenResponse(
            access_token=session.access_token,
            token_type="bearer",
            expires_in=session.expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {e!s}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_request: RefreshRequest | None = None,
    request: Request = None,
):
    """Refresh an access token.
    
    Args:
        response: FastAPI response
        refresh_request: Optional refresh token request
        request: FastAPI request (for cookie access)
        
    Returns:
        New access token and refresh token
        
    Raises:
        HTTPException: If token refresh fails
    """
    # Get refresh token from request body or cookie
    refresh_token = None
    if refresh_request:
        refresh_token = refresh_request.refresh_token
    elif request and "refresh_token" in request.cookies:
        refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token provided"
        )

    try:
        # Get auth manager
        auth_manager = get_auth_manager()

        # Refresh token
        tokens = auth_manager.refresh_token(refresh_token)

        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600 * 24 * 7,  # 7 days
            path="/auth"
        )

        # Return access token
        return TokenResponse(
            access_token=tokens["access_token"],
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {e!s}"
        )

@router.post("/logout")
async def logout(response: Response):
    """Logout by clearing cookies.
    
    Args:
        response: FastAPI response
        
    Returns:
        Success message
    """
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/auth",
        secure=True,
        httponly=True
    )

    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: CurrentUser = None):
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
        
    Raises:
        HTTPException: If not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Get persistence integration
    persistence = get_persistence_integration()

    # Get user context
    user_context = persistence.get_user_context(current_user)

    # Return user information
    return UserResponse(
        id=current_user.get("id"),
        email=current_user.get("email"),
        username=user_context.get("username"),
        roles=current_user.get("app_metadata", {}).get("roles", []),
        permissions=current_user.get("permissions", [])
    )

@router.get("/threads")
async def list_user_threads(
    limit: int = 100,
    offset: int = 0,
    user: dict[str, Any] = Depends(require_auth(["threads:own"]))
):
    """List threads owned by the current user.
    
    Args:
        limit: Maximum number of threads to return
        offset: Offset for pagination
        user: Current authenticated user
        
    Returns:
        List of thread information
    """
    # Get persistence integration
    persistence = get_persistence_integration()

    # List threads
    return persistence.list_user_threads(user.get("id"), limit, offset)

@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    user: dict[str, Any] = Depends(require_auth(["threads:own"]))
):
    """Delete a thread owned by the current user.
    
    Args:
        thread_id: Thread ID to delete
        user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If deletion fails
    """
    # Get persistence integration
    persistence = get_persistence_integration()

    # Check if user has management permission
    has_manage = "threads:manage" in user.get("permissions", [])

    # For regular users, check ownership
    if not has_manage and not persistence.check_thread_ownership(thread_id, user.get("id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this thread"
        )

    # Delete thread
    success = persistence.delete_thread(thread_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete thread"
        )

    return {"message": "Thread deleted successfully"}
