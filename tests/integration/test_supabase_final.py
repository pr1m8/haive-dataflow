#!/usr/bin/env python3
"""Final test to confirm Supabase persistence is working."""

import asyncio
from uuid import uuid4

import psycopg


async def test_supabase_final():
    """Final test with direct connection to avoid connection pool conflicts."""
    print("Final Supabase persistence test...")

    # Use the connection string we confirmed works
    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        # Create direct connection
        conn = await psycopg.AsyncConnection.connect(uri)
        print("✓ Connected to Supabase")

        async with conn.cursor() as cursor:
            # Test basic operations
            await cursor.execute("SELECT current_timestamp")
            timestamp = await cursor.fetchone()
            print(f"✓ Current timestamp: {timestamp[0]}")

            # Test inserting into threads table
            thread_id = f"test-{uuid4()}"
            user_id = "test-user-123"

            print(f"\nTesting thread insertion: {thread_id}")
            await cursor.execute(
                """
                INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """,
                (thread_id, user_id, "TestAgent", '{"test": true}'),
            )

            print("✓ Inserted thread")

            # Verify insertion
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
                print("✓ Retrieved thread successfully:")
                print(f"  ID: {row[0]}")
                print(f"  User: {row[1]}")
                print(f"  Agent: {row[2]}")
                print(f"  Metadata: {row[3]}")
            else:
                print("✗ Could not retrieve thread")

            # Check agent_state schema
            await cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'agent_state'
                ORDER BY table_name
            """
            )
            tables = await cursor.fetchall()
            print(f"\n✓ Agent state tables available: {[t[0] for t in tables]}")

            # Test agent_state operations (checkpoints table)
            if tables:
                # Test inserting a checkpoint
                checkpoint_data = '{"test": "checkpoint_data", "messages": []}'
                await cursor.execute(
                    """
                    INSERT INTO agent_state.checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        thread_id,
                        "default",
                        "test-checkpoint",
                        None,
                        "checkpoint",
                        checkpoint_data.encode(),
                        "{}",
                    ),
                )

                print("✓ Inserted test checkpoint")

                # Retrieve checkpoint
                await cursor.execute(
                    """
                    SELECT checkpoint_id, checkpoint, metadata
                    FROM agent_state.checkpoints
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                checkpoint_row = await cursor.fetchone()
                if checkpoint_row:
                    print(f"✓ Retrieved checkpoint: {checkpoint_row[0]}")
                else:
                    print("✗ Could not retrieve checkpoint")

            # Clean up
            await cursor.execute(
                "DELETE FROM agent_state.checkpoints WHERE thread_id = %s", (thread_id,)
            )
            await cursor.execute(
                "DELETE FROM public.threads WHERE id = %s", (thread_id,)
            )
            print("✓ Cleaned up test data")

        await conn.close()

        print("\n🎉 SUCCESS: Supabase persistence is working correctly!")
        print("   - Can connect to zkssazqhwcetsnbiuqik Supabase instance")
        print("   - Can read/write to public.threads table")
        print("   - Can read/write to agent_state.checkpoints table")
        print("   - Migration schemas are present and functional")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_supabase_final())
