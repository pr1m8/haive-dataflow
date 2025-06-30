#!/usr/bin/env python3
"""Test with agents that are actually available"""

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


async def test_available_agents():
    """Test with agents that are available according to the logs"""

    token = create_test_jwt()
    if not token:
        print("Failed to create JWT token")
        return False

    print(f"Created JWT token: {token[:30]}...")

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
        print(f"\n--- Testing {agent_name} ---")

        # Simple URL without config
        uri = f"{base_url}/api/ws/chat/{agent_name}?token={urllib.parse.quote(token)}"
        print(f"Testing URL: {uri[:60]}...")

        try:
            print("Attempting connection...")
            websocket = await websockets.connect(uri)
            print("✓ WebSocket connected!")

            # Send a test message
            test_message = {
                "type": "message",
                "content": f"Hello {agent_name}! Please respond to this test message so we can confirm Supabase persistence is working.",
            }

            print(f"Sending: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Wait for response
            print("Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                print(f"✓ Received: {response}")

                # Try to get one more message
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print(f"✓ Received 2: {response2}")
                except asyncio.TimeoutError:
                    print("No second message")

                await websocket.close()
                print(f"✓ {agent_name} test completed successfully!")
                print(
                    "🎉 Agent is working and data should be visible in Supabase database!"
                )
                return True

            except asyncio.TimeoutError:
                print("⏰ Response timeout")
                await websocket.close()

        except Exception as e:
            print(f"✗ {agent_name} connection failed: {e}")
            continue

    print("All tested agents failed")
    return False


if __name__ == "__main__":
    result = asyncio.run(test_available_agents())
    print(f"\nFinal Result: {'SUCCESS' if result else 'FAILED'}")
    if result:
        print("\n🔥 SUCCESS! Check your Supabase database for the conversation data!")
    else:
        print("\n❌ FAILED: No agents responded successfully")
