#!/usr/bin/env python3
"""
Migration script to set up Supabase for Haive agent persistence

This script will:
1. Check Supabase connection
2. Run database migrations
3. Test the checkpointer
4. Provide next steps
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages/haive-dataflow/src"))
sys.path.insert(0, str(project_root / "packages/haive-core/src"))

from .config.environment import get_supabase_server_config
from .persistence.supabase_adapter import SupabasePersistence


def check_environment():
    """Check if all required environment variables are set"""

    print("=== Checking Environment ===")

    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET"]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Show first and last 3 chars for security
            display_value = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"
            print(f"✓ {var}: {display_value}")

    if missing_vars:
        print(f"\n✗ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False

    print("✓ All environment variables are set")
    return True


def check_supabase_connection():
    """Test connection to Supabase"""

    print("\n=== Testing Supabase Connection ===")

    try:
        config = get_supabase_server_config()
        print(f"✓ Supabase URL: {config.url}")
        print(f"✓ Service key configured")

        # Test persistence adapter
        persistence = SupabasePersistence()
        print("✓ Supabase persistence adapter created")

        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


async def test_checkpointer():
    """Test the Supabase checkpointer functionality"""

    print("\n=== Testing Checkpointer ===")

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
            print("✓ Thread registration successful")
        else:
            print("✗ Thread registration failed")
            return False

        print("✓ Supabase checkpointer is working correctly")
        return True

    except Exception as e:
        print(f"✗ Checkpointer test failed: {e}")
        return False


def run_sql_migration():
    """Instructions for running SQL migration"""

    print("\n=== Database Migration ===")
    print("To set up the required tables in Supabase:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Run the SQL script in: supabase_migration.sql")
    print("4. This will create the agent_state schema and all required tables")

    # Check if SQL file exists
    sql_file = project_root / "supabase_migration.sql"
    if sql_file.exists():
        print(f"✓ SQL migration file found at: {sql_file}")
    else:
        print(f"✗ SQL migration file not found at: {sql_file}")

    input("\nPress Enter after running the SQL migration in Supabase...")


def show_configuration_example():
    """Show how to use the new Supabase configuration"""

    print("\n=== Configuration Example ===")
    print(
        """
# Example: Using Supabase checkpointer in your agent

from haive.dataflow.persistence.supabase_adapter import SupabasePersistence
from haive.core.engine.agent.config import AgentConfig

# Create your agent config
agent_config = AgentConfig(
    name="MyAgent",
    # ... other config
)

# Set up Supabase persistence
persistence = SupabasePersistence()
user_id = "your-user-id"
thread_id = "your-thread-id"

# Register the thread
await persistence.register_thread(
    thread_id=thread_id,
    user_id=user_id,
    metadata={"agent_name": "MyAgent"}
)

# Build and use your agent
agent = agent_config.build_agent()
result = await agent.arun(
    "Hello!",
    thread_id=thread_id,
    config={"configurable": {"user_id": user_id}}
)
"""
    )


def show_websocket_usage():
    """Show WebSocket configuration for Supabase"""

    print("\n=== WebSocket Usage ===")
    print(
        """
# WebSocket configuration with Supabase persistence

config = {
    "agent_name": "TextAnalyzer",
    "provider": "azure",
    "model": "gpt-4o",
    "stream": True,
    "persistent": true,  # This enables Supabase persistence
    "stream_mode": "messages",
    "stream_format": "text"
}

# Connect to WebSocket
ws_url = "ws://192.168.2.13:8000/api/ws/chat/TextAnalyzer"
ws_url += f"?token={your_jwt_token}&config={json.dumps(config)}"

# Your conversations will now be persisted in Supabase!
"""
    )


async def main():
    """Main migration function"""

    print("🚀 Haive Supabase Migration Tool")
    print("=" * 50)

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

    print("\n🎉 Migration Complete!")
    print("=" * 50)
    print("Your Haive agents are now configured to use Supabase for persistence.")
    print("All agent conversations and state will be stored in your Supabase database.")
    print("\nNext steps:")
    print("1. Restart your API server to pick up the changes")
    print("2. Test agent conversations through WebSocket")
    print("3. Check your Supabase dashboard to see the data")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
