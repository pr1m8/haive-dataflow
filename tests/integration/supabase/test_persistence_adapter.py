#!/usr/bin/env python3
"""Test the Supabase persistence adapter directly."""

import asyncio
import os
from datetime import datetime


async def test_persistence_adapter():
    """Test the Supabase persistence adapter."""

    print("🔧 Testing Supabase Persistence Adapter")
    print("=" * 50)

    # Check environment variables
    print("📋 Environment variables:")
    env_vars = [
        "SUPABASE_URL",
        "SUPABASE_DATABASE_URI",
        "SUPABASE_DATABASE_URI_SSL",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_JWT_SECRET",
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Show first and last few characters for security
            if len(value) > 20:
                displayed = f"{value[:10]}...{value[-6:]}"
            else:
                displayed = value[:15] + "..." if len(value) > 15 else value
            print(f"  ✓ {var}: {displayed}")
        else:
            print(f"  ❌ {var}: not set")

    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        # Create adapter
        persistence = SupabasePersistence()
        print("\n✓ Created SupabasePersistence adapter")

        # Show configuration
        print(f"✓ Postgres config created: {type(persistence.postgres_config)}")
        print(f"✓ Supabase config created: {type(persistence.supabase_config)}")

        # Test thread registration
        thread_id = f"adapter-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        user_id = "test-user-456"

        print("\n🧵 Testing thread registration..."..")
        print(f"  Thread ID: {thread_id}")
        print(f"  User ID: {user_id}")

        success = await persistence.register_thread(
            thread_id=thread_id,
            user_id=user_id,
            metadata={
                "test": True,
                "adapter": "supabase",
                "timestamp": datetime.now().isoformat(),
            },
        )

        if success:
            print("✓ Successfully registered thread via adapter"r")
        else:
            print("❌ Failed to register thread via adapter"r")
            return False

        # Test state update
        print("\n💾 Testing state update..."..")
        test_state = {
            "messages": [{"role": "user", "content": "Hello from persistence test"}],
            "step": 1,
            "timestamp": datetime.now().isoformat(),
            "test_data": {"key": "value", "number": 42},
        }

        update_success = await persistence.update_state(
            thread_id=thread_id,
            user_id=user_id,
            data=test_state,
            metadata={
                "source": "persistence_test",
                "timestamp": datetime.now().isoformat(),
            },
        )

        if update_success:
            print("✓ Successfully updated state via adapter"r")
        else:
            print("❌ Failed to update state via adapter"r")
            return False

        # Test state retrieval
        print("\n📥 Testing state retrieval..."..")
        retrieved_state = await persistence.get_state(
            thread_id=thread_id, user_id=user_id
        )

        if retrieved_state:
            print("✓ Successfully retrieved state via adapter"r")
            if isinstance(retrieved_state, dict):
                print(f"  State keys: {list(retrieved_state.keys())}")
                if "messages" in retrieved_state:
                    print(f"  Messages count: {len(retrieved_state['messages'])}")
            else:
                print(f"  State type: {type(retrieved_state)}")
        else:
            print("❌ Failed to retrieve state via adapter"r")
            return False

        print("\n🎉 Persistence adapter test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Persistence adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_checkpointer_factory():
    """Test the checkpointer factory functions."""

    print("\n🏭 Testing Checkpointer Factory")
    print("=" * 50)

    try:
        from haive.core.persistence.factory import acreate_postgres_checkpointer
        from haive.core.persistence.postgres_config import PostgresCheckpointerConfig

        # Create config using Supabase connection
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
            "SUPABASE_DATABASE_URI"
        )

        if not supabase_uri:
            print("❌ No Supabase connection string found")
            return False

        config = PostgresCheckpointerConfig(
            connection_string=supabase_uri, setup_needed=True
        )

        print("✓ Created PostgreSQL config for Supabase"e")
        print(f"  Connection string length: {len(supabase_uri)}")

        # Test creating checkpointer
        checkpointer = await acreate_postgres_checkpointer(config)
        print(f"✓ Created checkpointer: {type(checkpointer)}")

        # Check if it's a real PostgreSQL checkpointer or memory fallback
        from langgraph.checkpoint.memory import MemorySaver

        if isinstance(checkpointer, MemorySaver):
            print(
                "⚠️  Using MemorySaver fallback (PostgreSQL dependencies may be missing)"
            )
        else:
            print("✓ Using actual PostgreSQL checkpointer")

            # Check connection
            if hasattr(checkpointer, "conn"):
                print("✓ Checkpointer has connection pool")
            else:
                print("❌ Checkpointer missing connection pool")

        return True

    except Exception as e:
        print(f"❌ Checkpointer factory test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""

    print("🚀 Starting Persistence Adapter Tests")
    print("=" * 60)

    # Test 1: Checkpointer factory
    factory_success = await test_checkpointer_factory()

    if factory_success:
        # Test 2: Persistence adapter
        adapter_success = await test_persistence_adapter()

        if adapter_success:
            print("\n🎊 ALL TESTS PASSED!")
            print("The persistence system is configured correctly for Supabase.")
        else:
            print("\n⚠️  Factory works but adapter has issues")
    else:
        print("\n❌ Factory test failed - check PostgreSQL dependencies")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
