#!/usr/bin/env python3
"""Directly test Supabase connection and persistence without WebSocket."""

import asyncio
import contextlib
import os
from datetime import datetime

import asyncpg


async def test_supabase_connection():
    """Test direct connection to Supabase and check persistence setup."""
    # Try the working oecoeyomphckolkywbzz instance first
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI")

    if supabase_uri:
        pass
    else:
        # Try the SSL version
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL")
        if supabase_uri and "[PASSWORD_NEEDED]" in supabase_uri:
            password = "ITfz5B0wU6ehVXI1"
            supabase_uri = supabase_uri.replace("[PASSWORD_NEEDED]", password)

    if not supabase_uri:
        return False

    # Extract host for display
    (supabase_uri.split("@")[1].split("/")[0] if "@" in supabase_uri else "unknown")

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

        # Connect
        conn = await asyncpg.connect(supabase_uri)

        # Check agent_state schema
        schemas = await conn.fetch(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'agent_state'
        """
        )

        if not schemas:
            await conn.close()
            return False

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

        for table in tables:
            table_name = table["table_name"]
            table["column_count"]

            # Get row count
            with contextlib.suppress(Exception):
                await conn.fetchval(f"SELECT COUNT(*) FROM agent_state.{table_name}")

        # Test insert into threads table
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

            # Verify the insert
            result = await conn.fetchrow(
                """
                SELECT * FROM agent_state.threads
                WHERE thread_id = $1
            """,
                test_thread_id,
            )

            if result:
                pass
            else:
                pass

        except Exception:
            pass

        # Test checkpoints table
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

            # Count checkpoints for our thread
            await conn.fetchval(
                """
                SELECT COUNT(*) FROM agent_state.checkpoints
                WHERE thread_id = $1
            """,
                test_thread_id,
            )

        except Exception:
            pass

        # Show recent activity

        recent_threads = await conn.fetch(
            """
            SELECT thread_id, user_id, agent_name, created_at
            FROM agent_state.threads
            ORDER BY created_at DESC
            LIMIT 5
        """
        )

        if recent_threads:
            for _thread in recent_threads:
                pass

        recent_checkpoints = await conn.fetch(
            """
            SELECT thread_id, checkpoint_id, type, created_at
            FROM agent_state.checkpoints
            ORDER BY created_at DESC
            LIMIT 5
        """
        )

        if recent_checkpoints:
            for _cp in recent_checkpoints:
                pass

        await conn.close()
        return True

    except Exception:
        return False


async def test_persistence_adapter():
    """Test the Supabase persistence adapter directly."""
    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        # Create adapter
        persistence = SupabasePersistence()

        # Test thread registration
        thread_id = f"adapter-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        user_id = "test-user-456"

        success = await persistence.register_thread(
            thread_id=thread_id,
            user_id=user_id,
            metadata={"test": True, "adapter": "supabase"},
        )

        if success:
            pass
        else:
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
            pass
        else:
            return False

        # Test state retrieval
        retrieved_state = await persistence.get_state(
            thread_id=thread_id, user_id=user_id
        )

        if retrieved_state:
            pass
        else:
            return False

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    # Test 1: Direct connection
    connection_success = await test_supabase_connection()

    if connection_success:
        # Test 2: Persistence adapter
        adapter_success = await test_persistence_adapter()

        if adapter_success:
            pass
        else:
            pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
