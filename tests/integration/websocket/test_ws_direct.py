"""Direct WebSocket test for haive-dataflow API."""

import asyncio
import json

import websockets


async def test_websocket():
    """Test WebSocket connection directly."""

    # Try different agent names
    agent_names = ["simple", "simple_agent", "SimpleAgent", "test"]

    for agent_name in agent_names:
        print(f"\nTrying agent: {agent_name}")

        # Try with test token
        uri = f"ws://localhost:8000/api/ws/chat/{agent_name}?token=test-token"

        try:
            async with websockets.connect(uri) as ws:
                print(f"✓ Connected to {agent_name}!")

                # Send test message
                message = {"messages": [{"role": "user", "content": "Hello"}]}
                await ws.send(json.dumps(message))

                # Receive response
                response = await ws.recv()
                data = json.loads(response)
                print(f"Response: {data}")

                break  # Success

        except Exception as e:
            print(f"✗ Failed: {e}")

    # Also try the reset endpoint
    print("\nChecking reset endpoint:")
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/ws/chat/thread/test-thread/reset",
            headers={"Authorization": "Bearer test-token"},
        )
        print(f"Reset endpoint status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
