#!/usr/bin/env python3
"""Test PostgreSQL connection to Supabase."""

import asyncio
import os
import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))
sys.path.insert(0, str(current_dir.parent.parent.parent))

# Load environment variables
from dotenv import load_dotenv

env_path = current_dir.parent.parent.parent / ".env"
load_dotenv(env_path)

print(f"Loading .env from: {env_path}")


async def test_postgres_connection():
    """Test direct PostgreSQL connection to Supabase."""

    # Check what Supabase environment variables we have
    print("\n=== Environment Variables ===")
    supabase_vars = {
        k: v for k, v in os.environ.items() if "SUPABASE" in k or "POSTGRES" in k
    }
    for key, value in supabase_vars.items():
        if "PASSWORD" in key or "KEY" in key or "SECRET" in key:
            # Mask sensitive values
            print(
                f"{key}: {'*' * 10}...{value[-4:] if len(value) > 4 else '*' * len(value)}"
            )
        else:
            print(f"{key}: {value}")

    # Try to create a PostgreSQL config
    print("\n=== Testing PostgreSQL Config Creation ===")
    try:
        from haive.core.persistence.postgres_config import PostgresCheckpointerConfig

        # Check for connection string first
        connection_string = (
            os.getenv("SUPABASE_POSTGRES_CONNECTION")
            or os.getenv("SUPABASE_DATABASE_URI_SSL")
            or os.getenv("SUPABASE_DATABASE_URI")
        )

        if connection_string:
            print(f"Found connection string: {connection_string[:50]}...")

            # Check if the connection string has placeholders
            if (
                "[NEED_PASSWORD]" in connection_string
                or "[PASSWORD_NEEDED]" in connection_string
            ):
                print(
                    "Connection string has password placeholder, using SUPABASE_DATABASE_URI instead"
                )
                # Use the complete URI with password
                connection_string = os.getenv("SUPABASE_DATABASE_URI")
                print(f"Using: {connection_string[:50]}...")

            config = PostgresCheckpointerConfig(
                connection_string=connection_string, setup_needed=True
            )
        else:
            # Fall back to individual parameters
            print("No connection string found, using individual parameters")
            config = PostgresCheckpointerConfig(
                db_host=os.getenv("SUPABASE_HOST", "localhost"),
                db_port=int(os.getenv("SUPABASE_PORT", "6543")),
                db_name=os.getenv("SUPABASE_DBNAME", "postgres"),
                db_user=os.getenv("SUPABASE_USER", "postgres"),
                db_pass=os.getenv("SUPABASE_PASSWORD", ""),
                ssl_mode="require",
                setup_needed=True,
            )

        print("✓ PostgreSQL config created successfully")
        print(f"  Host: {config.db_host}")
        print(f"  Port: {config.db_port}")
        print(f"  Database: {config.db_name}")
        print(f"  User: {config.db_user}")
        print(f"  SSL Mode: {config.ssl_mode}")

    except Exception as e:
        print(f"✗ Failed to create PostgreSQL config: {e}")
        return

    # Try to create a checkpointer and test connection
    print("\n=== Testing Checkpointer Creation ===")
    try:
        from haive.core.persistence.factory import acreate_postgres_checkpointer

        checkpointer = await acreate_postgres_checkpointer(config)
        print("✓ Checkpointer created successfully")

        # Test if we can get a connection
        print("\n=== Testing Database Connection ===")
        try:
            async with checkpointer.conn.connection() as conn:
                async with conn.cursor() as cursor:
                    # Test basic query
                    await cursor.execute("SELECT version()")
                    version = await cursor.fetchone()
                    print("✓ Connected to PostgreSQL!"!")
                    print(f"  Version: {version[0]}")

                    # Check if we can see the agent_state schema
                    await cursor.execute(
                        """
                        SELECT schema_name 
                        FROM information_schema.schemata 
                        WHERE schema_name = 'agent_state'
                    """
                    )
                    schema_exists = await cursor.fetchone()

                    if schema_exists:
                        print("✓ agent_state schema exists")

                        # Check tables in agent_state schema
                        await cursor.execute(
                            """
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'agent_state'
                            ORDER BY table_name
                        """
                        )
                        tables = await cursor.fetchall()
                        print(f"  Tables in agent_state: {[t[0] for t in tables]}")
                    else:
                        print("✗ agent_state schema not found")

                    # Check if we can see the public.threads table
                    await cursor.execute(
                        """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'threads'
                    """
                    )
                    threads_exists = await cursor.fetchone()

                    if threads_exists:
                        print("✓ public.threads table exists")
                    else:
                        print("✗ public.threads table not found")

        except Exception as e:
            print(f"✗ Failed to connect to database: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"✗ Failed to create checkpointer: {e}")
        import traceback

        traceback.print_exc()


# Also test the SupabasePersistence adapter
async def test_supabase_persistence():
    """Test the SupabasePersistence adapter."""
    print("\n=== Testing SupabasePersistence Adapter ===")

    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        persistence = SupabasePersistence()
        print("✓ SupabasePersistence created")

        # Check the internal config
        print(f"  Config host: {persistence.postgres_config.db_host}")
        print(f"  Config port: {persistence.postgres_config.db_port}")
        print(f"  Config database: {persistence.postgres_config.db_name}")
        print(f"  Config user: {persistence.postgres_config.db_user}")

        # Try to get a checkpointer
        await persistence.get_checkpointer()
        print("✓ Got checkpointer from persistence adapter")

    except Exception as e:
        print(f"✗ Failed to test SupabasePersistence: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run all tests."""
    await test_postgres_connection()
    await test_supabase_persistence()


if __name__ == "__main__":
    asyncio.run(main())
