#!/usr/bin/env python3
"""Test with agents that are actually available."""

import asyncio
import contextlib
import json
import os
import urllib.parse
from datetime import UTC, datetime, timedelta

import jwt
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_test_jwt():
    """Create a test JWT token for Supabase."""
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        return None

    payload = {
        "sub": "test-user-123",
        "aud": "authenticated",
        "role": "authenticated",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }

    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


async def test_available_agents():
    """Test with agents that are available according to the logs."""
    token = create_test_jwt()
    if not token:
        return False

    # Agents from the game discovery log that were successfully registered
    available_agents = [
        "among_us",
        "battleship",
        "checkers",
        "chess",
        "clue",
        "connect4",
        "debate",
        "dominoes",
        "fox_and_geese",
        "mafia",
        "mancala",
        "mastermind",
        "nim",
        "poker",
        "reversi",
        "tic_tac_toe",
    ]

    base_url = "ws://localhost:8000"

    for agent_name in available_agents[:3]:  # Test first 3
        # Simple URL without config
        uri = f"{base_url}/api/ws/chat/{agent_name}?token={urllib.parse.quote(token)}"

        try:
            websocket = await websockets.connect(uri)

            # Send a test message
            test_message = {
                "type": "message",
                "content": f"Hello {agent_name}! Please respond to this test message so we can confirm Supabase persistence is working.",
            }

            await websocket.send(json.dumps(test_message))

            # Wait for response
            try:
                await asyncio.wait_for(websocket.recv(), timeout=15)

                # Try to get one more message
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(websocket.recv(), timeout=5)

                await websocket.close()
                return True

            except TimeoutError:
                await websocket.close()

        except Exception:
            continue

    return False


if __name__ == "__main__":
    result = asyncio.run(test_available_agents())
    if result:
        pass
    else:
        pass
