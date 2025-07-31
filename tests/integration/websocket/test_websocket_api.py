"""Test WebSocket API directly with curl commands."""

import json
import subprocess


def test_websocket_with_curl():
    """Test WebSocket connection using curl."""

    print("Testing WebSocket API with SimpleAgent...")

    # Test 1: Get available agents
    print("\n1. Getting available agents:")
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/agents"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        try:
            agents = json.loads(result.stdout)
            print(f"Available agents: {json.dumps(agents, indent=2)}")
        except:
            print(f"Response: {result.stdout}")
    else:
        print(f"Error: {result.stderr}")

    # Test 2: Test WebSocket with wscat or websocat
    print("\n2. Testing WebSocket connection:")
    print("Run this command in another terminal:")
    print("wscat -c 'ws://localhost:8000/api/ws/chat/simple?token=test'")
    print("\nThen send this message:")
    print('{"messages": [{"role": "user", "content": "Hello"}]}')

    # Test 3: Test with curl WebSocket upgrade
    print("\n3. Testing with curl (HTTP request to check endpoint):")
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "GET",
            "http://localhost:8000/api/ws/chat/simple?token=test",
            "-H",
            "Connection: Upgrade",
            "-H",
            "Upgrade: websocket",
        ],
        capture_output=True,
        text=True,
    )
    print(f"Response: {result.stdout}")

    # Test 4: Check agent config endpoint
    print("\n4. Checking agent config:")
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/agents/simple/config"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        try:
            config = json.loads(result.stdout)
            print(f"Agent config: {json.dumps(config, indent=2)}")
        except:
            print(f"Response: {result.stdout}")


def test_websocket_with_python():
    """Test WebSocket using Python websocket-client."""

    print("\n5. Testing with Python websocket-client:")
    print("Run this Python code:")
    print(
        """
import websocket
import json

ws = websocket.WebSocket()
ws.connect("ws://localhost:8000/api/ws/chat/simple?token=test")

# Send message
message = {"messages": [{"role": "user", "content": "Hello"}]}
ws.send(json.dumps(message))

# Receive responses
while True:
    result = ws.recv()
    data = json.loads(result)
    print(f"Received: {data}")
    if data.get('type') == 'status' and data.get('content') == 'complete':
        break

ws.close()
"""
    )


if __name__ == "__main__":
    print("Make sure haive-dataflow is running on port 8000")
    print(
        "Run: cd packages/haive-dataflow && poetry run python -m haive.dataflow.api.main"
    )
    print("-" * 60)

    test_websocket_with_curl()
    test_websocket_with_python()
