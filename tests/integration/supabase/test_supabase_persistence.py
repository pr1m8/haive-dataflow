#!/usr/bin/env python3
"""Test Supabase persistence with a simple agent."""

import asyncio
import json

import websockets


async def test_supabase_persistence():
    """Test that agent conversations are saved to Supabase."""
    # Test message that will be sent to the agent
    test_message = "Hello from Supabase persistence test!"

    try:
        # Connect to WebSocket API
        uri = "ws://localhost:8000/api/ws/chat/CheckersAgent?token=test"

        async with websockets.connect(uri) as websocket:

            # Send test message
            message = {"messages": [{"role": "user", "content": test_message}]}

            await websocket.send(json.dumps(message))

            # Collect all responses
            responses = []

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    responses.append(data)

                    if (
                        data.get("type") == "status"
                        and data.get("content") == "complete"
                    ):
                        break
                    if data.get("type") == "error":
                        break

                except TimeoutError:
                    break

            # Show summary
            for _i, _resp in enumerate(responses):
                pass

            return True

    except Exception:
        return False


async def check_supabase_data():
    """Check if data was saved to Supabase by connecting directly."""
    try:
        import os

        import asyncpg

        # Get Supabase connection string
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
            "SUPABASE_DATABASE_URI"
        )

        if not supabase_uri:
            return False

        # Connect to Supabase
        conn = await asyncpg.connect(supabase_uri)

        # Check agent_state schema
        schemas = await conn.fetch(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'agent_state'"
        )
        if schemas:
            pass
        else:
            await conn.close()
            return False

        # Check tables in agent_state schema
        tables = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'agent_state'
            ORDER BY table_name
        """
        )

        for table in tables:
            table_name = table["table_name"]

            # Count rows
            await conn.fetchval(f"SELECT COUNT(*) FROM agent_state.{table_name}")

        # Check recent checkpoints
        recent_checkpoints = await conn.fetch(
            """
            SELECT thread_id, checkpoint_id, created_at
            FROM agent_state.checkpoints
            ORDER BY created_at DESC
            LIMIT 5
        """
        )

        if recent_checkpoints:
            for _cp in recent_checkpoints:
                pass
        else:
            pass

        # Check recent threads
        recent_threads = await conn.fetch(
            """
            SELECT thread_id, user_id, created_at, agent_name
            FROM agent_state.threads
            ORDER BY created_at DESC
            LIMIT 5
        """
        )

        if recent_threads:
            for _thread in recent_threads:
                pass
        else:
            pass

        await conn.close()
        return True

    except Exception:
        return False


async def main():
    """Run the complete Supabase persistence test."""
    # Test 1: Send message via WebSocket
    websocket_success = await test_supabase_persistence()

    if websocket_success:
        # Test 2: Check if data was saved
        await asyncio.sleep(2)  # Give time for data to be written
        database_success = await check_supabase_data()

        if database_success:
            pass
        else:
            pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
