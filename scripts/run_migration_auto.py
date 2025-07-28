#!/usr/bin/env python3
"""
Automated Supabase migration that runs the SQL directly
"""

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
    """Get PostgreSQL connection string for Supabase"""

    supabase_config = get_supabase_server_config()

    # Parse Supabase URL to get connection details
    url = supabase_config.url  # https://zkssazqhwcetsnbiuqik.supabase.co
    url.split("//")[1].split(".")[0]

    # Build connection string
    conn_str = f"postgresql://postgres:{os.getenv('SUPABASE_PASSWORD', 'ITfz5B0wU6ehVXI1')}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    return conn_str


def run_sql_migration():
    """Run the SQL migration directly"""

    print("=== Running SQL Migration ===")

    # Read the SQL file
    sql_file = project_root / "supabase_migration.sql"
    if not sql_file.exists():
        print(f"✗ SQL file not found: {sql_file}")
        return False

    with open(sql_file) as f:
        sql_content = f.read()

    try:
        # Connect to Supabase PostgreSQL
        conn_str = get_postgres_connection_string()
        print("Connecting to Supabase PostgreSQL...")

        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                # Execute the SQL migration
                print("Executing SQL migration...")
                cursor.execute(sql_content)
                conn.commit()
                print("✓ SQL migration completed successfully")

        return True

    except Exception as e:
        print(f"✗ SQL migration failed: {e}")
        return False


async def test_checkpointer():
    """Test the Supabase checkpointer functionality"""

    print("\n=== Testing Checkpointer ===")

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
            print("✓ Thread registration successful")
            print(f"✓ Thread {test_thread_id} registered for user {test_user_id}")
        else:
            print("✗ Thread registration failed")
            return False

        print("✓ Supabase checkpointer is working correctly")
        return True

    except Exception as e:
        print(f"✗ Checkpointer test failed: {e}")
        return False


async def main():
    """Main migration function"""

    print("🚀 Automated Haive Supabase Migration")
    print("=" * 50)

    # Check environment
    print("=== Checking Environment ===")
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            display_value = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: Not set")
            return False

    # Run SQL migration
    if not run_sql_migration():
        return False

    # Test checkpointer
    if not await test_checkpointer():
        return False

    print("\n🎉 Migration Complete!")
    print("=" * 50)
    print("✓ Supabase database schema created")
    print("✓ Checkpointer tested and working")
    print("✓ Agent persistence now uses Supabase")

    print("\nYour agent conversations will now be stored in Supabase!")
    print("Check your Supabase dashboard to see the new agent_state schema.")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nMigration cancelled by user")
        sys.exit(1)
