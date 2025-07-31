#!/usr/bin/env python
"""Run the Haive Game API with the dynamically discovered game agents.

This script creates a FastAPI application that includes both the main API
and the game routes for all discovered game agents. It runs the server
on port 8005 with uvicorn.

Example usage:
    python -m haive.dataflow.api.run_game_api
"""

import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from .api.game_router import discover_game_agents, game_agents, get_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("game-api")

# Add package paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
packages_dir = os.path.join(haive_root, "packages")
haive_games_path = os.path.join(packages_dir, "haive-games/src")

# Add paths to sys.path for imports to work
for path in [haive_root, packages_dir, haive_games_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import after setting up paths


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

    # Include game router
    discover_game_agents()
    game_router = get_router()
    app.include_router(game_router)

    logger.info(
        f"Discovered and registered routes for {
            len(game_agents)} games: {
            list(
                game_agents.keys())}"
    )

    return app


def main():
    """Run the API server."""
    app = create_app()

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
    )


if __name__ == "__main__":
    main()
