#!/usr/bin/env python3
"""Test WebSocket API with Supabase persistence."""

import asyncio
import json
from uuid import uuid4

import psycopg
import websockets


async def test_websocket_and_database():
    """Test WebSocket endpoint and verify data is stored in Supabase."""
    print("Testing WebSocket API with Supabase persistence...")

    # Create a unique thread ID
    thread_id = f"test-ws-{uuid4()}"
    print(f"Using thread ID: {thread_id}")

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
        print("\nConnecting to WebSocket...")
        async with websockets.connect("ws://localhost:8192/agents/ws") as websocket:
            print("✓ Connected to WebSocket")

            # Send message
            print("Sending message to agent...")
            await websocket.send(json.dumps(test_message))
            print("✓ Message sent")

            # Receive response
            print("Waiting for response...")
            responses = []
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    responses.append(response)
                    print(f"Received: {response[:100]}...")

                    # Try to parse as JSON
                    try:
                        data = json.loads(response)
                        if data.get("type") == "complete":
                            print("✓ Received completion signal")
                            break
                    except json.JSONDecodeError:
                        pass

            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                if responses:
                    print(f"✓ Received {len(responses)} responses")
                else:
                    print("✗ No responses received")
                    return

    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
        return

    # Now check if data was stored in Supabase
    print("\n=== Checking Supabase Database ===")

    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)
        print("✓ Connected to Supabase")

        async with conn.cursor() as cursor:
            # Check if thread was created in public.threads
            print(f"\nChecking for thread: {thread_id}")
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
                print("✓ Thread found in public.threads:")
                print(f"  Thread ID: {thread_row[0]}")
                print(f"  Name: {thread_row[1]}")
                print(f"  Metadata: {thread_row[2]}")
                print(f"  Created: {thread_row[3]}")
            else:
                print("✗ Thread not found in public.threads")

            # Check if checkpoint was created in agent_state.checkpoints
            print("\nChecking for checkpoints...")
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
                print(f"✓ Found {len(checkpoint_rows)} checkpoints:")
                for i, row in enumerate(checkpoint_rows):
                    print(f"  Checkpoint {i+1}: {row[0]}")
                    print(f"    Created: {row[3]}")
                    # Truncate checkpoint data for display
                    data_str = str(row[1])[:100] if row[1] else "None"
                    print(f"    Data: {data_str}...")
            else:
                print("✗ No checkpoints found")

            # Check other related tables
            await cursor.execute(
                """
                SELECT COUNT(*) FROM public.checkpoints WHERE thread_id = %s
            """,
                (thread_id,),
            )
            checkpoint_count = (await cursor.fetchone())[0]
            print(f"\nPublic checkpoints: {checkpoint_count}")

        await conn.close()

        if thread_row or checkpoint_rows:
            print("\n🎉 SUCCESS: Data was successfully stored in Supabase!")
            print("   - WebSocket connection worked")
            print("   - Agent processed the message")
            print("   - Persistence system stored data in Supabase")
        else:
            print("\n❌ Data not found in Supabase database")

    except Exception as e:
        print(f"✗ Database check failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket_and_database())
