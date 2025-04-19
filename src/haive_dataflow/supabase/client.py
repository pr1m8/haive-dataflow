# haive_dataflow/supabase/client.py
import os
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class SupabaseConfig(BaseModel):
    """Configuration for Supabase integration."""
    url: str = Field(..., description="Supabase project URL")
    key: str = Field(..., description="Supabase API key")
    jwt_secret: Optional[str] = Field(None, description="JWT secret for token verification")
    
    class Config:
        extra = "allow"

class SupabaseClient:
    """Client for Supabase integration with Haive framework."""
    
    def __init__(self, config: Optional[SupabaseConfig] = None):
        """Initialize Supabase client with optional configuration."""
        self.config = config or self._load_from_env()
        self._client = None
        
    def _load_from_env(self) -> SupabaseConfig:
        """Load configuration from environment variables."""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
        
        if not url or not key:
            raise ValueError("Supabase URL and key must be provided via config or environment variables")
        
        return SupabaseConfig(url=url, key=key, jwt_secret=jwt_secret)
    
    @property
    def client(self):
        """Get or create Supabase client."""
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self.config.url, self.config.key)
            except ImportError:
                raise ImportError("Supabase package not installed. Install with: pip install supabase")
        return self._client
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token and extract user information.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Dictionary with user information from token
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Option 1: Use Supabase client if available
            user = self.client.auth.get_user(token)
            return {
                "supabase_user_id": user.id,
                "email": user.email,
                "metadata": user.user_metadata,
                "app_metadata": user.app_metadata
            }
        except Exception as e:
            # Option 2: Manual JWT verification if client approach fails
            try:
                import jwt
                
                if not self.config.jwt_secret:
                    raise ValueError("JWT secret is required for manual token verification")
                
                decoded = jwt.decode(
                    token, 
                    self.config.jwt_secret, 
                    algorithms=["HS256"],
                    options={"verify_signature": True}
                )
                
                return {
                    "supabase_user_id": decoded.get("sub"),
                    "email": decoded.get("email"),
                    "metadata": decoded.get("user_metadata", {}),
                    "app_metadata": decoded.get("app_metadata", {})
                }
            except Exception as jwt_error:
                raise ValueError(f"Invalid token: {str(jwt_error)} (original error: {str(e)})")
    
    def extract_permissions(self, user_data: Dict[str, Any]) -> list:
        """
        Extract permissions from user data.
        
        Args:
            user_data: User data from verify_token
            
        Returns:
            List of permission strings
        """
        # Extract from app_metadata (customize based on your Supabase schema)
        app_metadata = user_data.get("app_metadata", {})
        return app_metadata.get("permissions", [])

# Singleton instance
_supabase_client = None

def get_supabase_client(config: Optional[SupabaseConfig] = None) -> SupabaseClient:
    """
    Get or create the Supabase client singleton.
    
    Args:
        config: Optional configuration to override environment variables
        
    Returns:
        SupabaseClient instance
    """
    global _supabase_client
    if _supabase_client is None or config is not None:
        _supabase_client = SupabaseClient(config)
    return _supabase_client