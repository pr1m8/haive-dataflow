"""Run_Integrated_Api core module.

This module provides run integrated api functionality for the Haive framework.

Functions:
    main: Main functionality.
"""

#!/usr/bin/env python
"""Run the integrated Haive API with game support.

This script runs the main Haive API with the integrated game routes.
It sets up proper import paths and runs the app with uvicorn.

Usage:
    python run_integrated_api.py
"""

import logging
import os
import sys

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("integrated-api")

# Add package paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Set environment variables for development
os.environ["HAIVE_ENV"] = os.environ.get("HAIVE_ENV", "development")


def main():
    """Run the integrated API."""
    try:
        # Import the app
        from haive.dataflow.api.app import app

        logger.info("Starting integrated Haive API with game support...")
        logger.info("Server will be available at http://localhost:8000")

        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
    except Exception as e:
        logger.error(f"Failed to start API: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
