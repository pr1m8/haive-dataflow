# haive/dataflow/auth/supabase.py
from typing import Optional, Dict, Any, Union
import jwt
import logging
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from haive.dataflow.config.environment import SupabaseClientConfig, SupabaseServerConfig

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class SupabaseAuth:
    """Authentication provider using Supabase JWT."""
    
    def __init__(self, server_config: Optional[SupabaseServerConfig] = None):
        """Initialize with server-side config (for backend operations)."""
        self.config = server_config or SupabaseServerConfig()
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Supabase JWT token and return payload if valid."""
        if not token:
            return None
            
        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret.get_secret_value(),
                algorithms=["HS256"]
            )
            return payload
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    def get_user_id(self, token: str) -> Optional[str]:
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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth: SupabaseAuth = Depends(get_auth_instance)
) -> Optional[str]:
    """
    Verify the token and return the user ID.
    
    This is for frontend API routes - can be used with FastAPI Depends.
    """
    if not credentials:
        return None
        
    user_id = auth.get_user_id(credentials.credentials)
    if not user_id:
        return None
        
    return user_id

# Required auth middleware that raises an exception for unauthorized access
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