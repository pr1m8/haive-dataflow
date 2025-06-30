#!/usr/bin/env python3
"""Debug WebSocket connection issues"""

import asyncio
import json
import sys

import websockets


async def debug_websocket():
    """Debug the WebSocket connection"""

    token = sys.argv[1] if len(sys.argv) > 1 else "test"
    base_url = "ws://192.168.2.13:8000"

    # Try the simplest possible connection
    agent_name = "test"  # Use any name

    # Minimal config
    config = {"agent_name": agent_name, "provider": "azure", "model": "gpt-4o"}

    uri = (
        f"{base_url}/api/ws/chat/{agent_name}?token={token}&config={json.dumps(config)}"
    )
    print(f"Testing URL: {uri[:100]}...")

    try:
        print("Attempting connection...")
        websocket = await websockets.connect(uri)
        print("✓ WebSocket connected!")

        # Wait for any response
        response = await websocket.recv()
        print(f"✓ Received: {response}")

        await websocket.close()
        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")

        # Try without config
        simple_uri = f"{base_url}/api/ws/chat/{agent_name}?token={token}"
        print(f"Trying simpler URL: {simple_uri}")

        try:
            websocket = await websockets.connect(simple_uri)
            print("✓ Simple connection worked!")
            response = await websocket.recv()
            print(f"✓ Response: {response}")
            await websocket.close()
            return True
        except Exception as e2:
            print(f"✗ Simple connection also failed: {e2}")
            return False


if __name__ == "__main__":
    result = asyncio.run(debug_websocket())
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
