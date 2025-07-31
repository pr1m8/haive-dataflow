"""Test WebSocket connection with SimpleAgent to see actual schema behavior."""

import asyncio
import contextlib
import json

import websockets
from haive.agents.simple.agent import SimpleAgent
from haive.core.llm.aug_llm_config import AugLLMConfig


def create_tool():
    """Create a simple tool for testing."""

    def get_weather(location: str) -> str:
        """Get weather for a location."""
        return f"The weather in {location} is sunny and 72°F"

    return get_weather


async def test_simple_agent_websocket():
    """Test SimpleAgent via WebSocket API."""
    # Test 1: SimpleAgent without tools
    SimpleAgent(
        name="simple_no_tools",
        engine=AugLLMConfig(
            model="gpt-3.5-turbo",
            prompt_template="You are a helpful assistant. Answer: {messages}",
        ),
    )

    # Check schema

    # Test 2: SimpleAgent with tools
    agent2 = SimpleAgent(
        name="simple_with_tools",
        engine=AugLLMConfig(
            model="gpt-3.5-turbo",
            prompt_template="You are a helpful assistant. Answer: {messages}",
            tools=[create_tool()],
        ),
    )

    # Check schema

    # Test WebSocket connection
    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/api/ws/chat/simple_with_tools?token=test"

        async with websockets.connect(uri) as websocket:
            # Send a simple message
            message = {
                "messages": [
                    {"role": "user", "content": "What's the weather in Paris?"}
                ]
            }

            await websocket.send(json.dumps(message))

            # Receive responses
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)

                    if data.get("type") == "response":
                        pass
                    elif data.get("type") == "error" or (
                        data.get("type") == "status"
                        and data.get("content") == "complete"
                    ):
                        break

                except TimeoutError:
                    break

    except Exception:
        pass

    # Test 4: Check minimal input requirements

    # Test with minimal input
    minimal_input = {"messages": [{"role": "user", "content": "Hello"}]}
    with contextlib.suppress(Exception):
        agent2.invoke(minimal_input)

    # Test with full ToolState input
    full_input = {
        "messages": [{"role": "user", "content": "Hello"}],
        "tools": [],
        "tool_routes": {},
        "name_attrs": ["name"],
        "content": None,
        "output_schemas": {},
        "engine_route_config": {},
    }
    with contextlib.suppress(Exception):
        agent2.invoke(full_input)


if __name__ == "__main__":
    asyncio.run(test_simple_agent_websocket())
