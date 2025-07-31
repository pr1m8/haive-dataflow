#!/usr/bin/env python3
"""Simple WebSocket test without config parameter."""

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


async def test_simple_websocket():
    """Test WebSocket without config parameter."""
    token = create_test_jwt()
    if not token:
        return False

    # Try the simplest possible connection
    base_url = "ws://localhost:8000"
    agent_name = "SimpleAgent"

    # URL encode the token to be safe
    encoded_token = urllib.parse.quote(token)

    # Simple URL without config
    uri = f"{base_url}/api/ws/chat/{agent_name}?token={encoded_token}"

    try:

        websocket = await websockets.connect(uri)

        # Just wait for any initial message
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(websocket.recv(), timeout=5)

        # Send a simple message
        test_message = {"type": "message", "content": "Hello!"}

        await websocket.send(json.dumps(test_message))

        # Wait for response
        await asyncio.wait_for(websocket.recv(), timeout=10)

        await websocket.close()
        return True

    except Exception:
        return False


if __name__ == "__main__":
    result = asyncio.run(test_simple_websocket())
