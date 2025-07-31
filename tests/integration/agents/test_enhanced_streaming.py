#!/usr/bin/env python3
"""Test enhanced streaming modes with Haive agents."""

import asyncio
import json
import sys

import websockets

# Configuration
BASE_URL = "ws://192.168.2.13:8000"
AGENT_NAME = "TextAnalyzer"  # Change to your agent name


async def test_streaming_mode(token, mode, format_type="auto"):
    """Test a specific streaming mode."""
    # Connect to WebSocket
    uri = f"{BASE_URL}/api/ws/chat/{AGENT_NAME}?token={token}"

    # Chat configuration with enhanced options
    config = {
        "agent_name": AGENT_NAME,
        "provider": "azure",
        "model": "gpt-4o",
        "stream": True,
        "stream_mode": mode,
        "stream_format": format_type,
        "persistent": False,
    }

    # Add config to URL
    uri += f"&config={json.dumps(config)}"

    async with websockets.connect(uri) as websocket:
        # Wait for welcome message
        json.loads(await websocket.recv())

        # Send a test message
        message = {
            "type": "message",
            "content": "Analyze this text: 'Artificial intelligence is transforming how we work.' Extract entities and sentiment.",
        }

        await websocket.send(json.dumps(message))

        # Receive streaming responses
        stream_complete = False
        chunk_count = 0

        while not stream_complete:
            response = json.loads(await websocket.recv())

            if response["type"] == "status":
                if response["content"]["status"] == "streaming":
                    pass
                elif response["content"]["status"] == "complete":
                    stream_complete = True
            elif response["type"] == "response":
                chunk_count += 1
                # Display based on format
                if format_type in {"json", "structured"}:
                    pass
                else:
                    pass
            else:
                pass


async def test_all_modes(token):
    """Test different streaming mode combinations."""
    # Test different mode/format combinations
    test_cases = [
        ("messages", "text"),  # Chat-like text streaming
        ("messages", "json"),  # Full message objects
        ("values", "auto"),  # State values streaming
        ("updates", "structured"),  # Structured updates with type info
        ("debug", "json"),  # Debug information
    ]

    for mode, format_type in test_cases:
        try:
            await test_streaming_mode(token, mode, format_type)
            await asyncio.sleep(1)  # Small delay between tests
        except Exception:
            pass


async def test_progressive_updates(token):
    """Test progressive schema updates."""
    uri = f"{BASE_URL}/api/ws/chat/{AGENT_NAME}?token={token}"

    config = {
        "agent_name": AGENT_NAME,
        "provider": "azure",
        "model": "gpt-4o",
        "stream": True,
        "stream_mode": "values",
        "stream_format": "structured",
        "progressive_updates": True,
        "persistent": False,
    }

    uri += f"&config={json.dumps(config)}"

    async with websockets.connect(uri) as websocket:
        json.loads(await websocket.recv())

        message = {
            "type": "message",
            "content": "Analyze sentiment and extract key phrases from: 'The new AI system works brilliantly and exceeds all expectations.'",
        }

        await websocket.send(json.dumps(message))

        complete = False

        while not complete:
            response = json.loads(await websocket.recv())

            if (
                response["type"] == "status"
                and response["content"]["status"] == "complete"
            ):
                complete = True
            elif response["type"] == "response":
                content = response["content"]
                if isinstance(content, dict) and "data" in content:
                    pass


async def main():
    """Main test function."""
    # Get token from command line or use test token
    token = sys.argv[1] if len(sys.argv) > 1 else "test"

    try:
        # Test all streaming modes
        await test_all_modes(token)

        # Test progressive updates
        await test_progressive_updates(token)

    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
