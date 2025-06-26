#!/usr/bin/env python
"""
Test script for the integrated API.

This script makes a simple request to the integrated API to verify that
both the main API and game routes are working correctly.

Usage:
    python test_integration.py
"""

import logging
import sys

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("integration-test")


def test_api_health():
    """Test the API health endpoint."""
    url = "http://localhost:8000/api/health"

    try:
        logger.info(f"Testing API health endpoint: {url}")
        response = requests.get(url)
        response.raise_for_status()

        logger.info(f"Health check successful: {response.json()}")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


def test_games_endpoint():
    """Test the games index endpoint."""
    url = "http://localhost:8000/api/games"

    try:
        logger.info(f"Testing games index endpoint: {url}")
        response = requests.get(url)
        response.raise_for_status()

        logger.info(f"Games index accessible: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Games index failed: {e}")
        return False


def main():
    """Run the integration tests."""
    logger.info("Starting integration tests...")

    health_ok = test_api_health()
    games_ok = test_games_endpoint()

    if health_ok and games_ok:
        logger.info("All tests passed! Integration is working correctly.")
        return 0
    else:
        logger.error("Integration tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
