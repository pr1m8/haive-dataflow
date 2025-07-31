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
    # Create persistence adapter
    persistence = SupabasePersistence()

    # Check connection
    checkpointer = await persistence.get_checkpointer()

    # Test direct database operations

    try:
        async with checkpointer.conn.connection() as conn:
            async with conn.cursor() as cursor:
                # Test basic query
                await cursor.execute("SELECT current_timestamp")
                await cursor.fetchone()

                # Check if we can insert into public.threads
                thread_id = f"test-{uuid4()}"
                user_id = "test-user-123"

                await cursor.execute(
                    """
                    INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """,
                    (thread_id, user_id, "TestAgent", '{"test": true}'),
                )

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
                    pass
                else:
                    pass

                # Check agent_state schema tables
                await cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'agent_state'
                    ORDER BY table_name
                """
                )
                await cursor.fetchall()

                # Clean up
                await cursor.execute(
                    "DELETE FROM public.threads WHERE id = %s", (thread_id,)
                )

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_minimal_persistence())
