#!/usr/bin/env python3
"""Test Supabase persistence adapter directly."""

import asyncio
import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

from haive.dataflow.persistence.supabase_adapter import SupabasePersistence


async def test_persistence():
    """Test the SupabasePersistence adapter."""
    # Create persistence adapter
    persistence = SupabasePersistence()

    # Check the internal config

    # Try to get a checkpointer
    checkpointer = await persistence.get_checkpointer()

    # Test connection
    try:
        async with checkpointer.conn.connection() as conn, conn.cursor() as cursor:
            await cursor.execute("SELECT version()")
            await cursor.fetchone()

            # Check for our migration
            await cursor.execute(
                """
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.schemata
                        WHERE schema_name = 'agent_state'
                    )
                """
            )
            has_agent_state = (await cursor.fetchone())[0]

            await cursor.execute(
                """
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'threads'
                    )
                """
            )
            has_threads = (await cursor.fetchone())[0]

            if has_agent_state and has_threads:
                pass
            else:
                pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_persistence())
