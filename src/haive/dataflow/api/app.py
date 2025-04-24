# haive_dataflow/api/app.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from haive.dataflow.auth.middleware import SupabaseAuthMiddleware
from haive.dataflow.api.middleware.logging import RequestLoggingMiddleware
from haive.dataflow.api.middleware.rate_limit import RateLimitMiddleware
from haive.dataflow.api.routes.agent_routes import router as agent_router
from haive.dataflow.api.routes.conversation_routes import router as conversation_router
from haive.dataflow.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app
    app = FastAPI(
        title=settings.api.title,
        description="API for the Haive AI Framework",
        version="1.0.0",
        debug=settings.api.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, rate_limit_per_minute=settings.api.rate_limit)
    app.add_middleware(SupabaseAuthMiddleware)
    
    # Include routers with prefix
    prefix = settings.api.prefix
    app.include_router(agent_router, prefix=prefix)
    app.include_router(conversation_router, prefix=prefix)
    
    # Health check endpoint
    @app.get(f"{prefix}/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok", "environment": settings.environment}
    
    return app

app = create_app()