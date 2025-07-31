#!/usr/bin/env python3
"""Simple WebSocket test."""

import asyncio

import websockets


async def test():
    # Use development mode bypass
    import os

    os.environ["HAIVE_ENV"] = "development"

    token = "test"  # Development bypass token
    url = f"ws://localhost:8000/api/agent/chat/base_agent_v2?token={token}"
    print(f"Connecting to: {url}")

    try:
        async with websockets.connect(url) as websocket:
            print("Connected!")
            await websocket.close()
    except Exception as e:
        print(f"Error: {e}")


asyncio.run(test())
