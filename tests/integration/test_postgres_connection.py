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


async def test_postgres_connection():
    """Test direct PostgreSQL connection to Supabase."""
    # Check what Supabase environment variables we have
    supabase_vars = {
        k: v for k, v in os.environ.items() if "SUPABASE" in k or "POSTGRES" in k
    }
    for key, _value in supabase_vars.items():
        if "PASSWORD" in key or "KEY" in key or "SECRET" in key:
            # Mask sensitive values
            pass
        else:
            pass

    # Try to create a PostgreSQL config
    try:
        from haive.core.persistence.postgres_config import PostgresCheckpointerConfig

        # Check for connection string first
        connection_string = (
            os.getenv("SUPABASE_POSTGRES_CONNECTION")
            or os.getenv("SUPABASE_DATABASE_URI_SSL")
            or os.getenv("SUPABASE_DATABASE_URI")
        )

        if connection_string:
            # Check if the connection string has placeholders
            if (
                "[NEED_PASSWORD]" in connection_string
                or "[PASSWORD_NEEDED]" in connection_string
            ):
                # Use the complete URI with password
                connection_string = os.getenv("SUPABASE_DATABASE_URI")

            config = PostgresCheckpointerConfig(
                connection_string=connection_string, setup_needed=True
            )
        else:
            # Fall back to individual parameters
            config = PostgresCheckpointerConfig(
                db_host=os.getenv("SUPABASE_HOST", "localhost"),
                db_port=int(os.getenv("SUPABASE_PORT", "6543")),
                db_name=os.getenv("SUPABASE_DBNAME", "postgres"),
                db_user=os.getenv("SUPABASE_USER", "postgres"),
                db_pass=os.getenv("SUPABASE_PASSWORD", ""),
                ssl_mode="require",
                setup_needed=True,
            )

    except Exception:
        return

    # Try to create a checkpointer and test connection
    try:
        from haive.core.persistence.factory import acreate_postgres_checkpointer

        checkpointer = await acreate_postgres_checkpointer(config)

        # Test if we can get a connection
        try:
            async with checkpointer.conn.connection() as conn, conn.cursor() as cursor:
                # Test basic query
                await cursor.execute("SELECT version()")
                await cursor.fetchone()

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
                    # Check tables in agent_state schema
                    await cursor.execute(
                        """
                            SELECT table_name
                            FROM information_schema.tables
                            WHERE table_schema = 'agent_state'
                            ORDER BY table_name
                        """
                    )
                    await cursor.fetchall()
                else:
                    pass

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
                    pass
                else:
                    pass

        except Exception:
            import traceback

            traceback.print_exc()

    except Exception:
        import traceback

        traceback.print_exc()


# Also test the SupabasePersistence adapter
async def test_supabase_persistence():
    """Test the SupabasePersistence adapter."""
    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        persistence = SupabasePersistence()

        # Check the internal config

        # Try to get a checkpointer
        await persistence.get_checkpointer()

    except Exception:
        import traceback

        traceback.print_exc()


async def main():
    """Run all tests."""
    await test_postgres_connection()
    await test_supabase_persistence()


if __name__ == "__main__":
    asyncio.run(main())
