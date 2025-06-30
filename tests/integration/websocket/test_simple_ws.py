#!/usr/bin/env python3
"""Simple WebSocket test without config parameter"""

import asyncio
import json
import os
import urllib.parse
from datetime import datetime, timedelta, timezone

import jwt
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_test_jwt():
    """Create a test JWT token for Supabase"""
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        return None

    payload = {
        "sub": "test-user-123",
        "aud": "authenticated",
        "role": "authenticated",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


async def test_simple_websocket():
    """Test WebSocket without config parameter"""

    token = create_test_jwt()
    if not token:
        print("Failed to create JWT token")
        return False

    print(f"Created JWT token: {token[:30]}...")

    # Try the simplest possible connection
    base_url = "ws://localhost:8000"
    agent_name = "SimpleAgent"

    # URL encode the token to be safe
    encoded_token = urllib.parse.quote(token)

    # Simple URL without config
    uri = f"{base_url}/api/ws/chat/{agent_name}?token={encoded_token}"
    print(f"Testing URL: {uri[:80]}...")

    try:
        print("Attempting connection...")

        websocket = await websockets.connect(uri)
        print("✓ WebSocket connected!")

        # Just wait for any initial message
        try:
            initial_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"✓ Initial message: {initial_msg}")
        except asyncio.TimeoutError:
            print("No initial message received")

        # Send a simple message
        test_message = {"type": "message", "content": "Hello!"}

        print(f"Sending: {test_message}")
        await websocket.send(json.dumps(test_message))

        # Wait for response
        response = await asyncio.wait_for(websocket.recv(), timeout=10)
        print(f"✓ Received: {response}")

        await websocket.close()
        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_simple_websocket())
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
