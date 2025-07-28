"""Run_Simple core module.

This module provides run simple functionality for the Haive framework.

Functions:
    main: Main functionality.
"""

#!/usr/bin/env python
"""Simple standalone script to run the Haive Game API.

This script runs the game router directly without depending on other Haive modules.
It's designed for testing the game router functionality in isolation.
"""

import logging
import os
import sys

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("simple-game-api")

# Get the path to the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Import the game_router module directly
sys.path.insert(0, current_dir)
import game_router


def main():
    """Run the API server."""
    # Create the app using the standalone function
    app = game_router.create_game_router_app()

    # Run server
    logger.info("Starting game API server on http://localhost:8005")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
    )


if __name__ == "__main__":
    main()
