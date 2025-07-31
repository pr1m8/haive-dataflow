"""Supabase persistence adapter for the Haive framework.

This module provides an adapter for persisting data to Supabase's PostgreSQL
database. It handles the connection management, Row-Level Security (RLS)
context, and provides methods for storing and retrieving data.

The adapter integrates with Haive's core persistence system, specifically
the PostgreSQL checkpointer, to provide a consistent interface for data
storage and retrieval while respecting Supabase's security model.

Key features:
- RLS context management for proper access control
- Connection pooling and management
- Checkpointing for LangGraph state persistence
- Thread registration for conversation tracking

Typical usage example:

    ```python
    from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

    # Create the persistence adapter
    persistence = SupabasePersistence()

    # Register a thread
    thread_id = await persistence.register_thread(
        user_id="user-123",
        metadata={"agent_id": "agent-456"}
    )

    # Store a checkpoint
    await persistence.store_checkpoint(
        thread_id=thread_id,
        checkpoint_id="checkpoint-1",
        state={"key": "value"},
        user_id="user-123"
    )

    # Retrieve a checkpoint
    checkpoint = await persistence.get_checkpoint(
        thread_id=thread_id,
        checkpoint_id="checkpoint-1",
        user_id="user-123"
    )
    ```
"""

import json
import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Any

from haive.core.persistence.postgres_config import PostgresCheckpointerConfig

from haive.dataflow.config.environment import get_supabase_server_config

from .persistence.factory import (
    acreate_postgres_checkpointer,
    aget_postgres_checkpoint,
    aput_postgres_checkpoint,
    aregister_postgres_thread,
)

logger = logging.getLogger(__name__)


