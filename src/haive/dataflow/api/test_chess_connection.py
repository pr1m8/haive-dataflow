#!/usr/bin/env python
"""
Simple test client for the chess game WebSocket.

This script attempts to connect to the chess game WebSocket,
and prints the response. It can be used to verify that the
game router is working correctly.

Usage:
    python test_chess_connection.py
"""

import asyncio
import json
import logging
import sys

import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chess-test-client")


async def test_connection():
    """Test WebSocket connection to the chess game."""
    # WebSocket URL for chess game
    game_id = "test123"
    uri = f"ws://localhost:8005/api/ws/chess/{game_id}"

    logger.info(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected successfully!")

            # Receive initial state
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(
                f"Initial state received: {json.dumps(data, indent=2)[:200]}..."
            )

            # Request AI move
            logger.info("Requesting AI move...")
            await websocket.send(json.dumps({"type": "ai_move"}))

            # Receive state after AI move
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"State after AI move: {json.dumps(data, indent=2)[:200]}...")

            # Request game state
            logger.info("Requesting game state...")
            await websocket.send(json.dumps({"type": "get_state"}))

            # Receive game state
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Game state received: {json.dumps(data, indent=2)[:200]}...")

            logger.info("Test completed successfully!")

    except Exception as e:
        logger.error(f"Error connecting to WebSocket: {e}")
        return False

    return True


def main():
    """Run the test client."""
    logger.info("Starting test client for chess game...")

    # Run the test
    result = asyncio.run(test_connection())

    if result:
        logger.info("Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
