#!/usr/bin/env python3
"""Minimal test to verify Supabase persistence is working."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from haive.dataflow.persistence.supabase_adapter import SupabasePersistence


async def test_minimal_persistence():
    """Test minimal persistence operations."""
    print("Testing minimal Supabase persistence...")

    # Create persistence adapter
    persistence = SupabasePersistence()
    print("✓ Created persistence adapter")

    # Check connection
    checkpointer = await persistence.get_checkpointer()
    print("✓ Got checkpointer")

    # Test direct database operations
    print("\nTesting direct database operations...")

    try:
        async with checkpointer.conn.connection() as conn:
            async with conn.cursor() as cursor:
                # Test basic query
                await cursor.execute("SELECT current_timestamp")
                timestamp = await cursor.fetchone()
                print(f"✓ Current timestamp: {timestamp[0]}")

                # Check if we can insert into public.threads
                thread_id = f"test-{uuid4()}"
                user_id = "test-user-123"

                print(f"\nInserting test thread: {thread_id}")
                await cursor.execute(
                    """
                    INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """,
                    (thread_id, user_id, "TestAgent", '{"test": true}'),
                )

                print("✓ Inserted thread")

                # Check if we can read it back
                await cursor.execute(
                    """
                    SELECT id, user_id, agent_name, metadata, created_at
                    FROM public.threads 
                    WHERE id = %s
                """,
                    (thread_id,),
                )

                row = await cursor.fetchone()
                if row:
                    print("✓ Retrieved thread:")
                    print(f"  ID: {row[0]}")
                    print(f"  User ID: {row[1]}")
                    print(f"  Agent: {row[2]}")
                    print(f"  Metadata: {row[3]}")
                    print(f"  Created: {row[4]}")
                else:
                    print("✗ Could not retrieve thread")

                # Check agent_state schema tables
                await cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'agent_state'
                    ORDER BY table_name
                """
                )
                tables = await cursor.fetchall()
                print(f"\n✓ Agent state tables: {[t[0] for t in tables]}")

                # Clean up
                await cursor.execute(
                    "DELETE FROM public.threads WHERE id = %s", (thread_id,)
                )
                print("✓ Cleaned up test data")

    except Exception as e:
        print(f"✗ Database operation failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n✅ Persistence test completed!")


if __name__ == "__main__":
    asyncio.run(test_minimal_persistence())
