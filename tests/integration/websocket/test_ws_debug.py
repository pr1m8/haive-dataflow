#!/usr/bin/env python3
"""Debug WebSocket connection issues."""

import asyncio
import json
import sys

import websockets


async def debug_websocket():
    """Debug the WebSocket connection."""
    token = sys.argv[1] if len(sys.argv) > 1 else "test"
    base_url = "ws://192.168.2.13:8000"

    # Try the simplest possible connection
    agent_name = "test"  # Use any name

    # Minimal config
    config = {"agent_name": agent_name, "provider": "azure", "model": "gpt-4o"}

    uri = (
        f"{base_url}/api/ws/chat/{agent_name}?token={token}&config={json.dumps(config)}"
    )

    try:
        websocket = await websockets.connect(uri)

        # Wait for any response
        await websocket.recv()

        await websocket.close()
        return True

    except Exception:

        # Try without config
        simple_uri = f"{base_url}/api/ws/chat/{agent_name}?token={token}"

        try:
            websocket = await websockets.connect(simple_uri)
            await websocket.recv()
            await websocket.close()
            return True
        except Exception:
            return False


if __name__ == "__main__":
    result = asyncio.run(debug_websocket())
