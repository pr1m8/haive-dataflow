# src/haive_dataflow/api/auth.py

from typing import Dict, Any, Optional, List
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Use absolute import path
from haive_dataflow.supabase import get_auth_manager

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency for Supabase authentication.
    
    Args:
        request: FastAPI request
        credentials: Authentication credentials
        
    Returns:
        User information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Skip auth if no credentials provided
    if not credentials:
        return None
        
    # Verify token
    token = credentials.credentials
    auth_manager = get_auth_manager()
    
    try:
        user_info = auth_manager.verify_jwt(token)
        return user_info
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

def require_auth(permissions: Optional[List[str]] = None):
    """
    Create dependency that requires authentication with optional permissions.
    
    Args:
        permissions: Optional list of required permissions
        
    Returns:
        FastAPI dependency
    """
    async def auth_dependency(
        user: Optional[Dict[str, Any]] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
            
        # Check permissions if specified
        if permissions:
            user_permissions = user.get("permissions", [])
            missing = [p for p in permissions if p not in user_permissions]
            
            if missing:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required permissions: {', '.join(missing)}"
                )
                
        return user
        
    return auth_dependency