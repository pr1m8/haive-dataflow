"""Test WebSocket connection with SimpleAgent to see actual schema behavior."""

import asyncio
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

    print("Testing SimpleAgent WebSocket connection...")

    # Test 1: SimpleAgent without tools
    print("\n1. Testing SimpleAgent WITHOUT tools:")
    agent1 = SimpleAgent(
        name="simple_no_tools",
        engine=AugLLMConfig(
            model="gpt-3.5-turbo",
            prompt_template="You are a helpful assistant. Answer: {messages}",
        ),
    )

    # Check schema
    print(f"Input schema fields: {list(agent1.input_schema.model_fields.keys())}")
    print(f"State schema fields: {list(agent1.state_schema.model_fields.keys())}")
    print(f"State schema base: {agent1.state_schema.__bases__}")

    # Test 2: SimpleAgent with tools
    print("\n2. Testing SimpleAgent WITH tools:")
    agent2 = SimpleAgent(
        name="simple_with_tools",
        engine=AugLLMConfig(
            model="gpt-3.5-turbo",
            prompt_template="You are a helpful assistant. Answer: {messages}",
            tools=[create_tool()],
        ),
    )

    # Check schema
    print(f"Input schema fields: {list(agent2.input_schema.model_fields.keys())}")
    print(f"State schema fields: {list(agent2.state_schema.model_fields.keys())}")
    print(f"State schema base: {agent2.state_schema.__bases__}")

    # Test WebSocket connection
    print("\n3. Testing actual WebSocket connection:")
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

            print(f"\nSending message: {message}")
            await websocket.send(json.dumps(message))

            # Receive responses
            print("\nReceiving responses:")
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    print(f"Response type: {data.get('type')}")

                    if data.get("type") == "response":
                        print(f"Content: {data.get('content')}")
                    elif data.get("type") == "error":
                        print(f"Error: {data.get('content')}")
                        break
                    elif (
                        data.get("type") == "status"
                        and data.get("content") == "complete"
                    ):
                        break

                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break

    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        print("Make sure haive-dataflow is running on port 8000")

    # Test 4: Check minimal input requirements
    print("\n4. Testing minimal input requirements:")

    # Test with minimal input
    minimal_input = {"messages": [{"role": "user", "content": "Hello"}]}
    try:
        result = agent2.invoke(minimal_input)
        print("✓ Minimal input works even with tools!")
        print(f"Result keys: {list(result.keys())}")
    except Exception as e:
        print(f"✗ Minimal input failed: {e}")

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
    try:
        result = agent2.invoke(full_input)
        print("✓ Full ToolState input also works")
    except Exception as e:
        print(f"✗ Full input failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple_agent_websocket())
