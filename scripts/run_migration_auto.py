#!/usr/bin/env python3
"""Automated Supabase migration that runs the SQL directly."""

import asyncio
import os
import sys
from pathlib import Path

import psycopg2

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages/haive-dataflow/src"))
sys.path.insert(0, str(project_root / "packages/haive-core/src"))

from .config.environment import get_supabase_server_config


def get_postgres_connection_string():
    """Get PostgreSQL connection string for Supabase."""
    supabase_config = get_supabase_server_config()

    # Parse Supabase URL to get connection details
    url = supabase_config.url  # https://zkssazqhwcetsnbiuqik.supabase.co
    url.split("//")[1].split(".")[0]

    # Build connection string
    conn_str = f"postgresql://postgres:{os.getenv('SUPABASE_PASSWORD', 'ITfz5B0wU6ehVXI1')}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    return conn_str


def run_sql_migration():
    """Run the SQL migration directly."""
    # Read the SQL file
    sql_file = project_root / "supabase_migration.sql"
    if not sql_file.exists():
        return False

    with open(sql_file) as f:
        sql_content = f.read()

    try:
        # Connect to Supabase PostgreSQL
        conn_str = get_postgres_connection_string()

        with psycopg2.connect(conn_str) as conn, conn.cursor() as cursor:
            # Execute the SQL migration
            cursor.execute(sql_content)
            conn.commit()

        return True

    except Exception:
        return False


async def test_checkpointer():
    """Test the Supabase checkpointer functionality."""
    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        persistence = SupabasePersistence()

        # Test thread registration
        test_thread_id = "migration-test-thread"
        test_user_id = "b9284d47-72b5-4960-a177-0788fc4b0809"  # Your actual user ID

        success = await persistence.register_thread(
            thread_id=test_thread_id,
            user_id=test_user_id,
            metadata={"test": True, "migration": True, "agent_name": "TestAgent"},
        )

        if success:
            pass
        else:
            return False

        return True

    except Exception:
        return False


async def main():
    """Main migration function."""
    # Check environment
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"
        else:
            return False

    # Run SQL migration
    if not run_sql_migration():
        return False

    # Test checkpointer
    return await test_checkpointer()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        sys.exit(1)
