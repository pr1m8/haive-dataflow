#!/usr/bin/env python3
"""Chess API demonstration script.

This script launches a standalone API server for the chess game
with WebSocket support and Supabase integration.

Usage:
    python run_chess_api.py [--port PORT]

Environment variables:
    SUPABASE_URL: The URL of your Supabase instance
    SUPABASE_SERVICE_KEY: Service role API key
    SUPABASE_ANON_KEY: Anonymous API key
"""

import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from game_api import GameAPIFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("chess-api")


def verify_environment() -> bool:
    """Verify that required environment variables are set."""
    required_vars = []

    # Check for Supabase environment variables
    if not os.getenv("SUPABASE_URL"):
        logger.warning("SUPABASE_URL environment variable is not set")
        required_vars.append("SUPABASE_URL")

    if not os.getenv("SUPABASE_SERVICE_KEY") and not os.getenv("SUPABASE_ANON_KEY"):
        logger.warning("Neither SUPABASE_SERVICE_KEY nor SUPABASE_ANON_KEY is set")
        required_vars.append("SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY")

    if required_vars:
        logger.warning(
            f"Missing required environment variables: {', '.join(required_vars)}"
        )
        logger.warning("Will fall back to memory persistence if Supabase is requested")
        return False

    return True


def run_chess_api(port: int = 8000):
    """Run the chess API server."""
    try:
        # Fix imports for local development

        # Add the parent directories to the path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        )
        packages_dir = os.path.dirname(parent_dir)

        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if packages_dir not in sys.path:
            sys.path.insert(0, packages_dir)

        # Import locally

        # Create chess API
        chess_api = GameAPIFactory.create_chess_api()
        logger.info("Chess API created successfully")

        # Run the server
        logger.info(f"Starting chess API server on port {port}")
        chess_api.run(host="0.0.0.0", port=port)

    except ImportError as e:
        logger.exception(f"Failed to import required modules: {e}")
        logger.exception(
            "Make sure haive.games.chess and haive.dataflow.api are installed"
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting chess API: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Parse arguments and run the chess API server."""
    # Load environment variables from .env file if present
    load_dotenv()

    # Verify environment
    verify_environment()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run chess API server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    args = parser.parse_args()

    # Fix for Windows asyncio issues
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the server
    run_chess_api(port=args.port)


if __name__ == "__main__":
    main()
