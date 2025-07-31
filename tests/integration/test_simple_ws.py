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

    try:
        async with websockets.connect(url) as websocket:
            await websocket.close()
    except Exception:
        pass


asyncio.run(test())
