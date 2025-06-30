#!/usr/bin/env python3
"""Test enhanced streaming modes with Haive agents"""

import asyncio
import json
import sys

import websockets

# Configuration
BASE_URL = "ws://192.168.2.13:8000"
AGENT_NAME = "TextAnalyzer"  # Change to your agent name


async def test_streaming_mode(token, mode, format_type="auto"):
    """Test a specific streaming mode"""

    print(f"\n{'='*50}")
    print(f"Testing stream_mode='{mode}', stream_format='{format_type}'")
    print(f"{'='*50}")

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

    print(f"Connecting to {AGENT_NAME} with mode={mode}, format={format_type}")

    async with websockets.connect(uri) as websocket:
        # Wait for welcome message
        welcome = json.loads(await websocket.recv())
        print(f"Connected: Thread {welcome['content']['thread_id']}")

        # Send a test message
        message = {
            "type": "message",
            "content": "Analyze this text: 'Artificial intelligence is transforming how we work.' Extract entities and sentiment.",
        }

        print(f"\nSending: {message['content'][:50]}...")
        await websocket.send(json.dumps(message))

        # Receive streaming responses
        print("\nStreaming responses:")
        stream_complete = False
        chunk_count = 0

        while not stream_complete:
            response = json.loads(await websocket.recv())

            if response["type"] == "status":
                if response["content"]["status"] == "streaming":
                    print(
                        f"--- Stream started (mode: {response['content'].get('mode', 'unknown')}) ---"
                    )
                elif response["content"]["status"] == "complete":
                    print(f"--- Stream complete ({chunk_count} chunks) ---")
                    stream_complete = True
            elif response["type"] == "response":
                chunk_count += 1
                # Display based on format
                if format_type == "json" or format_type == "structured":
                    print(
                        f"Chunk {chunk_count}: {json.dumps(response['content'], indent=2)[:200]}..."
                    )
                else:
                    print(f"Chunk {chunk_count}: {str(response['content'])[:100]}...")
            else:
                print(
                    f"Other: {response['type']} - {str(response.get('content', ''))[:100]}"
                )


async def test_all_modes(token):
    """Test different streaming mode combinations"""

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
        except Exception as e:
            print(f"Error testing {mode}/{format_type}: {e}")


async def test_progressive_updates(token):
    """Test progressive schema updates"""

    print(f"\n{'='*50}")
    print("Testing Progressive Updates")
    print(f"{'='*50}")

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
        welcome = json.loads(await websocket.recv())
        print(f"Connected for progressive updates")

        message = {
            "type": "message",
            "content": "Analyze sentiment and extract key phrases from: 'The new AI system works brilliantly and exceeds all expectations.'",
        }

        await websocket.send(json.dumps(message))

        print("\nProgressive updates:")
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
                    print(f"Update - Type: {content.get('type', 'unknown')}")
                    print(
                        f"  Data keys: {list(content['data'].keys()) if isinstance(content['data'], dict) else 'N/A'}"
                    )


async def main():
    """Main test function"""
    # Get token from command line or use test token
    token = sys.argv[1] if len(sys.argv) > 1 else "test"

    print("=== Enhanced Haive Agent Streaming Test ===")
    print(f"Using token: {token[:10]}...")

    try:
        # Test all streaming modes
        await test_all_modes(token)

        # Test progressive updates
        await test_progressive_updates(token)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
