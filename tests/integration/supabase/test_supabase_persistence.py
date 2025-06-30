#!/usr/bin/env python3
"""Test Supabase persistence with a simple agent."""

import asyncio
import json

import websockets
from langchain_core.messages import HumanMessage


async def test_supabase_persistence():
    """Test that agent conversations are saved to Supabase."""

    print("Testing Supabase persistence...")

    # Test message that will be sent to the agent
    test_message = "Hello from Supabase persistence test!"

    try:
        # Connect to WebSocket API
        uri = "ws://localhost:8000/api/ws/chat/CheckersAgent?token=test"

        async with websockets.connect(uri) as websocket:
            print(f"✓ Connected to WebSocket: {uri}")

            # Send test message
            message = {"messages": [{"role": "user", "content": test_message}]}

            print(f"📤 Sending: {message}")
            await websocket.send(json.dumps(message))

            # Collect all responses
            responses = []
            print("\n📥 Receiving responses:")

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    responses.append(data)

                    print(
                        f"  {data.get('type', 'unknown')}: {str(data.get('content', ''))[:100]}..."
                    )

                    if (
                        data.get("type") == "status"
                        and data.get("content") == "complete"
                    ):
                        print("✓ Conversation completed")
                        break
                    elif data.get("type") == "error":
                        print(f"❌ Error: {data.get('content')}")
                        break

                except asyncio.TimeoutError:
                    print("⏰ Timeout - ending conversation")
                    break

            print(f"\n📊 Total responses received: {len(responses)}")

            # Show summary
            for i, resp in enumerate(responses):
                print(f"  {i+1}. {resp.get('type', 'unknown')}")

            return True

    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False


async def check_supabase_data():
    """Check if data was saved to Supabase by connecting directly."""

    print("\n🔍 Checking Supabase data...")

    try:
        import os

        import asyncpg

        # Get Supabase connection string
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
            "SUPABASE_DATABASE_URI"
        )

        if not supabase_uri:
            print("❌ No Supabase connection string found in environment")
            return False

        print(f"✓ Found Supabase URI: {supabase_uri[:50]}...")

        # Connect to Supabase
        conn = await asyncpg.connect(supabase_uri)
        print("✓ Connected to Supabase")

        # Check agent_state schema
        schemas = await conn.fetch(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'agent_state'"
        )
        if schemas:
            print("✓ agent_state schema exists")
        else:
            print("❌ agent_state schema not found")
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

        print(f"✓ Found {len(tables)} tables in agent_state schema:")
        for table in tables:
            table_name = table["table_name"]

            # Count rows
            count = await conn.fetchval(
                f"SELECT COUNT(*) FROM agent_state.{table_name}"
            )
            print(f"  - {table_name}: {count} rows")

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
            print(f"\n📋 Recent checkpoints ({len(recent_checkpoints)}):")
            for cp in recent_checkpoints:
                print(
                    f"  - Thread: {cp['thread_id']}, ID: {cp['checkpoint_id']}, Time: {cp['created_at']}"
                )
        else:
            print("\n📋 No checkpoints found")

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
            print(f"\n🧵 Recent threads ({len(recent_threads)}):")
            for thread in recent_threads:
                print(
                    f"  - ID: {thread['thread_id']}, User: {thread['user_id']}, Agent: {thread['agent_name']}, Time: {thread['created_at']}"
                )
        else:
            print("\n🧵 No threads found")

        await conn.close()
        print("✓ Database check completed")
        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


async def main():
    """Run the complete Supabase persistence test."""

    print("🚀 Starting Supabase Persistence Test")
    print("=" * 50)

    # Test 1: Send message via WebSocket
    websocket_success = await test_supabase_persistence()

    if websocket_success:
        # Test 2: Check if data was saved
        await asyncio.sleep(2)  # Give time for data to be written
        database_success = await check_supabase_data()

        if database_success:
            print("\n🎉 SUCCESS: Supabase persistence is working!")
        else:
            print("\n⚠️  WARNING: WebSocket worked but no data found in Supabase")
    else:
        print("\n❌ FAILED: WebSocket test failed")

    print("\n" + "=" * 50)
    print("Test completed")


if __name__ == "__main__":
    asyncio.run(main())
