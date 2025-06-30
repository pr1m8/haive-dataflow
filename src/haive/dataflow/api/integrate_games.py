#!/usr/bin/env python
"""Integration module for adding game routes to the main Haive API.

This module provides functions to add game WebSocket endpoints and routes
to an existing FastAPI application. It integrates with the game_router module
to discover and register game agents dynamically.

Usage:
    ```python
    from haive.dataflow.api.app import app
    from haive.dataflow.api.integrate_games import add_game_routes

    # Add game routes to the main app
    add_game_routes(app)
    ```
"""

import logging
import os
import sys

from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("games-integration")


def configure_import_paths():
    """Configure import paths for game_router module."""
    # Get the path to the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Add haive_root and packages to sys.path
    haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
    packages_dir = os.path.join(haive_root, "packages")
    haive_games_path = os.path.join(packages_dir, "haive-games/src")

    # Add paths to sys.path for imports to work
    for path in [haive_root, packages_dir, haive_games_path]:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Add current directory to path to find game_router
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)


def add_game_routes(app: FastAPI, prefix: str = "/games"):
    """Add game routes to the main API.

    This function discovers game agents and adds routes for each game type
    to the provided FastAPI application. It creates both REST endpoints and
    WebSocket endpoints for real-time game state streaming.

    Args:
        app: The FastAPI application to add routes to
        prefix: The URL prefix for game routes (default: "/games")

    Returns:
        The updated FastAPI application
    """
    # Configure import paths
    configure_import_paths()

    # Import game_router after setting up paths
    try:
        import game_router

        # Discover game agents
        game_router.discover_game_agents()

        # Check if we found any games
        if not game_router.game_agents:
            logger.warning("No game agents discovered. Game routes will not be added.")
            return app

        # Create a router with all game routes
        games_router = game_router.get_router()

        # Add the router to the app with the specified prefix
        app.include_router(games_router, prefix=prefix)

        logger.info(
            f"Added routes for {len(game_router.game_agents)} games: {list(game_router.game_agents.keys())}"
        )

        return app

    except ImportError as e:
        logger.error(f"Failed to import game_router module: {e}")
        return app
    except Exception as e:
        logger.error(f"Error adding game routes: {e}", exc_info=True)
        return app
