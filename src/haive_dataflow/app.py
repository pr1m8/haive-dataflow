"""
Main FastAPI application for Haive Dataflow.

This module provides the main FastAPI application setup, including middleware,
routers, and exception handlers for the Haive Dataflow API.
"""

import os
import logging
from typing import Callable, Dict, Any, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .supabase.middleware import SupabaseAuthMiddleware, UserContextMiddleware
from .api.auth import auth_router

# Set up logging
logger = logging.getLogger(__name__)

def create_app(
    title: str = "Haive API",
    description: str = "API for Haive Framework",
    version: str = "0.1.0",
    debug: bool = False,
    additional_routers: List[Any] = None,
    additional_middleware: List[Callable] = None,
    cors_origins: List[str] = None,
    exclude_auth_paths: List[str] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        title: API title
        description: API description
        version: API version
        debug: Enable debug mode
        additional_routers: Additional routers to include
        additional_middleware: Additional middleware to add
        cors_origins: CORS allowed origins
        exclude_auth_paths: Paths to exclude from authentication
        
    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app with appropriate configuration
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        debug=debug,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
    )
    
    # Add exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with structured response."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body},
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],  # Customize for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Supabase authentication middleware
    app.add_middleware(
        SupabaseAuthMiddleware,
        exclude_paths=exclude_auth_paths or ["/docs", "/openapi.json", "/redoc", "/health"],
    )
    
    # Add user context middleware
    app.add_middleware(UserContextMiddleware)
    
    # Add additional middleware
    if additional_middleware:
        for middleware in additional_middleware:
            app.add_middleware(middleware)
    
    # Include routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    
    # Include additional routers
    if additional_routers:
        for router in additional_routers:
            app.include_router(router)
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": version}
    
    # Add static files if in debug mode or if SERVE_STATIC is set
    if debug or os.getenv("SERVE_STATIC", "").lower() in ("1", "true", "yes"):
        static_dir = os.getenv("STATIC_DIR", "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Custom OpenAPI documentation if not in debug mode
    if not debug:
        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{title} - API Documentation",
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css",
            )
        
        @app.get("/openapi.json", include_in_schema=False)
        async def get_open_api_endpoint():
            return get_openapi(
                title=title,
                version=version,
                description=description,
                routes=app.routes,
            )
    
    return app

# Default app instance
app = create_app(
    title=os.getenv("API_TITLE", "Haive API"),
    description=os.getenv("API_DESCRIPTION", "API for Haive Framework"),
    version=os.getenv("API_VERSION", "0.1.0"),
    debug=os.getenv("DEBUG", "").lower() in ("1", "true", "yes"),
    cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
)