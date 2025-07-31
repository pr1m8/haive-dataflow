#!/usr/bin/env python3
"""API debugging script to test agent and LLM endpoints."""

import contextlib
import sys

import requests

# Base URL - adjust as needed
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    with contextlib.suppress(Exception):
        requests.get(f"{BASE_URL}/api/health")


def test_llm_generate(token=None):
    """Test LLM generate endpoint."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Test data
    data = {
        "provider": "azure",
        "model": "gpt-4o",
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant.",
    }

    # Test with query parameter
    params = {"query": "Hello, how are you?"}

    with contextlib.suppress(Exception):
        requests.post(
            f"{BASE_URL}/api/llm/generate", json=data, params=params, headers=headers
        )


def test_routes_discovery():
    """Try to discover available routes."""
    # Common endpoints to test
    endpoints = [
        "/api/health",
        "/api/llm/generate",
        "/api/ws/chat/test",
        "/api/conversations/",
        "/docs",
        "/openapi.json",
    ]

    for endpoint in endpoints:
        with contextlib.suppress(Exception):
            requests.get(f"{BASE_URL}{endpoint}")


def main():
    """Main function."""
    # Get token from command line if provided
    token = sys.argv[1] if len(sys.argv) > 1 else None
    if token:
        pass

    # Run tests
    test_health()
    test_routes_discovery()
    test_llm_generate(token)


if __name__ == "__main__":
    main()
