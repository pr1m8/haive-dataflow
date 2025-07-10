"""Haive API Application Module.

This module defines and configures the FastAPI application for the Haive framework.
It sets up middleware, routes, and the core API functionality.

The API provides RESTful and WebSocket endpoints for interacting with the Haive
registry, agents, conversations, and LLM models. It includes authentication,
request logging, and rate limiting middleware.

It also provides WebSocket endpoints for streaming game agent states, with
dynamic discovery of available games from the haive-games package.

Typical usage example:

    ```python
    from haive.dataflow.api.app import app
    import uvicorn

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    ```
"""

import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from haive.dataflow.api.middleware.logging import RequestLoggingMiddleware
from haive.dataflow.api.middleware.rate_limit import RateLimitMiddleware
from haive.dataflow.api.routes.agent_discovery_routes import (
    router as agent_discovery_router,
)
from haive.dataflow.api.routes.agent_routes import router as agent_router
from haive.dataflow.api.routes.conversation_routes import router as conversation_router
from haive.dataflow.api.routes.llm_routes import router as llm_router
from haive.dataflow.api.routes.routes import router as react_agent_router
from haive.dataflow.api.routes.tools_routes import router as tools_router
from haive.dataflow.auth.middleware import SupabaseAuthMiddleware
from haive.dataflow.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

import os
import logging
from fastapi import FastAPI
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from haive.agents.simple.agent import SimpleAgent
from langgraph.checkpoint.postgres import PostgresSaver

from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
 
def create_lifespan(api_prefix: str):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Create the agent with async persistence for CopilotKit
        graph = SimpleAgent(
            checkpoint_mode="async"  # Use async mode for CopilotKit
        )
        
        # Set up the async checkpointer properly in the async context
        if hasattr(graph, '_async_setup_needed') and graph._async_setup_needed:
            try:
                from haive.core.persistence.handlers import setup_async_checkpointer
                if hasattr(graph, '_async_persistence_config'):
                    graph.checkpointer = await setup_async_checkpointer(graph._async_persistence_config)
                    graph._async_setup_needed = False
                    print(f"Async checkpointer set up successfully: {type(graph.checkpointer).__name__}")
            except Exception as e:
                print(f"Error setting up async checkpointer in lifespan: {e}")
                # Fall back to memory checkpointer
                from langgraph.checkpoint.memory import MemorySaver
                graph.checkpointer = MemorySaver()
        
        # Now compile the graph with the properly set up checkpointer
        compiled_graph = graph.compile()

        sdk = CopilotKitRemoteEndpoint(
            agents=[
                LangGraphAgent(
                    name="simple_agent",
                    description="Simple agent.",
                    graph=compiled_graph,
                ),
            ],
        )
        
        # Add the endpoint to the app
        add_fastapi_endpoint(app, sdk, f"{api_prefix}/copilotkit")
        
        yield
    return lifespan

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    This function creates a new FastAPI application instance, configures middleware
    for CORS, authentication, logging, and rate limiting, and registers the API
    routes for agents, conversations, LLM models, and game agents.

    The application configuration is loaded from settings, allowing for
    environment-specific customization.

    Returns:
        FastAPI: A configured FastAPI application instance ready to serve requests.

    Example:
        >>> app = create_app()
        >>> # Run the app with Uvicorn
        >>> import uvicorn
        >>> uvicorn.run(app, host="0.0.0.0", port=8000)
    """

    prefix = settings.api.prefix
    # Create FastAPI app
    app = FastAPI(
        title=settings.api.title,
        description="API for the Haive AI Framework",
        version="1.0.0",
        debug=settings.api.debug,
        lifespan=create_lifespan(prefix),
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
    app.add_middleware(
        RateLimitMiddleware, rate_limit_per_minute=settings.api.rate_limit
    )
    app.add_middleware(SupabaseAuthMiddleware)

    # Include routers with prefix
    prefix = settings.api.prefix
    app.include_router(agent_router, prefix=prefix)
    app.include_router(agent_discovery_router, prefix=prefix)
    app.include_router(conversation_router, prefix=prefix)
    app.include_router(llm_router, prefix=prefix)
    app.include_router(react_agent_router, prefix=prefix)
    app.include_router(tools_router, prefix=prefix)

    # Health check endpoint
    @app.get(f"{prefix}/health")
    async def health_check():
        """Health check endpoint.

        This endpoint provides a simple health check for the API, returning
        a status and the current environment. It can be used by monitoring
        tools to verify that the API is running and responsive.

        Returns:
            dict: A dictionary containing the status ("ok") and the current environment.

        Example:
            >>> response = requests.get("http://localhost:8000/api/health")
            >>> print(response.json())
            {"status": "ok", "environment": "development"}
        """
        return {"status": "ok", "environment": settings.environment}

    # Add game routes
    try:
        # Configure import paths for game_router
        current_dir = os.path.dirname(os.path.abspath(__file__))
        haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
        packages_dir = os.path.join(haive_root, "packages")
        haive_games_path = os.path.join(packages_dir, "haive-games/src")

        # Add paths to sys.path for imports to work
        for path in [haive_root, packages_dir, haive_games_path]:
            if path not in sys.path:
                sys.path.insert(0, path)

        # Import game_router after setting up paths
        from haive.dataflow.api.game_router import (
            discover_game_agents,
            game_agents,
            get_router,
        )

        # Discover game agents
        logger.info("Discovering game agents...")
        discover_game_agents()

        if game_agents:
            # Create a router with all game routes
            logger.info(
                f"Found {len(game_agents)} game agents: {list(game_agents.keys())}"
            )
            games_router = get_router()

            # Add the router to the app with the specified prefix
            app.include_router(games_router, prefix=f"{prefix}/games")
            logger.info("Game routes added successfully")
    except Exception as e:
        logger.error(f"Failed to add game routes: {e}", exc_info=True)

    return app


app = create_app()


import logging

# In your main.py file
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Log the full error details
    logger.error(f"Validation error in request: {request.url}")
    for error in exc.errors():
        logger.error(f"Error: {error}")

    # Return a more detailed response
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error in request data", "errors": exc.errors()},
    )
