"""Test WebSocket API directly with curl commands."""

import contextlib
import json
import subprocess


def test_websocket_with_curl():
    """Test WebSocket connection using curl."""
    # Test 1: Get available agents
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/agents"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        with contextlib.suppress(Exception):
            json.loads(result.stdout)
    else:
        pass

    # Test 2: Test WebSocket with wscat or websocat

    # Test 3: Test with curl WebSocket upgrade
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
        check=False,
    )

    # Test 4: Check agent config endpoint
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/agents/simple/config"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        with contextlib.suppress(Exception):
            json.loads(result.stdout)


def test_websocket_with_python():
    """Test WebSocket using Python websocket-client."""


if __name__ == "__main__":
    test_websocket_with_curl()
    test_websocket_with_python()
