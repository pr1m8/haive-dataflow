#!/usr/bin/env python3
"""Test WebSocket streaming with Haive agents"""

import asyncio
import json
import sys

import websockets

# Configuration
BASE_URL = "ws://192.168.2.13:8000"
AGENT_NAME = "TextAnalyzer"  # Change this to your agent name


async def test_agent_streaming(token):
    """Test agent WebSocket streaming"""

    # Connect to WebSocket
    uri = f"{BASE_URL}/api/ws/chat/{AGENT_NAME}?token={token}"

    # Chat configuration
    config = {
        "agent_name": AGENT_NAME,
        "provider": "azure",
        "model": "gpt-4o",
        "stream": True,  # Enable streaming
        "persistent": False,
    }

    # Add config to URL
    uri += f"&config={json.dumps(config)}"

    print(f"Connecting to {uri}")

    async with websockets.connect(uri) as websocket:
        # Wait for welcome message
        welcome = json.loads(await websocket.recv())
        print(f"Connected: {welcome}")

        # Send a test message
        message = {
            "type": "message",
            "content": "Tell me a short story about AI in 3 sentences, streaming each sentence separately.",
        }

        print(f"\nSending: {message['content']}")
        await websocket.send(json.dumps(message))

        # Receive streaming responses
        print("\nStreaming response:")
        stream_complete = False

        while not stream_complete:
            response = json.loads(await websocket.recv())

            if response["type"] == "status":
                if response["content"]["status"] == "streaming":
                    print("--- Stream started ---")
                elif response["content"]["status"] == "complete":
                    print("--- Stream complete ---")
                    stream_complete = True
            elif response["type"] == "response":
                # Print streamed content
                print(f"[{response.get('stream_index', 0)}] {response['content']}")
            else:
                print(f"Received: {response}")


async def test_agent_non_streaming(token):
    """Test agent WebSocket without streaming"""

    # Connect to WebSocket
    uri = f"{BASE_URL}/api/ws/chat/{AGENT_NAME}?token={token}"

    # Chat configuration
    config = {
        "agent_name": AGENT_NAME,
        "provider": "azure",
        "model": "gpt-4o",
        "stream": False,  # Disable streaming
        "persistent": False,
    }

    # Add config to URL
    uri += f"&config={json.dumps(config)}"

    print("\n\nTesting non-streaming mode...")
    print(f"Connecting to {uri}")

    async with websockets.connect(uri) as websocket:
        # Wait for welcome message
        welcome = json.loads(await websocket.recv())
        print(f"Connected: {welcome}")

        # Send a test message
        message = {"type": "message", "content": "What is 2+2?"}

        print(f"\nSending: {message['content']}")
        await websocket.send(json.dumps(message))

        # Receive response
        response = json.loads(await websocket.recv())
        print(f"Response: {response['content']}")


async def main():
    """Main test function"""
    # Get token from command line or use test token
    token = sys.argv[1] if len(sys.argv) > 1 else "test"

    print("=== Haive Agent Streaming Test ===")
    print(f"Using token: {token[:10]}...")

    try:
        # Test streaming mode
        await test_agent_streaming(token)

        # Test non-streaming mode
        await test_agent_non_streaming(token)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
