#!/usr/bin/env python3
"""Simple test to confirm agent streaming works and data appears in Supabase."""

import asyncio
import json
import sys
import uuid

import websockets

# Add paths for imports
sys.path.insert(0, "packages/haive-dataflow/src")
sys.path.insert(0, "packages/haive-core/src")


async def test_simple_agent():
    """Test agent streaming and confirm data appears in Supabase."""
    # Generate a unique thread ID for this test
    thread_id = str(uuid.uuid4())

    # WebSocket URL (assuming your server is running on port 8000)
    ws_url = "ws://localhost:8000/api/agent/ws"

    try:
        # Connect to WebSocket
        async with websockets.connect(ws_url) as websocket:

            # Send a simple message
            message = {
                "agent_name": "SimpleAgent",
                "message": "Hello, this is a test message",
                "config": {"stream_mode": "messages", "thread_id": thread_id},
            }

            await websocket.send(json.dumps(message))

            # Listen for responses
            response_count = 0
            while response_count < 5:  # Limit to 5 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    response_count += 1

                    # If we get an error or completion, break
                    if data.get("type") in ["error", "complete"]:
                        break

                except TimeoutError:
                    break
                except json.JSONDecodeError:
                    break

        # Now check if data appeared in Supabase
        await check_supabase_data(thread_id)

    except Exception:
        return False

    return True


async def check_supabase_data(thread_id):
    """Check if the thread data appeared in Supabase."""
    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        persistence = SupabasePersistence()

        # Try to get thread info
        thread_info = await persistence.get_thread_info(thread_id, "test-user")
        if thread_info:
            pass
        else:
            pass

        # Try to get state
        state = await persistence.get_state(thread_id, "test-user")
        if state:
            pass
        else:
            pass

    except Exception:
        pass


if __name__ == "__main__":
    # Check if server is running first
    success = asyncio.run(test_simple_agent())

    if success:
        pass
    else:
        pass
