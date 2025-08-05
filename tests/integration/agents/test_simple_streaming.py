#!/usr/bin/env python3
"""Simple test for agent streaming."""

import asyncio
import json
import sys

import websockets

BASE_URL = "ws://192.168.2.13:8000"


async def test_simple_agent():
    """Test with a simple agent name that should exist."""
    token = sys.argv[1] if len(sys.argv) > 1 else "test"

    # Try different agent names
    agent_names = ["simple", "chat", "base", "test", "agent"]

    for agent_name in agent_names:
        try:
            # Simple config
            config = {
                "agent_name": agent_name,
                "provider": "azure",
                "model": "gpt-4o",
                "stream": True,
                "persistent": False,
            }

            uri = f"{BASE_URL}/api/ws/chat/{agent_name}?token={token}&config={json.dumps(config)}"

            async with websockets.connect(uri, timeout=10) as websocket:
                # Wait for welcome
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5)
                json.loads(welcome)

                # Send simple message
                message = {"type": "message", "content": "Hello!"}
                await websocket.send(json.dumps(message))

                # Get response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                json.loads(response)

                return True

        except Exception:
            pass

    return False


if __name__ == "__main__":
    result = asyncio.run(test_simple_agent())
