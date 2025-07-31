#!/usr/bin/env python3
"""Test agent with Supabase persistence."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))
sys.path.insert(0, str(current_dir.parent.parent))

from haive.agents.simple.agent import SimpleAgent

from haive.dataflow.persistence.supabase_adapter import SupabasePersistence


async def test_agent_persistence():
    """Test agent with Supabase persistence."""
    # Create persistence adapter
    persistence = SupabasePersistence()

    # Get checkpointer
    checkpointer = await persistence.get_checkpointer()

    # Create unique thread ID
    thread_id = f"test-thread-{uuid4()}"
    user_id = "test-user-123"

    # Register thread
    await persistence.register_thread(
        thread_id=thread_id,
        user_id=user_id,
        metadata={"agent_name": "SimpleAgent", "test": True},
    )

    # Create agent with checkpointer
    agent = SimpleAgent()

    # Create execution context with checkpointer
    execution_context = {
        "configurable": {"thread_id": thread_id, "checkpointer": checkpointer}
    }

    # Send a message
    messages = [
        {
            "role": "user",
            "content": "Hello! Can you remember this: My favorite color is blue.",
        }
    ]

    response = await agent.run(messages=messages, stream=False, **execution_context)

    # Send another message to test memory
    messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": "What is my favorite color?"})

    await agent.run(messages=messages, stream=False, **execution_context)

    # Check if thread info is in database
    thread_info = await persistence.get_thread_info(thread_id, user_id)
    if thread_info:
        pass
    else:
        pass

    # Check state
    state = await persistence.get_state(thread_id, user_id)
    if state:
        pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(test_agent_persistence())
