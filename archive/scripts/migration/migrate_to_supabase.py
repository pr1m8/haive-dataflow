#!/usr/bin/env python3
"""Migration script to set up Supabase for Haive agent persistence.

This script will:
1. Check Supabase connection
2. Run database migrations
3. Test the checkpointer
4. Provide next steps
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages/haive-dataflow/src"))
sys.path.insert(0, str(project_root / "packages/haive-core/src"))

from haive.dataflow.config.environment import get_supabase_server_config
from haive.dataflow.persistence.supabase_adapter import SupabasePersistence


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET"]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Show first and last 3 chars for security
            f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"

    if missing_vars:
        for var in missing_vars:
            pass
        return False

    return True


def check_supabase_connection():
    """Test connection to Supabase."""
    try:
        get_supabase_server_config()

        # Test persistence adapter
        SupabasePersistence()

        return True

    except Exception:
        return False


async def test_checkpointer():
    """Test the Supabase checkpointer functionality."""
    try:
        persistence = SupabasePersistence()

        # Test thread registration
        test_thread_id = "migration-test-thread"
        test_user_id = "migration-test-user"

        success = await persistence.register_thread(
            thread_id=test_thread_id,
            user_id=test_user_id,
            metadata={"test": True, "migration": True},
        )

        if success:
            pass
        else:
            return False

        return True

    except Exception:
        return False


def run_sql_migration():
    """Instructions for running SQL migration."""
    # Check if SQL file exists
    sql_file = project_root / "supabase_migration.sql"
    if sql_file.exists():
        pass
    else:
        pass

    input("\nPress Enter after running the SQL migration in Supabase...")


def show_configuration_example():
    """Show how to use the new Supabase configuration."""


def show_websocket_usage():
    """Show WebSocket configuration for Supabase."""


async def main():
    """Main migration function."""
    # Check environment
    if not check_environment():
        return False

    # Check connection
    if not check_supabase_connection():
        return False

    # Run SQL migration
    run_sql_migration()

    # Test checkpointer
    if not await test_checkpointer():
        return False

    # Show configuration examples
    show_configuration_example()
    show_websocket_usage()

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
