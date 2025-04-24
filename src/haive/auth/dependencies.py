# haive_dataflow/auth/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from haive.dataflow.auth.supabase import SupabaseAuth
from haive.dataflow.config.environment import get_supabase_server_config

# Security scheme for auth header
security = HTTPBearer(auto_error=False)

# Get auth instance for dependency injection
def get_auth_instance():
    """Get the auth instance for dependency injection."""
    config = get_supabase_server_config()
    return SupabaseAuth(config)

# Optional auth - returns user_id if authenticated, None otherwise
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth: SupabaseAuth = Depends(get_auth_instance)
) -> Optional[str]:
    """
    Verify the token and return the user ID if valid.
    
    This is for routes where auth is optional.
    """
    if not credentials:
        return None
        
    user_id = auth.get_user_id(credentials.credentials)
    return user_id  # Will be None if invalid

# Required auth - raises exception if not authenticated
async def require_auth(
    user_id: Optional[str] = Depends(get_current_user)
) -> str:
    """
    Require authentication for a route.
    
    Raises HTTPException if not authenticated.
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id