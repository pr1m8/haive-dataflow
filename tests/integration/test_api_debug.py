#!/usr/bin/env python3
"""API debugging script to test agent and LLM endpoints"""

import sys

import requests

# Base URL - adjust as needed
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


def test_llm_generate(token=None):
    """Test LLM generate endpoint"""
    print("\n=== Testing LLM Generate Endpoint ===")
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

    try:
        response = requests.post(
            f"{BASE_URL}/api/llm/generate", json=data, params=params, headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")


def test_routes_discovery():
    """Try to discover available routes"""
    print("\n=== Testing Route Discovery ===")

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
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")


def main():
    """Main function"""
    print(f"Testing API at {BASE_URL}")

    # Get token from command line if provided
    token = sys.argv[1] if len(sys.argv) > 1 else None
    if token:
        print(f"Using token: {token[:10]}...")

    # Run tests
    test_health()
    test_routes_discovery()
    test_llm_generate(token)


if __name__ == "__main__":
    main()
