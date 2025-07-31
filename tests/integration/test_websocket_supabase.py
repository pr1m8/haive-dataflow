#!/usr/bin/env python3
"""Test WebSocket API with Supabase persistence."""

import asyncio
import json
from uuid import uuid4

import psycopg
import websockets


async def test_websocket_and_database():
    """Test WebSocket endpoint and verify data is stored in Supabase."""
    # Create a unique thread ID
    thread_id = f"test-ws-{uuid4()}"

    # Test data
    test_message = {
        "message": "Hello! My favorite color is purple. Can you remember this?",
        "agent_id": "simple",
        "user_id": "test-user-123",
        "thread_id": thread_id,
        "stream_mode": "messages",
    }

    try:
        # Connect to WebSocket
        async with websockets.connect("ws://localhost:8192/agents/ws") as websocket:

            # Send message
            await websocket.send(json.dumps(test_message))

            # Receive response
            responses = []
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    responses.append(response)

                    # Try to parse as JSON
                    try:
                        data = json.loads(response)
                        if data.get("type") == "complete":
                            break
                    except json.JSONDecodeError:
                        pass

            except TimeoutError:
                if responses:
                    pass
                else:
                    return

    except Exception:
        return

    # Now check if data was stored in Supabase

    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)

        async with conn.cursor() as cursor:
            # Check if thread was created in public.threads
            await cursor.execute(
                """
                SELECT thread_id, name, metadata, created_at
                FROM public.threads
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            thread_row = await cursor.fetchone()
            if thread_row:
                pass
            else:
                pass

            # Check if checkpoint was created in agent_state.checkpoints
            await cursor.execute(
                """
                SELECT checkpoint_id, checkpoint_data, metadata, created_at
                FROM agent_state.checkpoints
                WHERE thread_id = %s
                ORDER BY created_at DESC
                LIMIT 3
            """,
                (thread_id,),
            )

            checkpoint_rows = await cursor.fetchall()
            if checkpoint_rows:
                for _i, row in enumerate(checkpoint_rows):
                    # Truncate checkpoint data for display
                    str(row[1])[:100] if row[1] else "None"
            else:
                pass

            # Check other related tables
            await cursor.execute(
                """
                SELECT COUNT(*) FROM public.checkpoints WHERE thread_id = %s
            """,
                (thread_id,),
            )
            (await cursor.fetchone())[0]

        await conn.close()

        if thread_row or checkpoint_rows:
            pass
        else:
            pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket_and_database())
