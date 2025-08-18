#!/usr/bin/env python
"""Run the Haive Games API with dynamic game discovery.

This script runs a standalone API for game agents with dynamic discovery
from the haive-games package. It creates WebSocket endpoints for each
discovered game agent and provides HTML clients for testing.

Usage:
    python run_games_api.py
"""

import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from haive.dataflow.api.game_router import discover_game_agents, game_agents, get_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("games-api")

# Add package paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
packages_dir = os.path.join(haive_root, "packages")
haive_games_path = os.path.join(packages_dir, "haive-games/src")

# Add paths to sys.path for imports to work
for path in [src_dir, haive_root, packages_dir, haive_games_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set environment variables for development
os.environ["HAIVE_ENV"] = os.environ.get("HAIVE_ENV", "development")


def create_app():
    """Create FastAPI app with game routes."""
    # Create FastAPI app
    app = FastAPI(
        title="Haive Games API",
        description="API for Haive game agents with dynamic discovery",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add the game router
    try:
        # Import the game_router module

        # Discover game agents
        discover_game_agents()

        if game_agents:
            # Create a router with all game routes
            games_router = get_router()

            # Add the router to the app
            app.include_router(games_router)

            logger.info(
                f"Added routes for {len(game_agents)} games: {list(game_agents.keys())}"
            )

            # Add main route
            @app.get("/", response_class=HTMLResponse)
            async def root():
                """Root endpoint that redirects to games index."""
                return RedirectResponse(url="/games")

            # Add health check
            @app.get("/health")
            async def health_check():
                """Health check endpoint."""
                return {
                    "status": "ok",
                    "available_games": list(game_agents.keys()),
                    "game_count": len(game_agents),
                }

        else:
            logger.warning("No game agents discovered.")

            # Add fallback route
            @app.get("/", response_class=HTMLResponse)
            async def root():
                """Root.
"""
                return """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Haive Games API</title>
                    </head>
                    <body>
                        <h1>Haive Games API</h1>
                        <p>No game agents were discovered. Please check the logs for details.</p>
                    </body>
                </html>
                """

    except Exception as e:
        logger.error(f"Error setting up game routes: {e}", exc_info=True)
        error_message = str(e)

        # Add fallback route
        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Root.
"""
            return f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Haive Games API</title>
                </head>
                <body>
                    <h1>Haive Games API</h1>
                    <p>Error: {error_message}</p>
                </body>
            </html>
            """

    return app


def main():
    """Run the games API server."""
    app = create_app()

    # Run server on port 8005 (different from main API)
    logger.info("Starting Games API server on http://localhost:8005")
    logger.info("Access the game list at http://localhost:8005/games")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
    )


if __name__ == "__main__":
    main()
