#!/usr/bin/env python3
"""Test script to verify API endpoints are working."""

import asyncio
import json
import signal
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
                    except:
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
                except:
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
    print("🧪 Testing Haive DataFlow API Endpoints")
    print("=" * 50)

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
            print(f"Testing {endpoint}...", end=" ")
            result = await test_endpoint(session, endpoint)
            results.append(result)

            if result["success"]:
                print("✅ SUCCESS")
            else:
                print(f"❌ FAILED ({result.get('status', 'ERROR')})")
                if "error" in result:
                    print(f"   Error: {result['error']}")

        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)

        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        print(f"Successful endpoints: {success_count}/{total_count}")
        print(f"Success rate: {success_count/total_count*100:.1f}%")

        print("\n📋 DETAILED RESULTS:")
        for result in results:
            print(f"\n{result['endpoint']}:")
            print(f"  Status: {result['status']}")
            print(f"  Success: {result['success']}")
            if "sample_data" in result:
                print(f"  Sample: {result['sample_data']}")
            if "error" in result:
                print(f"  Error: {result['error']}")

        return success_count, total_count


def start_api_server():
    """Start the API server in background."""
    print("🚀 Starting API server...")

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
    print("⏳ Waiting for server to start...")
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
                        print("✅ Server is running!")
                    else:
                        print(f"⚠️ Server responded with status {response.status}")
            except Exception as e:
                print(f"❌ Server is not responding: {e}")
                return

        # Run endpoint tests
        success_count, total_count = await test_api_endpoints()

        # Test a simple game creation (if games API is available)
        print("\n🎮 Testing Game API...")
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
                print("✅ Game creation endpoint works!")
            else:
                print(
                    f"❌ Game creation failed: {result.get('error', 'Unknown error')}"
                )

        print(f"\n🎯 FINAL RESULT: {success_count}/{total_count} endpoints working")

        if success_count >= total_count * 0.8:  # 80% success rate
            print("🎉 API is working well!")
            return True
        else:
            print("⚠️ Some API endpoints have issues")
            return False

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False
    finally:
        # Clean up server process
        if server_process:
            print("\n🧹 Stopping API server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Server stopped")


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        sys.exit(1)
