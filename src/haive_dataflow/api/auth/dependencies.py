"""
FastAPI dependencies for Supabase authentication.

This module provides dependency functions and classes for FastAPI that
integrate with Supabase authentication, enabling route-level auth requirements.
"""

from typing import Dict, Any, Optional, List, Callable, Annotated
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

from haive_dataflow.supabase.auth import get_auth_manager
from haive_dataflow.supabase.persistence import get_persistence_integration

# Security schemes for Bearer token
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for Supabase authentication.
    
    Args:
        request: FastAPI request
        credentials: Authentication credentials
        
    Returns:
        User information or None if no credentials
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if user was already authenticated by middleware
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user
    
    # Skip auth if no credentials provided
    if not credentials:
        return None
    
    # Verify token
    token = credentials.credentials
    auth_manager = get_auth_manager()
    
    try:
        user_info = auth_manager.verify_jwt(token)
        
        # Store user in request state for later use
        request.state.user = user_info
        request.state.authenticated = True
        
        return user_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Optional[Dict[str, Any]]:
    """
    Similar to get_current_user but never raises an exception.
    
    Args:
        user: User from get_current_user dependency
        
    Returns:
        User information or None
    """
    return user

def require_auth(permissions: Optional[List[str]] = None):
    """
    Create dependency that requires authentication with optional permissions.
    
    Args:
        permissions: Optional list of required permissions
        
    Returns:
        FastAPI dependency
    """
    async def auth_dependency(
        request: Request,
        user: Optional[Dict[str, Any]] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check permissions if specified
        if permissions:
            auth_manager = get_auth_manager()
            if not auth_manager.check_permissions(user, permissions):
                user_permissions = user.get("permissions", [])
                missing = [p for p in permissions if p not in user_permissions]
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing)}"
                )
        
        return user
    
    return auth_dependency

def require_thread_ownership(thread_id_path: str = "thread_id"):
    """
    Create dependency that requires ownership of a thread.
    
    Args:
        thread_id_path: Path parameter name for thread ID
        
    Returns:
        FastAPI dependency
    """
    async def ownership_dependency(
        request: Request,
        user: Dict[str, Any] = Depends(require_auth(["threads:own"])),
    ) -> Dict[str, Any]:
        # Get thread ID from path parameters
        thread_id = request.path_params.get(thread_id_path)
        if not thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing thread ID parameter: {thread_id_path}"
            )
        
        # Check thread ownership
        persistence = get_persistence_integration()
        user_id = user.get("id")
        
        # Admins can access any thread
        is_admin = "admin" in user.get("app_metadata", {}).get("roles", [])
        has_manage_permission = "threads:manage" in user.get("permissions", [])
        
        if is_admin or has_manage_permission:
            return user
        
        # Check ownership for regular users
        if not persistence.check_thread_ownership(thread_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this thread"
            )
        
        return user
    
    return ownership_dependency

# Common dependencies
CurrentUser = Annotated[Optional[Dict[str, Any]], Depends(get_current_user)]
OptionalUser = Annotated[Optional[Dict[str, Any]], Depends(get_optional_user)]
AuthenticatedUser = Annotated[Dict[str, Any], Depends(require_auth())]
AdminUser = Annotated[Dict[str, Any], Depends(require_auth(["threads:manage"]))]