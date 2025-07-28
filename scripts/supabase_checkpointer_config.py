#!/usr/bin/env python3
"""
Supabase Checkpointer Configuration for Haive Agents

This module provides configuration and setup for using Supabase as the
checkpointer backend for Haive agents. It replaces local storage with
cloud-based persistence.
"""

import logging
import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .config.environment import get_supabase_server_config
from .engine.agent.config import AgentConfig
from .persistence.supabase_config import SupabaseSaver

logger = logging.getLogger(__name__)


class SupabaseCheckpointerConfig(BaseModel):
    """Configuration for Supabase-based agent checkpointing"""

    use_supabase: bool = Field(
        default=True, description="Enable Supabase checkpointing"
    )
    schema_name: str = Field(
        default="agent_state", description="Supabase schema for agent data"
    )
    table_prefix: str = Field(default="", description="Prefix for table names")
    enable_cleanup: bool = Field(
        default=True, description="Enable automatic cleanup of old checkpoints"
    )
    cleanup_days: int = Field(default=30, description="Days to keep checkpoints")
    batch_size: int = Field(default=100, description="Batch size for operations")


def create_supabase_checkpointer(user_id: str = None) -> SupabaseSaver:
    """Create a Supabase checkpointer instance"""

    # Get Supabase configuration
    supabase_config = get_supabase_server_config()

    # Create the checkpointer
    checkpointer = SupabaseSaver(
        supabase_url=supabase_config.url,
        supabase_key=supabase_config.service_role_key.get_secret_value(),
        user_id=user_id,
        initialize_schema=True,
    )

    logger.info(f"Created Supabase checkpointer for user: {user_id}")
    return checkpointer


def configure_agent_for_supabase(
    agent_config: AgentConfig, user_id: str, thread_id: str = None
) -> AgentConfig:
    """Configure an agent to use Supabase checkpointing"""

    # Create Supabase checkpointer
    checkpointer = create_supabase_checkpointer(user_id)

    # Set checkpointer on agent config
    agent_config.checkpointer = checkpointer
    agent_config.checkpoint_mode = "async"  # Use async mode for better performance

    # Add metadata about the configuration
    agent_config.metadata.update(
        {
            "persistence_backend": "supabase",
            "user_id": user_id,
            "configured_at": "2025-06-28T09:50:00Z",
        }
    )

    # Set thread configuration if provided
    if thread_id:
        agent_config.runnable_config = {
            "configurable": {"thread_id": thread_id, "user_id": user_id}
        }

    logger.info(f"Configured agent {agent_config.name} for Supabase persistence")
    return agent_config


# Migration utilities
class SupabaseMigrator:
    """Utility class for migrating existing agent data to Supabase"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.checkpointer = create_supabase_checkpointer(user_id)

    async def migrate_thread_data(
        self, thread_id: str, old_checkpoints: dict[str, Any]
    ):
        """Migrate checkpoint data from old storage to Supabase"""

        try:
            # Register thread in Supabase
            await self.checkpointer.aput_thread(
                thread_id=thread_id,
                metadata={
                    "migrated_from": "local_storage",
                    "migration_date": "2025-06-28",
                    "user_id": self.user_id,
                },
            )

            # Migrate checkpoints
            migrated_count = 0
            for checkpoint_id, checkpoint_data in old_checkpoints.items():
                await self.checkpointer.aput(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": checkpoint_id,
                        }
                    },
                    checkpoint=checkpoint_data,
                    metadata={},
                )
                migrated_count += 1

            logger.info(f"Migrated {migrated_count} checkpoints for thread {thread_id}")
            return migrated_count

        except Exception as e:
            logger.error(f"Error migrating thread {thread_id}: {e}")
            raise

    async def cleanup_old_data(self, confirm: bool = False):
        """Clean up old checkpoint data (use with caution)"""

        if not confirm:
            logger.warning("cleanup_old_data called without confirmation - skipping")
            return

        # This would implement cleanup of old local storage
        # Implementation depends on your current storage format
        logger.info("Old data cleanup would be implemented here")


# Example usage functions
def setup_supabase_for_agent(agent_name: str, user_id: str) -> dict[str, Any]:
    """Set up Supabase configuration for a specific agent"""

    config = {
        "checkpointer_type": "supabase",
        "checkpointer_config": {
            "user_id": user_id,
            "schema_name": "agent_state",
            "table_prefix": f"{agent_name}_",
        },
        "agent_metadata": {
            "persistence_backend": "supabase",
            "agent_name": agent_name,
            "user_id": user_id,
        },
    }

    return config


def get_supabase_connection_info():
    """Get Supabase connection information for debugging"""

    supabase_config = get_supabase_server_config()

    return {
        "url": supabase_config.url,
        "has_service_key": bool(supabase_config.service_role_key.get_secret_value()),
        "has_jwt_secret": bool(os.getenv("SUPABASE_JWT_SECRET")),
        "postgres_connection": supabase_config.postgres_connection,
    }


# Test function
async def test_supabase_checkpointer(user_id: str = "test-user"):
    """Test the Supabase checkpointer functionality"""

    print("=== Testing Supabase Checkpointer ===")

    try:
        # Create checkpointer
        checkpointer = create_supabase_checkpointer(user_id)
        print(f"✓ Created checkpointer for user: {user_id}")

        # Test thread registration
        thread_id = "test-thread-123"
        await checkpointer.aput_thread(
            thread_id=thread_id, metadata={"test": True, "created_by": "test_function"}
        )
        print(f"✓ Registered thread: {thread_id}")

        # Test checkpoint storage
        test_checkpoint = {
            "state": {"messages": ["Hello", "World"]},
            "config": {"temperature": 0.7},
        }

        await checkpointer.aput(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": "test-checkpoint-1",
                }
            },
            checkpoint=test_checkpoint,
            metadata={"test": True},
        )
        print(f"✓ Stored test checkpoint")

        # Test checkpoint retrieval
        retrieved = await checkpointer.aget(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": "test-checkpoint-1",
                }
            }
        )

        if retrieved:
            print(f"✓ Retrieved checkpoint successfully")
        else:
            print(f"✗ Failed to retrieve checkpoint")

        print("=== Supabase Checkpointer Test Complete ===")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    # Test the configuration
    print("Supabase connection info:", get_supabase_connection_info())

    # Run test
    asyncio.run(test_supabase_checkpointer())
