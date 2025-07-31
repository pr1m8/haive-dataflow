#!/usr/bin/env python3
"""Test agent with proper JWT token."""

import asyncio
import json
import os
from datetime import datetime, timedelta

import jwt
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_test_jwt():
    """Create a test JWT token for Supabase."""
    # Get the JWT secret from environment
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        return None

    # Create a test payload
    payload = {
        "sub": "test-user-123",  # User ID
        "aud": "authenticated",  # Required audience
        "role": "authenticated",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    # Create the token
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


async def test_agent_with_jwt():
    """Test agent connection with proper JWT."""
    # Create test token
    token = create_test_jwt()
    if not token:
        return False

    # Test with different agent names from the log
    agents_to_try = [
        "SimpleAgent",
        "CheckersAgent",
        "TicTacToeAgent",
        "connect4",
        "chess",
    ]

    base_url = "ws://localhost:8000"

    for agent_name in agents_to_try:

        # Create config
        config = {
            "agent_name": agent_name,
            "provider": "azure",
            "model": "gpt-4o",
            "stream": True,
            "persistent": True,  # Enable persistence to test Supabase
        }

        # Create WebSocket URL with proper format
        uri = f"{base_url}/api/ws/chat/{agent_name}?token={token}&config={json.dumps(config)}"

        try:
            websocket = await websockets.connect(uri)

            # Send a test message
            test_message = {
                "type": "message",
                "content": f"Hello {agent_name}! Please respond to this test message.",
            }

            await websocket.send(json.dumps(test_message))

            # Wait for response(s)
            for _i in range(5):  # Wait for up to 5 messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)

                    response_data = json.loads(response)
                    if (
                        response_data.get("type") == "status"
                        and response_data.get("content", {}).get("status") == "complete"
                    ):
                        break

                except TimeoutError:
                    break

            await websocket.close()
            return True

        except Exception:
            continue

    return False


if __name__ == "__main__":
    result = asyncio.run(test_agent_with_jwt())
