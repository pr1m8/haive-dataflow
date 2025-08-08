#!/usr/bin/env python3
"""Set up Supabase tables using the Supabase Python client."""

import contextlib
import os
import sys
from pathlib import Path

try:
    from supabase import Client, create_client
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
    from supabase import Client, create_client

# Add project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages/haive-dataflow/src"))


def create_supabase_client() -> Client:
    """Create Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

    return create_client(url, key)


def setup_tables():
    """Set up the agent state tables."""
    supabase = create_supabase_client()

    # SQL commands to create tables
    sql_commands = [
        # Create schema
        "CREATE SCHEMA IF NOT EXISTS agent_state;",
        # Create threads table
        """
        CREATE TABLE IF NOT EXISTS agent_state.threads (
            thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}',
            agent_name TEXT,
            agent_config JSONB DEFAULT '{}'
        );
        """,
        # Create checkpoints table
        """
        CREATE TABLE IF NOT EXISTS agent_state.checkpoints (
            thread_id UUID NOT NULL REFERENCES agent_state.threads(thread_id) ON DELETE CASCADE,
            checkpoint_ns TEXT NOT NULL DEFAULT '',
            checkpoint_id UUID NOT NULL,
            parent_checkpoint_id UUID,
            type TEXT,
            checkpoint JSONB NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
        );
        """,
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_threads_user_id ON agent_state.threads(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON agent_state.checkpoints(thread_id);",
        # Enable RLS
        "ALTER TABLE agent_state.threads ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE agent_state.checkpoints ENABLE ROW LEVEL SECURITY;",
    ]

    # RLS Policies
    rls_policies = [
        # Threads policies
        """
        CREATE POLICY IF NOT EXISTS "Users can view their own threads"
        ON agent_state.threads FOR SELECT
        USING (auth.uid() = user_id);
        """,
        """
        CREATE POLICY IF NOT EXISTS "Users can create their own threads"
        ON agent_state.threads FOR INSERT
        WITH CHECK (auth.uid() = user_id);
        """,
        """
        CREATE POLICY IF NOT EXISTS "Users can update their own threads"
        ON agent_state.threads FOR UPDATE
        USING (auth.uid() = user_id);
        """,
        # Checkpoints policies
        """
        CREATE POLICY IF NOT EXISTS "Users can view their own checkpoints"
        ON agent_state.checkpoints FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM agent_state.threads
                WHERE threads.thread_id = checkpoints.thread_id
                AND threads.user_id = auth.uid()
            )
        );
        """,
        """
        CREATE POLICY IF NOT EXISTS "Users can create checkpoints for their threads"
        ON agent_state.checkpoints FOR INSERT
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM agent_state.threads
                WHERE threads.thread_id = checkpoints.thread_id
                AND threads.user_id = auth.uid()
            )
        );
        """,
    ]

    try:
        # Execute table creation
        for _i, sql in enumerate(sql_commands):
            supabase.rpc("exec_sql", {"sql": sql})

        # Execute RLS policies
        for _i, policy in enumerate(rls_policies):
            with contextlib.suppress(Exception):
                supabase.rpc("exec_sql", {"sql": policy})

        return True

    except Exception:
        # Try a simpler approach - just test if we can query
        try:
            supabase.table("threads").select("*").limit(1).execute()
            return True
        except Exception:
            return False


def test_tables():
    """Test that tables are working."""
    try:
        supabase = create_supabase_client()

        # Test inserting a thread
        test_data = {
            "thread_id": "test-thread-123",
            "user_id": "b9284d47-72b5-4960-a177-0788fc4b0809",
            "metadata": {"test": True},
            "agent_name": "TestAgent",
        }

        # Try to insert
        result = supabase.table("agent_state.threads").insert(test_data).execute()

        if result.data:
            # Try to read it back
            read_result = (
                supabase.table("agent_state.threads")
                .select("*")
                .eq("thread_id", "test-thread-123")
                .execute()
            )

            if read_result.data:
                # Clean up
                supabase.table("agent_state.threads").delete().eq(
                    "thread_id", "test-thread-123"
                ).execute()

                return True

        return False

    except Exception:
        return False


def main():
    """Main function."""
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        return False

    # Set up tables
    if not setup_tables():
        return False

    # Test tables
    if not test_tables():
        pass

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
