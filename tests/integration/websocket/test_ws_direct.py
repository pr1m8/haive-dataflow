"""Direct WebSocket test for haive-dataflow API."""

import asyncio
import json

import websockets


async def test_websocket():
    """Test WebSocket connection directly."""
    # Try different agent names
    agent_names = ["simple", "simple_agent", "SimpleAgent", "test"]

    for agent_name in agent_names:

        # Try with test token
        uri = f"ws://localhost:8000/api/ws/chat/{agent_name}?token=test-token"

        try:
            async with websockets.connect(uri) as ws:

                # Send test message
                message = {"messages": [{"role": "user", "content": "Hello"}]}
                await ws.send(json.dumps(message))

                # Receive response
                response = await ws.recv()
                json.loads(response)

                break  # Success

        except Exception:
            pass

    # Also try the reset endpoint
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/ws/chat/thread/test-thread/reset",
            headers={"Authorization": "Bearer test-token"},
        )
        if response.status_code != 200:
            pass


if __name__ == "__main__":
    asyncio.run(test_websocket())
