#!/usr/bin/env python3
"""Simple test to confirm agent streaming works and data appears in Supabase."""

import asyncio
import json
import os
import sys
import uuid

import websockets

# Add paths for imports
sys.path.insert(0, "packages/haive-dataflow/src")
sys.path.insert(0, "packages/haive-core/src")


async def test_simple_agent():
    """Test agent streaming and confirm data appears in Supabase."""

    print("🚀 Testing simple agent streaming...")

    # Generate a unique thread ID for this test
    thread_id = str(uuid.uuid4())
    print(f"Using thread ID: {thread_id}")

    # WebSocket URL (assuming your server is running on port 8000)
    ws_url = "ws://localhost:8000/api/agent/ws"

    try:
        # Connect to WebSocket
        print("📡 Connecting to WebSocket...")
        async with websockets.connect(ws_url) as websocket:
            print("✓ Connected to WebSocket")

            # Send a simple message
            message = {
                "agent_name": "SimpleAgent",
                "message": "Hello, this is a test message",
                "config": {"stream_mode": "messages", "thread_id": thread_id},
            }

            print("📤 Sending message to agent...")
            await websocket.send(json.dumps(message))

            # Listen for responses
            response_count = 0
            while response_count < 5:  # Limit to 5 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    print(f"📨 Response {response_count + 1}: {data}")
                    response_count += 1

                    # If we get an error or completion, break
                    if data.get("type") in ["error", "complete"]:
                        break

                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    break

        print("✓ WebSocket test completed")

        # Now check if data appeared in Supabase
        print("\n🔍 Checking Supabase for data...")
        await check_supabase_data(thread_id)

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("Make sure the haive-dataflow server is running on port 8000")
        return False

    return True


async def check_supabase_data(thread_id):
    """Check if the thread data appeared in Supabase."""
    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        persistence = SupabasePersistence()
        print(f"Checking for thread: {thread_id}")

        # Try to get thread info
        thread_info = await persistence.get_thread_info(thread_id, "test-user")
        if thread_info:
            print(f"✓ Found thread in Supabase: {thread_info}")
        else:
            print("❌ Thread not found in Supabase")

        # Try to get state
        state = await persistence.get_state(thread_id, "test-user")
        if state:
            print(f"✓ Found state in Supabase: {state}")
        else:
            print("❌ State not found in Supabase")

    except Exception as e:
        print(f"❌ Error checking Supabase: {e}")


if __name__ == "__main__":
    # Check if server is running first
    print("🔧 Starting agent streaming test...")
    success = asyncio.run(test_simple_agent())

    if success:
        print("\n🎉 Test completed successfully!")
        print("If data appeared in Supabase, the migration is working correctly.")
    else:
        print("\n❌ Test failed.")
        print("Please start the haive-dataflow server and try again.")
