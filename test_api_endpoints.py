"""Test Api Endpoints - Utility functions for test api endpoints.

TODO: Add comprehensive description of test api endpoints functionality.

This module provides utility functions for the Haive AI Agent Framework.

Key Components:
    - start_api_server(): Start Api Server function

Example:
    Basic usage::

        from packages.haive-dataflow import None

        # Create instance
        instance = None(name='example')

        # Use the utility functions
        result = instance.start_api_server('input_data')

        print(f"Result: {result}")

Advanced Usage:
    TODO: Add advanced utility functions example

See Also:
    TODO: List related modules

Notes:
    TODO: Add implementation notes and caveats
"""

#!/usr/bin/env python3
"""Test script to verify API endpoints are working."""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import aiohttp

API_BASE = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds


async def test_endpoint(session, endpoint, method="GET", data=None):
    """Test a single API endpoint."""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            async with session.get(url, timeout=10) as response:
                result = {
                    "endpoint": endpoint,
                    "status": response.status,
                    "success": 200 <= response.status < 300,
                }
                if result["success"]:
                    try:
                        content = await response.json()
                        result["content_type"] = "json"
                        result["sample_data"] = (
                            str(content)[:200] + "..."
                            if len(str(content)) > 200
                            else str(content)
                        )
                    except Exception:
                        content = await response.text()
                        result["content_type"] = "text"
                        result["sample_data"] = (
                            content[:200] + "..." if len(content) > 200 else content
                        )
                return result
        elif method == "POST":
            async with session.post(url, json=data, timeout=10) as response:
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status": response.status,
                    "success": 200 <= response.status < 300,
                }
                try:
                    content = await response.json()
                    result["response"] = content
                except Exception:
                    result["response"] = await response.text()
                return result
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": "ERROR",
            "success": False,
            "error": str(e),
        }


async def test_api_endpoints():
    """Test various API endpoints."""
    # List of endpoints to test
    endpoints = [
        "/",
        "/api/health",
        "/docs",
        "/openapi.json",
        "/api/games/list",
        "/api/games/available",
        "/api/agents/discover",
        "/api/tools/list",
        "/api/llm/models",
    ]

    async with aiohttp.ClientSession() as session:
        results = []

        for endpoint in endpoints:
            result = await test_endpoint(session, endpoint)
            results.append(result)

            if result["success"] or "error" in result:
                pass

        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        for result in results:
            if "sample_data" in result:
                pass
            if "error" in result:
                pass

        return success_count, total_count


def start_api_server():
    """Start the API server in background."""
    # Start server
    cmd = [
        "poetry",
        "run",
        "uvicorn",
        "haive.dataflow.api.app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--log-level",
        "warning",  # Reduce noise
    ]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path(__file__).parent
    )

    # Wait a bit for server to start
    time.sleep(8)

    return process


async def main():
    """Main test function."""
    server_process = None

    try:
        # Start API server
        server_process = start_api_server()

        # Test if server is running
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_BASE}/api/health", timeout=5) as response:
                    if response.status == 200:
                        pass
                    else:
                        pass
            except Exception:
                return None

        # Run endpoint tests
        success_count, total_count = await test_api_endpoints()

        # Test a simple game creation (if games API is available)
        async with aiohttp.ClientSession() as session:
            # Test tic-tac-toe creation
            game_data = {
                "game_type": "tic_tac_toe",
                "player_1_model": "gpt-3.5-turbo",
                "player_2_model": "gpt-3.5-turbo",
            }

            result = await test_endpoint(
                session, "/api/games/create", method="POST", data=game_data
            )
            if result["success"]:
                pass
            else:
                pass

        if success_count >= total_count * 0.8:  # 80% success rate
            return True
        return False

    except KeyboardInterrupt:
        return False
    except Exception:
        return False
    finally:
        # Clean up server process
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        sys.exit(1)
