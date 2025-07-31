#!/usr/bin/env python3
"""Directly test Supabase connection and persistence without WebSocket."""

import asyncio
import os
from datetime import datetime

import asyncpg


async def test_supabase_connection():
    """Test direct connection to Supabase and check persistence setup."""

    print("🔍 Testing Supabase Connection")
    print("=" * 50)

    # Try the working oecoeyomphckolkywbzz instance first
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI")

    if supabase_uri:
        print("✓ Using oecoeyomphckolkywbzz instance (pooler connection)")")
    else:
        # Try the SSL version
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL")
        if supabase_uri and "[PASSWORD_NEEDED]" in supabase_uri:
            password = "ITfz5B0wU6ehVXI1"
            supabase_uri = supabase_uri.replace("[PASSWORD_NEEDED]", password)
            print("✓ Using zkssazqhwcetsnbiuqik instance with password"d")

    if not supabase_uri:
        print("❌ No Supabase connection string found")
        return False

    # Extract host for display
    host = (
        supabase_uri.split("@")[1].split("/")[0] if "@" in supabase_uri else "unknown"
    )
    print(f"✓ Connecting to: {host}")

    try:
        # Parse and fix the connection string to ensure proper username format
        if (
            "postgres.oecoeyomphckolkywbzz" not in supabase_uri
            and "oecoeyomphckolkywbzz" in supabase_uri
        ):
            # Fix username format
            supabase_uri = supabase_uri.replace(
                "postgresql://postgres:", "postgresql://postgres.oecoeyomphckolkywbzz:"
            )
            print("✓ Fixed username format to postgres.oecoeyomphckolkywbzz")

        # Connect
        conn = await asyncpg.connect(supabase_uri)
        print("✓ Connected to Supabase PostgreSQL")

        # Check agent_state schema
        schemas = await conn.fetch(
            """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'agent_state'
        """
        )

        if not schemas:
            print("❌ agent_state schema not found")
            await conn.close()
            return False

        print("✓ agent_state schema exists")

        # List all tables
        tables = await conn.fetch(
            """
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'agent_state' AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'agent_state'
            ORDER BY table_name
        """
        )

        print(f"\n📋 Found {len(tables)} tables in agent_state schema:")
        for table in tables:
            table_name = table["table_name"]
            column_count = table["column_count"]

            # Get row count
            try:
                row_count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM agent_state.{table_name}"
                )
                print(f"  - {table_name}: {column_count} columns, {row_count} rows")
            except Exception as e:
                print(
                    f"  - {table_name}: {column_count} columns, error counting rows: {e}"
                )

        # Test insert into threads table
        print("\n🧪 Testing insert into threads table..."..")
        test_thread_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        test_user_id = "test-user-123"

        try:
            await conn.execute(
                """
                INSERT INTO agent_state.threads (thread_id, user_id, agent_name, metadata)
                VALUES ($1, $2, $3, $4)
            """,
                test_thread_id,
                test_user_id,
                "TestAgent",
                {"test": True},
            )

            print(f"✓ Successfully inserted test thread: {test_thread_id}")

            # Verify the insert
            result = await conn.fetchrow(
                """
                SELECT * FROM agent_state.threads 
                WHERE thread_id = $1
            """,
                test_thread_id,
            )

            if result:
                print(f"✓ Verified thread exists: {dict(result)}")
            else:
                print("❌ Could not verify thread insertion")

        except Exception as e:
            print(f"❌ Failed to insert test thread: {e}")

        # Test checkpoints table
        print("\n🔄 Testing checkpoints table..."..")
        try:
            # Check if we can insert a checkpoint
            checkpoint_id = f"checkpoint-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            await conn.execute(
                """
                INSERT INTO agent_state.checkpoints (thread_id, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """,
                test_thread_id,
                checkpoint_id,
                None,
                "standard",
                {"state": "test"},
                {"source": "test"},
            )

            print(f"✓ Successfully inserted test checkpoint: {checkpoint_id}")

            # Count checkpoints for our thread
            checkpoint_count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM agent_state.checkpoints 
                WHERE thread_id = $1
            """,
                test_thread_id,
            )

            print(f"✓ Thread has {checkpoint_count} checkpoints")

        except Exception as e:
            print(f"❌ Failed to test checkpoints: {e}")

        # Show recent activity
        print("\n📊 Recent activity:"y:")

        recent_threads = await conn.fetch(
            """
            SELECT thread_id, user_id, agent_name, created_at
            FROM agent_state.threads 
            ORDER BY created_at DESC 
            LIMIT 5
        """
        )

        if recent_threads:
            print(f"Recent threads ({len(recent_threads)}):")
            for thread in recent_threads:
                print(
                    f"  - {thread['thread_id'][:20]}... | {thread['user_id']} | {thread['agent_name']} | {thread['created_at']}"
                )

        recent_checkpoints = await conn.fetch(
            """
            SELECT thread_id, checkpoint_id, type, created_at
            FROM agent_state.checkpoints 
            ORDER BY created_at DESC 
            LIMIT 5
        """
        )

        if recent_checkpoints:
            print(f"Recent checkpoints ({len(recent_checkpoints)}):")
            for cp in recent_checkpoints:
                print(
                    f"  - {cp['checkpoint_id'][:20]}... | {cp['thread_id'][:20]}... | {cp['type']} | {cp['created_at']}"
                )

        await conn.close()
        print("\n🎉 Supabase connection and persistence test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def test_persistence_adapter():
    """Test the Supabase persistence adapter directly."""

    print("\n🔧 Testing Supabase Persistence Adapter")
    print("=" * 50)

    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        # Create adapter
        persistence = SupabasePersistence()
        print("✓ Created SupabasePersistence adapter")

        # Test thread registration
        thread_id = f"adapter-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        user_id = "test-user-456"

        success = await persistence.register_thread(
            thread_id=thread_id,
            user_id=user_id,
            metadata={"test": True, "adapter": "supabase"},
        )

        if success:
            print(f"✓ Successfully registered thread via adapter: {thread_id}")
        else:
            print("❌ Failed to register thread via adapter"r")
            return False

        # Test state update
        test_state = {
            "messages": [{"role": "user", "content": "Hello from persistence test"}],
            "step": 1,
            "timestamp": datetime.now().isoformat(),
        }

        update_success = await persistence.update_state(
            thread_id=thread_id,
            user_id=user_id,
            data=test_state,
            metadata={"source": "persistence_test"},
        )

        if update_success:
            print("✓ Successfully updated state via adapter"r")
        else:
            print("❌ Failed to update state via adapter"r")
            return False

        # Test state retrieval
        retrieved_state = await persistence.get_state(
            thread_id=thread_id, user_id=user_id
        )

        if retrieved_state:
            print("✓ Successfully retrieved state via adapter"r")
            print(
                f"  State keys: {list(retrieved_state.keys()) if isinstance(retrieved_state, dict) else 'not a dict'}"
            )
        else:
            print("❌ Failed to retrieve state via adapter"r")
            return False

        print("\n🎉 Persistence adapter test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Persistence adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""

    print("🚀 Starting Supabase Persistence Tests")
    print("=" * 60)

    # Test 1: Direct connection
    connection_success = await test_supabase_connection()

    if connection_success:
        # Test 2: Persistence adapter
        adapter_success = await test_persistence_adapter()

        if adapter_success:
            print("\n🎊 ALL TESTS PASSED!")
            print("Supabase persistence is working correctly.")
        else:
            print("\n⚠️  Connection works but adapter has issues")
    else:
        print("\n❌ Connection failed - check environment variables")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
