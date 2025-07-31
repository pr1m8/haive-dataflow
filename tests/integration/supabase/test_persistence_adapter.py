#!/usr/bin/env python3
"""Test the Supabase persistence adapter directly."""

import asyncio
import os
from datetime import datetime


async def test_persistence_adapter():
    """Test the Supabase persistence adapter."""
    # Check environment variables
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
                f"{value[:10]}...{value[-6:]}"
            else:
                value[:15] + "..." if len(value) > 15 else value
        else:
            pass

    try:
        from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

        # Create adapter
        persistence = SupabasePersistence()

        # Show configuration

        # Test thread registration
        thread_id = f"adapter-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        user_id = "test-user-456"

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
            pass
        else:
            return False

        # Test state update
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
            pass
        else:
            return False

        # Test state retrieval
        retrieved_state = await persistence.get_state(
            thread_id=thread_id, user_id=user_id
        )

        if retrieved_state:
            if isinstance(retrieved_state, dict):
                if "messages" in retrieved_state:
                    pass
            else:
                pass
        else:
            return False

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def test_checkpointer_factory():
    """Test the checkpointer factory functions."""
    try:
        from haive.core.persistence.factory import acreate_postgres_checkpointer
        from haive.core.persistence.postgres_config import PostgresCheckpointerConfig

        # Create config using Supabase connection
        supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
            "SUPABASE_DATABASE_URI"
        )

        if not supabase_uri:
            return False

        config = PostgresCheckpointerConfig(
            connection_string=supabase_uri, setup_needed=True
        )

        # Test creating checkpointer
        checkpointer = await acreate_postgres_checkpointer(config)

        # Check if it's a real PostgreSQL checkpointer or memory fallback
        from langgraph.checkpoint.memory import MemorySaver

        if isinstance(checkpointer, MemorySaver) or hasattr(checkpointer, "conn"):
            pass
        else:
            pass

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    # Test 1: Checkpointer factory
    factory_success = await test_checkpointer_factory()

    if factory_success:
        # Test 2: Persistence adapter
        adapter_success = await test_persistence_adapter()

        if adapter_success:
            pass
        else:
            pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
