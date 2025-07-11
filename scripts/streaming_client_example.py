#!/usr/bin/env python3
"""
Example client showing different streaming modes usage

This demonstrates how to use the enhanced streaming options
for different use cases with Haive agents.
"""

import asyncio
import json

import websockets


class HaiveStreamingClient:
    """Client for Haive agent streaming with different modes"""

    def __init__(self, base_url="ws://192.168.2.13:8000", token="test"):
        self.base_url = base_url
        self.token = token

    async def chat_stream(self, agent_name, message, **options):
        """Stream a chat conversation with an agent"""

        config = {
            "agent_name": agent_name,
            "provider": options.get("provider", "azure"),
            "model": options.get("model", "gpt-4o"),
            "stream": True,
            "stream_mode": "messages",
            "stream_format": "text",  # Just the text content
            **options,
        }

        uri = f"{self.base_url}/api/ws/chat/{agent_name}?token={self.token}&config={json.dumps(config)}"

        async with websockets.connect(uri) as ws:
            # Wait for connection
            welcome = json.loads(await ws.recv())
            thread_id = welcome["content"]["thread_id"]

            # Send message
            await ws.send(json.dumps({"type": "message", "content": message}))

            # Stream responses
            full_response = ""
            async for chunk in self._stream_chunks(ws):
                if isinstance(chunk, str):
                    full_response += chunk
                    yield chunk

            # Return the full response after streaming
            # Note: Can't use return in async generator, so we'll handle this differently

    async def analyze_stream(self, agent_name, text, include_partial=False):
        """Stream analysis results with structured data"""

        config = {
            "agent_name": agent_name,
            "stream": True,
            "stream_mode": "values",  # Get full state values
            "stream_format": "structured",  # Include type info
            "progressive_updates": include_partial,
        }

        uri = f"{self.base_url}/api/ws/chat/{agent_name}?token={self.token}&config={json.dumps(config)}"

        async with websockets.connect(uri) as ws:
            await ws.recv()  # Welcome

            await ws.send(
                json.dumps({"type": "message", "content": f"Analyze: {text}"})
            )

            results = {}
            async for chunk in self._stream_chunks(ws):
                if isinstance(chunk, dict) and "data" in chunk:
                    # Update results with new data
                    data = chunk["data"]
                    if isinstance(data, dict):
                        results.update(data)
                        yield results.copy()

            # Final results are yielded above; cannot return in async generator

    async def debug_stream(self, agent_name, message):
        """Stream with debug information"""

        config = {
            "agent_name": agent_name,
            "stream": True,
            "stream_mode": "debug",
            "stream_format": "json",
        }

        uri = f"{self.base_url}/api/ws/chat/{agent_name}?token={self.token}&config={json.dumps(config)}"

        async with websockets.connect(uri) as ws:
            await ws.recv()  # Welcome

            await ws.send(json.dumps({"type": "message", "content": message}))

            debug_info = []
            async for chunk in self._stream_chunks(ws):
                debug_info.append(chunk)
                yield chunk

            # Debug info is yielded above; cannot return in async generator

    async def _stream_chunks(self, websocket):
        """Helper to stream chunks from websocket"""

        while True:
            response = json.loads(await websocket.recv())

            if response["type"] == "status":
                if response["content"]["status"] == "complete":
                    break
            elif response["type"] == "response":
                yield response["content"]


# Usage examples
async def example_usage():
    """Show different streaming use cases"""

    client = HaiveStreamingClient()

    # Example 1: Simple chat streaming
    print("=== Chat Streaming ===")
    async for text in client.chat_stream(
        "ChatAgent", "Tell me about Python in 2 sentences"
    ):
        print(text, end="", flush=True)
    print("\n")

    # Example 2: Analysis with structured data
    print("=== Analysis Streaming ===")
    async for analysis in client.analyze_stream(
        "TextAnalyzer",
        "The product is excellent but the service was disappointing.",
        include_partial=True,
    ):
        print(f"Current analysis: {json.dumps(analysis, indent=2)}")
        print("-" * 40)

    # Example 3: Debug information
    print("=== Debug Streaming ===")
    debug_chunks = []
    async for debug in client.debug_stream(
        "DebugAgent", "Process this with debug info"
    ):
        debug_chunks.append(debug)
        print(f"Debug chunk: {json.dumps(debug, indent=2)[:200]}...")


# Different configurations for various use cases
STREAMING_CONFIGS = {
    "chat": {
        "stream_mode": "messages",
        "stream_format": "text",
        "buffer_chunks": False,
    },
    "analysis": {
        "stream_mode": "values",
        "stream_format": "structured",
        "progressive_updates": True,
    },
    "realtime": {
        "stream_mode": "updates",
        "stream_format": "json",
        "buffer_chunks": False,
    },
    "batch": {
        "stream_mode": "values",
        "stream_format": "json",
        "buffer_chunks": True,
        "chunk_size": 5,
    },
    "debug": {
        "stream_mode": "debug",
        "stream_format": "json",
        "include_metadata": True,
    },
}

if __name__ == "__main__":
    asyncio.run(example_usage())
