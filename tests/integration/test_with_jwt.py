#!/usr/bin/env python3
"""Test agent with proper JWT token"""

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
    """Create a test JWT token for Supabase"""
    # Get the JWT secret from environment
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        print("No SUPABASE_JWT_SECRET found")
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
    print(f"Created test JWT token: {token[:20]}...")
    return token


async def test_agent_with_jwt():
    """Test agent connection with proper JWT"""

    # Create test token
    token = create_test_jwt()
    if not token:
        print("Failed to create JWT token")
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
        print(f"\n--- Testing {agent_name} ---")

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
        print(f"Testing URL: {uri[:80]}...")

        try:
            print("Attempting connection...")
            websocket = await websockets.connect(uri)
            print("✓ WebSocket connected!")

            # Send a test message
            test_message = {
                "type": "message",
                "content": f"Hello {agent_name}! Please respond to this test message.",
            }

            print(f"Sending message: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Wait for response(s)
            print("Waiting for response...")
            for i in range(5):  # Wait for up to 5 messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    print(f"✓ Response {i+1}: {response}")

                    response_data = json.loads(response)
                    if (
                        response_data.get("type") == "status"
                        and response_data.get("content", {}).get("status") == "complete"
                    ):
                        print("✓ Stream completed")
                        break

                except asyncio.TimeoutError:
                    print("⏰ Response timeout")
                    break

            await websocket.close()
            print(f"✓ {agent_name} test completed successfully!")
            return True

        except Exception as e:
            print(f"✗ {agent_name} connection failed: {e}")
            continue

    print("All agent tests failed")
    return False


if __name__ == "__main__":
    result = asyncio.run(test_agent_with_jwt())
    print(f"\nFinal Result: {'SUCCESS' if result else 'FAILED'}")
