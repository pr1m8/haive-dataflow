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
    print("Testing SupabasePersistence adapter...")

    # Create persistence adapter
    persistence = SupabasePersistence()

    # Check the internal config
    print(f"\nPostgreSQL Config:")
    print(
        f"  Connection string: {persistence.postgres_config.connection_string[:60]}..."
    )

    # Try to get a checkpointer
    print("\nGetting checkpointer...")
    checkpointer = await persistence.get_checkpointer()
    print("✓ Got checkpointer")

    # Test connection
    print("\nTesting connection...")
    try:
        async with checkpointer.conn.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT version()")
                version = await cursor.fetchone()
                print(f"✓ Connected to PostgreSQL!")
                print(f"  Version: {version[0][:50]}...")

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

                print(f"\n✓ Migration status:")
                print(f"  agent_state schema: {has_agent_state}")
                print(f"  public.threads table: {has_threads}")

                if has_agent_state and has_threads:
                    print("\n✅ Successfully connected to Supabase with migrations!")
                else:
                    print("\n❌ Connected but migrations not found")

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_persistence())
