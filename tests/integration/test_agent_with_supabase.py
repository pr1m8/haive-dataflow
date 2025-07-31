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
    print("Testing agent with Supabase persistence...")

    # Create persistence adapter
    persistence = SupabasePersistence()
    print("✓ Created persistence adapter")

    # Get checkpointer
    checkpointer = await persistence.get_checkpointer()
    print("✓ Got checkpointer")

    # Create unique thread ID
    thread_id = f"test-thread-{uuid4()}"
    user_id = "test-user-123"

    # Register thread
    print(f"\nRegistering thread: {thread_id}")
    success = await persistence.register_thread(
        thread_id=thread_id,
        user_id=user_id,
        metadata={"agent_name": "SimpleAgent", "test": True},
    )
    print(f"✓ Thread registered: {success}")

    # Create agent with checkpointer
    print("\nCreating SimpleAgent with checkpointer...")
    agent = SimpleAgent()

    # Create execution context with checkpointer
    execution_context = {
        "configurable": {"thread_id": thread_id, "checkpointer": checkpointer}
    }

    # Send a message
    print("\nSending message to agent...")
    messages = [
        {
            "role": "user",
            "content": "Hello! Can you remember this: My favorite color is blue.",
        }
    ]

    response = await agent.run(messages=messages, stream=False, **execution_context)

    print(f"Agent response: {response}")

    # Send another message to test memory
    print("\nSending follow-up message...")
    messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": "What is my favorite color?"})

    response2 = await agent.run(messages=messages, stream=False, **execution_context)

    print(f"Agent response 2: {response2}")

    # Check if thread info is in database
    print("\nChecking thread info in database...")
    thread_info = await persistence.get_thread_info(thread_id, user_id)
    if thread_info:
        print("✓ Thread found in database:")
        print(f"  ID: {thread_info['id']}")
        print(f"  User ID: {thread_info['user_id']}")
        print(f"  Agent: {thread_info['agent_name']}")
        print(f"  Metadata: {thread_info['metadata']}")
    else:
        print("✗ Thread not found in database")

    # Check state
    print("\nChecking persisted state...")
    state = await persistence.get_state(thread_id, user_id)
    if state:
        print("✓ State found in database")
        print(f"  State type: {type(state)}")
        print(
            f"  State keys: {list(state.keys()) if isinstance(state, dict) else 'N/A'}"
        )
    else:
        print("✗ State not found in database")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_agent_persistence())
