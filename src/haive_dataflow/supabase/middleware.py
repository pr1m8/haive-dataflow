"""
Middleware for Supabase authentication in FastAPI applications.

This module provides middleware components that integrate Supabase authentication
with FastAPI, enabling authentication verification and user context injection.
"""

from typing import Optional, Dict, Any, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from .auth import get_auth_manager
from .persistence import get_persistence_integration

class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for Supabase authentication and persistence integration.
    
    This middleware:
    1. Extracts and verifies JWT tokens from request headers
    2. Makes user information available in request state
    3. Integrates with the persistence layer for thread management
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        exclude_paths: Optional[list[str]] = None,
        on_auth_success: Optional[Callable[[Request, Dict[str, Any]], Awaitable[None]]] = None,
        on_auth_failure: Optional[Callable[[Request, Exception], Awaitable[None]]] = None
    ):
        """
        Initialize the middleware with the app and optional callbacks.
        
        Args:
            app: The ASGI application
            exclude_paths: List of path prefixes to exclude from authentication
            on_auth_success: Optional callback for successful authentication
            on_auth_failure: Optional callback for failed authentication
        """
        super().__init__(app)
        self.auth_manager = get_auth_manager()
        self.persistence = get_persistence_integration()
        self.exclude_paths = exclude_paths or ["/docs", "/openapi.json", "/redoc"]
        self.on_auth_success = on_auth_success
        self.on_auth_failure = on_auth_failure
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request, add authentication information.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint
            
        Returns:
            Response from the next handler
        """
        # Skip processing for excluded paths
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        # Extract token from Authorization header
        token = self._extract_token(request)
        
        # Verify token if present
        if token:
            try:
                user_info = self.auth_manager.verify_jwt(token)
                
                # Store user in request state
                request.state.user = user_info
                request.state.authenticated = True
                
                # Register thread if provided in query parameters
                thread_id = request.query_params.get("thread_id")
                if thread_id:
                    self.persistence.register_thread(thread_id, user_info)
                
                # Call success callback if provided
                if self.on_auth_success:
                    await self.on_auth_success(request, user_info)
                    
            except Exception as e:
                # Failed authentication - don't add user to state
                request.state.authenticated = False
                request.state.auth_error = str(e)
                
                # Call failure callback if provided
                if self.on_auth_failure:
                    await self.on_auth_failure(request, e)
        else:
            # No token provided
            request.state.authenticated = False
        
        # Continue processing the request
        response = await call_next(request)
        return response
    
    def _should_skip(self, path: str) -> bool:
        """
        Check if authentication should be skipped for this path.
        
        Args:
            path: Request path
            
        Returns:
            True if authentication should be skipped, False otherwise
        """
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from request headers.
        
        Args:
            request: The incoming request
            
        Returns:
            Token string or None
        """
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1]
        return None


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for injecting user context into requests.
    
    This middleware:
    1. Adds a comprehensive user context object to request state
    2. Handles anonymous users with appropriate default context
    3. Makes common user attributes directly accessible in templates
    """
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware with the app."""
        super().__init__(app)
        self.persistence = get_persistence_integration()
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request, add user context.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint
            
        Returns:
            Response from the next handler
        """
        # Check if user was authenticated by SupabaseAuthMiddleware
        if hasattr(request.state, "user") and request.state.user:
            # Create user context
            user_context = self.persistence.get_user_context(request.state.user)
            
            # Store in request state
            request.state.user_context = user_context
            
            # Add common attributes for convenience
            request.state.user_id = user_context.get("user_id")
            request.state.username = user_context.get("username", "User")
            request.state.is_admin = user_context.get("is_admin", False)
        else:
            # Anonymous user context
            request.state.user_context = {
                "is_authenticated": False,
                "username": "Anonymous",
                "is_admin": False
            }
            request.state.user_id = None
            request.state.username = "Anonymous"
            request.state.is_admin = False
        
        # Continue processing the request
        return await call_next(request)