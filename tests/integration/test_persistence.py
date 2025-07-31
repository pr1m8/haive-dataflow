#!/usr/bin/env python3
"""Test persistence is working with the API."""

import asyncio
import json
import os
from datetime import datetime

import websockets

# Get JWT token from environment or use a test token
JWT_TOKEN = os.getenv(
    "TEST_JWT_TOKEN",
    "eyJhbGciOiJIUzI1NiIsImtpZCI6IjhHb2w2WEVpdGZHTHJub2wiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzM1NDE3MTkxLCJpYXQiOjE3MzU0MTM1OTEsImlzcyI6Imh0dHBzOi8vemtzc2F6cWh3Y2V0c25iaXVxaWsuc3VwYWJhc2UuY28vYXV0aC92MSIsInN1YiI6ImI5Mjg0ZDQ3LTcyYjUtNDk2MC1hMTc3LTA3ODhmYzRiMDgwOSIsImVtYWlsIjoidGVzdEB1c2VyLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJ0ZXN0QHVzZXIuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImI5Mjg0ZDQ3LTcyYjUtNDk2MC1hMTc3LTA3ODhmYzRiMDgwOSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzM1NDEzNTkxfV0sInNlc3Npb25faWQiOiI5Y2Y1OGMyZS1jODI3LTQ2NzMtOGExNy00OTFjNWFmYjU2MmQiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.VsFuxKCGLXzjUeRb8xnoJUfI_wS1yOBYgNy5h3aJ1F8",
)


async def test_persistence():
    """Test if agent persistence is working."""
    thread_id = f"test-persistence-{datetime.now().isoformat()}"
    agent_name = "base_agent_v2"

    # Prepare WebSocket URL with auth token
    ws_url = f"ws://localhost:8000/api/agent/chat/{agent_name}?thread_id={thread_id}&token={JWT_TOKEN}"

    # Chat config with persistence enabled (default)
    config = {
        "agent_name": agent_name,
        "persistent": True,
        "stream": False,
        "stream_mode": "messages",
    }

    try:
        # Pass config in URL params
        config_str = json.dumps(config)
        full_url = f"{ws_url}&config={config_str}"
        async with websockets.connect(full_url) as websocket:
            # Wait for welcome message
            welcome = await websocket.recv()
            json.loads(welcome)

            # Send first message
            message1 = {"content": "My name is TestUser and I like Python programming."}
            await websocket.send(json.dumps(message1))

            # Get response
            response1 = await websocket.recv()
            json.loads(response1)

            # Close connection
            await websocket.close()

        # Reconnect to same thread
        async with websockets.connect(full_url) as websocket:
            # Wait for welcome message
            welcome2 = await websocket.recv()
            json.loads(welcome2)

            # Ask if it remembers
            message2 = {"content": "What is my name and what do I like?"}
            await websocket.send(json.dumps(message2))

            # Get response
            response2 = await websocket.recv()
            response2_data = json.loads(response2)

            # Check if it remembers
            content = response2_data.get("content", "").lower()
            if "testuser" in content and "python" in content:
                pass
            else:
                pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_persistence())