class SupabasePersistence:
    """Adapter for PostgreSQL persistence with Supabase RLS support.

    This class provides an adapter for persisting data to Supabase's PostgreSQL
    database with proper Row-Level Security (RLS) context management. It handles
    the complexities of setting the RLS context for database operations while
    providing a simple interface for storing and retrieving data.

    The adapter is designed to work with Haive's core persistence system,
    particularly the PostgreSQL checkpointer for LangGraph state persistence.

    Attributes:
        postgres_config: Configuration for PostgreSQL connection
        supabase_config: Configuration for Supabase connection
    """

    def __init__(self):
        """Initialize the persistence adapter.

        Loads the PostgreSQL and Supabase configurations from
        environment variables and prepares the adapter for use.
        """
        # Get configurations
        self.supabase_config = get_supabase_server_config()

        # Create Supabase-compatible PostgreSQL config using Supabase connection
        self.postgres_config = self._create_supabase_postgres_config()

    def _create_supabase_postgres_config(self):
        """Create PostgreSQL config that connects to Supabase instead of
        localhost.
        """
        # Use Supabase connection string from environment - check multiple possible env vars
        # Priority: Use the zkssazqhwcetsnbiuqik instance where we ran the migration
        # First try to get from .env file directly to avoid env var override

        env_path = os.path.join(os.path.dirname(__file__), "../../../../../../.env")
        supabase_uri = None

        if os.path.exists(env_path):
            with open(env_path) as f:
                content = f.read()
                # Look for SUPABASE_POSTGRES_CONNECTION with the actual password
                match = re.search(r"SUPABASE_POSTGRES_CONNECTION=([^\n]+)", content)
                if match:
                    uri = match.group(1).strip()
                    if "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" in uri:
                        supabase_uri = uri

        if not supabase_uri:
            # Fall back to env vars
            supabase_uri = os.getenv(
                "SUPABASE_DATABASE_URI"
            )  # This one has the actual password

            if not supabase_uri or "[" in supabase_uri:
                # Fall back to others if first one is not good
                supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
                    "SUPABASE_POSTGRES_CONNECTION"
                )

        if supabase_uri:
            # Use direct connection string
            return PostgresCheckpointerConfig(
                connection_string=supabase_uri, setup_needed=True
            )
        # Fall back to individual parameters (if needed)
        return PostgresCheckpointerConfig(
            db_host=os.getenv("SUPABASE_HOST", "localhost"),
            db_port=int(os.getenv("SUPABASE_PORT", "6543")),
            db_name=os.getenv("SUPABASE_DBNAME", "postgres"),
            db_user=os.getenv("SUPABASE_USER", "postgres"),
            db_pass=os.getenv("SUPABASE_PASSWORD", ""),
            ssl_mode="require",
            setup_needed=True,
        )

    @asynccontextmanager
    async def rls_context(self, connection, user_id: str):
        """Set RLS context for the duration of an operation.

        This async context manager sets the Row-Level Security (RLS) context
        for a database connection, allowing operations to be performed with
        the security context of a specific user. It ensures that the context
        is properly cleared after the operation completes, even if an exception
        occurs.

        Args:
            connection: The PostgreSQL database connection
            user_id: The ID of the user to set as the RLS context

        Yields:
            None: Control is yielded back to the caller with the RLS context set

        Example:
            ```python
            async with persistence.rls_context(connection, "user-123"):
                # Operations here will be performed with the RLS context of user-123
                await connection.execute("SELECT * FROM protected_table")
            # RLS context is cleared after the block exits
            ```
        """
        if not connection:
            yield
            return

        try:
            # Set RLS context
            async with connection.cursor() as cursor:
                await cursor.execute(f"SET LOCAL auth.uid = '{user_id}'")

            # Yield control back
            yield
        finally:
            # Clear RLS context
            try:
                async with connection.cursor() as cursor:
                    await cursor.execute("RESET auth.uid")
            except Exception as e:
                logger.exception(f"Error clearing RLS context: {e}")

    async def register_thread(
        self, thread_id: str, user_id: str, metadata: dict[str, Any] | None = None
    ) -> bool:
        """Register a thread with user ownership.

        Args:
            thread_id: Thread ID
            user_id: User ID for ownership
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        if metadata is None:
            metadata = {}

        # Add user_id to metadata
        metadata["user_id"] = user_id

        # Create checkpointer
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

        # Register using the existing function
        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Register thread
                    success = await aregister_postgres_thread(
                        checkpointer, thread_id, metadata
                    )

                    # Register thread in public.threads table with proper UUID structure
                    async with conn.cursor() as cursor:
                        # Insert/update thread using proper id structure
                        await cursor.execute(
                            """
                            INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, NOW(), NOW())
                            ON CONFLICT (id) DO UPDATE SET
                                user_id = EXCLUDED.user_id,
                                agent_name = EXCLUDED.agent_name,
                                metadata = EXCLUDED.metadata,
                                updated_at = NOW()
                        """,
                            (
                                thread_id,
                                user_id,
                                metadata.get("agent_name", "Unknown"),
                                json.dumps(metadata),
                            ),
                        )

            return success
        except Exception as e:
            logger.exception(f"Error registering thread: {e}")
            return False

    async def get_state(self, thread_id: str, user_id: str) -> Any | None:
        """Get conversation state with RLS enforcement.

        Args:
            thread_id: Thread ID
            user_id: User ID for RLS enforcement

        Returns:
            State data if found and accessible, None otherwise
        """
        # Create checkpointer
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

        # Config with thread_id
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Get checkpoint data
                    state = await aget_postgres_checkpoint(self.postgres_config, config)
                    return state
        except Exception as e:
            logger.exception(f"Error getting state: {e}")
            return None

    async def update_state(
        self,
        thread_id: str,
        user_id: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update conversation state with RLS enforcement.

        Args:
            thread_id: Thread ID
            user_id: User ID for RLS enforcement
            data: State data to store
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        # Create checkpointer
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

        # Config with thread_id
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Store checkpoint
                    metadata = metadata or {}
                    metadata["user_id"] = user_id

                    result = await aput_postgres_checkpoint(
                        self.postgres_config, config, data, metadata
                    )
                    return bool(result)
        except Exception as e:
            logger.exception(f"Error updating state: {e}")
            return False

    async def get_thread_info(
        self,
        thread_id: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        """Get thread information from the public.threads table.

        Args:
            thread_id: Thread ID
            user_id: User ID for RLS enforcement

        Returns:
            Thread information dictionary or None if not found
        """
        # Create checkpointer to get connection
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Get thread info
                    async with conn.cursor() as cursor:
                        await cursor.execute(
                            """
                            SELECT id, user_id, agent_name, metadata, created_at, updated_at
                            FROM public.threads
                            WHERE id = %s
                        """,
                            (thread_id,),
                        )

                        row = await cursor.fetchone()
                        if row:
                            return {
                                "id": row[0],
                                "user_id": row[1],
                                "agent_name": row[2],
                                "metadata": json.loads(row[3]) if row[3] else {},
                                "created_at": row[4],
                                "updated_at": row[5],
                            }
                        return None

        except Exception as e:
            logger.exception(f"Error getting thread info: {e}")
            return None

    async def get_checkpointer(self):
        """Get a PostgreSQL checkpointer configured for Supabase.

        This method returns a checkpointer that can be passed to an agent's
        configuration to enable state persistence.

        Returns:
            PostgresSaver: A configured PostgreSQL checkpointer

        Example:
            ```python
            persistence = SupabasePersistence()
            checkpointer = await persistence.get_checkpointer()

            # Pass to agent config
            agent_config.runnable_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpointer": checkpointer
                }
            }
            ```
        """
        return await acreate_postgres_checkpointer(self.postgres_config)

    async def get_user_threads(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get all threads for a user from the public.threads table.

        Args:
            user_id: User ID for RLS enforcement
            limit: Maximum number of threads to return

        Returns:
            List of thread dictionaries
        """
        # Create checkpointer to get connection
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Get user threads
                    async with conn.cursor() as cursor:
                        await cursor.execute(
                            """
                            SELECT id, agent_name, name, metadata, created_at, updated_at
                            FROM public.threads
                            WHERE user_id = %s
                            ORDER BY updated_at DESC
                            LIMIT %s
                        """,
                            (user_id, limit),
                        )

                        rows = await cursor.fetchall()
                        return [
                            {
                                "id": row[0],
                                "agent_name": row[1],
                                "name": row[2],
                                "metadata": json.loads(row[3]) if row[3] else {},
                                "created_at": row[4],
                                "updated_at": row[5],
                            }
                            for row in rows
                        ]

        except Exception as e:
            logger.exception(f"Error getting user threads: {e}")
            return []
