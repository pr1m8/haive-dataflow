"""
Supabase authentication utilities for Haive.

This module provides tools for JWT verification, permission checking, and user 
context management for Supabase authentication within the Haive framework.
"""

import os
import jwt
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# Explicit import from the same package
from haive_dataflow.supabase.client import get_supabase_client

# Set up logging
logger = logging.getLogger(__name__)

class SupabaseAuthConfig(BaseModel):
    """Configuration for Supabase authentication integration."""
    auth_enabled: bool = Field(
        default=True,
        description="Whether Supabase authentication is enabled"
    )
    auth_required: bool = Field(
        default=False,
        description="Whether authentication is required"
    )
    required_permissions: List[str] = Field(
        default_factory=list,
        description="Required permissions for access"
    )
    thread_ownership: bool = Field(
        default=True,
        description="Whether threads are associated with users"
    )
    use_direct_verification: bool = Field(
        default=True,
        description="Use direct JWT verification instead of API calls when possible"
    )

class SupabaseAuthManager:
    """
    Manages Supabase authentication for agent persistence.
    
    This class provides utilities for JWT verification, permission checking,
    and integrating user context with thread persistence.
    """
    
    def __init__(self, config: Optional[SupabaseAuthConfig] = None):
        """Initialize with optional configuration."""
        self.config = config or SupabaseAuthConfig()
        self.supabase = get_supabase_client()
        
        # Get JWT secret from environment
        self.jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
        if not self.jwt_secret and self.config.use_direct_verification:
            logger.warning("SUPABASE_JWT_SECRET not set - falling back to API verification")
    
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token and extract user information.
        
        Uses direct verification if JWT secret is available,
        otherwise falls back to Supabase API verification.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Dictionary with user information
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Try direct verification if JWT secret is available and enabled
            if self.jwt_secret and self.config.use_direct_verification:
                return self._verify_jwt_direct(token)
            
            # Fall back to API verification
            return self._verify_jwt_api(token)
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    def _verify_jwt_direct(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token directly using JWT secret.
        
        Args:
            token: JWT token
            
        Returns:
            User information dictionary
        """
        try:
            # Some JWT libraries may need help with Base64 encoding
            # If you're having issues with verification, try this preprocessing
            token = self._prepare_token_for_verification(token)
            
            # Decode and verify the JWT token
            decoded_token = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": True}
            )
            
            # Check token expiration
            if "exp" in decoded_token and datetime.now(timezone.utc).timestamp() > decoded_token["exp"]:
                raise ValueError("Token has expired")
                
            # Extract user information from the decoded token
            user_id = decoded_token.get("sub")
            if not user_id:
                raise ValueError("Invalid token: missing subject")
            
            # Construct user info from token claims
            app_metadata = decoded_token.get("app_metadata", {})
            user_metadata = decoded_token.get("user_metadata", {})
            
            user_info = {
                "id": user_id,
                "email": decoded_token.get("email"),
                "metadata": user_metadata,
                "app_metadata": app_metadata,
                "permissions": self._extract_permissions_from_metadata(app_metadata),
            }
            
            return user_info
        except jwt.PyJWTError as e:
            logger.warning(f"Direct JWT verification failed: {str(e)}, falling back to API verification")
            # Fall back to API verification
            return self._verify_jwt_api(token)
    
    def _prepare_token_for_verification(self, token: str) -> str:
        """
        Prepare Supabase JWT token for verification by restoring proper Base64 encoding.
        
        Supabase JWTs use URL-safe Base64 (replacing '+' with '-' and '/' with '_').
        Some JWT libraries need help with this encoding.
        
        Args:
            token: JWT token
            
        Returns:
            Processed token
        """
        parts = token.split('.')
        if len(parts) != 3:
            return token
        
        # Most JWT libraries handle this automatically, so this is a fallback
        # Only uncomment and use if you're having issues with verification
        
        # # Replace URL-safe characters and add padding if needed
        # for i in range(2):  # Only process header and payload
        #     # Replace URL-safe characters
        #     parts[i] = parts[i].replace('-', '+').replace('_', '/')
        #     
        #     # Add padding if needed
        #     remainder = len(parts[i]) % 4
        #     if remainder > 0:
        #         parts[i] += '=' * (4 - remainder)
        # 
        # return '.'.join(parts)
        
        return token
    
    def _verify_jwt_api(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token using Supabase API.
        
        Args:
            token: JWT token
            
        Returns:
            User information dictionary
        """
        # Use the Supabase client to verify the token
        user_response = self.supabase.auth.get_user(token)
        user = user_response.user
        
        if not user:
            raise ValueError("Invalid or expired token")
        
        # Extract user information
        user_info = {
            "id": user.id,
            "email": user.email,
            "metadata": user.user_metadata or {},
            "app_metadata": user.app_metadata or {},
            "permissions": self._extract_permissions_from_metadata(user.app_metadata or {}),
        }
        
        return user_info
    
    def _extract_permissions_from_metadata(self, app_metadata: Dict[str, Any]) -> List[str]:
        """
        Extract permissions from app_metadata.
        
        Args:
            app_metadata: App metadata dictionary
            
        Returns:
            List of permission strings
        """
        permissions = []
        
        # Extract direct permissions if present
        if "permissions" in app_metadata:
            if isinstance(app_metadata["permissions"], list):
                permissions.extend(app_metadata["permissions"])
            
        # Map roles to permissions if needed
        roles = app_metadata.get("roles", [])
        if roles and isinstance(roles, list):
            # Map from roles to permissions
            # This is configurable based on your Supabase setup
            role_permissions = {
                "admin": ["agent:use", "agent:create", "threads:manage"],
                "user": ["agent:use", "threads:own"]
            }
            
            for role in roles:
                if role in role_permissions:
                    permissions.extend(role_permissions[role])
        
        return list(set(permissions))  # Remove duplicates
    
    def check_permissions(self, user_info: Dict[str, Any], required_permissions: List[str] = None) -> bool:
        """
        Check if user has required permissions.
        
        Args:
            user_info: User information from verify_jwt
            required_permissions: Optional override for required permissions
            
        Returns:
            True if user has all required permissions, False otherwise
        """
        # Use provided permissions or fall back to configured permissions
        required = required_permissions or self.config.required_permissions
        
        if not required:
            return True
        
        user_permissions = user_info.get("permissions", [])
        return all(p in user_permissions for p in required)
    
    def extract_token_from_request(self, request) -> Optional[str]:
        """
        Extract JWT token from request headers.
        
        Args:
            request: HTTP request object
            
        Returns:
            Token string or None
        """
        headers = getattr(request, "headers", {})
        
        if callable(headers):
            headers = headers()
        
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1]
        return None
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh an access token using the refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dictionary with new access_token and refresh_token
            
        Raises:
            ValueError: If token refresh fails
        """
        try:
            # Use Supabase client to refresh the token
            refresh_response = self.supabase.auth.refresh_session(refresh_token)
            session = refresh_response.session
            
            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token
            }
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise ValueError(f"Token refresh failed: {str(e)}")

# Singleton instance
_auth_manager = None

def get_auth_manager(config: Optional[SupabaseAuthConfig] = None) -> SupabaseAuthManager:
    """Get or create Supabase auth manager singleton."""
    global _auth_manager
    if _auth_manager is None or config is not None:
        _auth_manager = SupabaseAuthManager(config)
    return _auth_manager