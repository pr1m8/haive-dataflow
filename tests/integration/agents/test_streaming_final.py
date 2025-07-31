#!/usr/bin/env python3
"""Final test for enhanced streaming functionality."""

import asyncio
import json
import sys
import traceback

import websockets

BASE_URL = "ws://192.168.2.13:8000"


async def test_enhanced_streaming():
    """Test the enhanced streaming functionality."""
    token = sys.argv[1] if len(sys.argv) > 1 else "test"

    # Test different streaming configurations
    test_configs = [
        {
            "name": "Basic Text Streaming",
            "config": {
                "agent_name": "simple",
                "provider": "azure",
                "model": "gpt-4o",
                "stream": True,
                "stream_mode": "messages",
                "stream_format": "text",
                "persistent": False,
            },
        },
        {
            "name": "JSON Streaming",
            "config": {
                "agent_name": "simple",
                "provider": "azure",
                "model": "gpt-4o",
                "stream": True,
                "stream_mode": "values",
                "stream_format": "json",
                "persistent": False,
            },
        },
        {
            "name": "Structured Streaming",
            "config": {
                "agent_name": "simple",
                "provider": "azure",
                "model": "gpt-4o",
                "stream": True,
                "stream_mode": "updates",
                "stream_format": "structured",
                "progressive_updates": True,
                "persistent": False,
            },
        },
    ]

    for test_case in test_configs:

        try:
            config = test_case["config"]
            agent_name = config["agent_name"]

            # Build WebSocket URL
            uri = f"{BASE_URL}/api/ws/chat/{agent_name}?token={token}&config={json.dumps(config)}"

            # Connect with simpler syntax
            websocket = await websockets.connect(uri)

            try:
                # Wait for welcome message
                welcome_raw = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome = json.loads(welcome_raw)

                if (
                    welcome.get("type") == "status"
                    and welcome.get("content", {}).get("status") == "connected"
                ):

                    # Send test message
                    test_message = {
                        "type": "message",
                        "content": "Analyze this text: 'The weather is beautiful today!' Extract sentiment and key phrases.",
                    }

                    await websocket.send(json.dumps(test_message))

                    # Collect streaming responses
                    responses = []
                    stream_complete = False
                    timeout_count = 0

                    while not stream_complete and timeout_count < 3:
                        try:
                            response_raw = await asyncio.wait_for(
                                websocket.recv(), timeout=10.0
                            )
                            response = json.loads(response_raw)
                            responses.append(response)

                            if response.get("type") == "status":
                                status = response.get("content", {}).get("status")
                                if status == "complete":
                                    stream_complete = True
                                elif status == "streaming":
                                    pass
                            elif response.get("type") == "response":
                                content = response.get("content")
                                if isinstance(content, str):
                                    pass
                                else:
                                    pass

                        except TimeoutError:
                            timeout_count += 1
                            if timeout_count >= 3:
                                break

                    # Show summary
                    [r.get("type", "unknown") for r in responses]

                else:
                    pass

            finally:
                await websocket.close()

        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enhanced_streaming())
