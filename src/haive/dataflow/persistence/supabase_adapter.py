# haive_dataflow/persistence/supabase_adapter.py
from typing import Optional, Dict, Any, Union
import logging
from contextlib import asynccontextmanager

from haive.dataflow.config.environment import get_postgres_config, get_supabase_server_config
from haive.core.persistence.postgres_config import PostgresCheckpointerConfig
from haive.core.persistence.factory import (
    acreate_postgres_checkpointer, aregister_postgres_thread,
    aget_postgres_checkpoint, aput_postgres_checkpoint
)

logger = logging.getLogger(__name__)

class SupabasePersistence:
    """Adapter for PostgreSQL persistence with Supabase RLS support."""
    
    def __init__(self):
        """Initialize the persistence adapter."""
        # Get configurations
        self.postgres_config = get_postgres_config()
        self.supabase_config = get_supabase_server_config()
        
    @asynccontextmanager
    async def rls_context(self, connection, user_id: str):
        """Set RLS context for the duration of an operation."""
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
                logger.error(f"Error clearing RLS context: {e}")
    
    async def register_thread(
        self, 
        thread_id: str, 
        user_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a thread with user ownership.
        
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
        metadata['user_id'] = user_id
        
        # Create checkpointer
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)
        
        # Register using the existing function
        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Register thread
                    success = await aregister_postgres_thread(checkpointer, thread_id, metadata)
                    
                    # Explicitly set user_id in the threads table
                    async with conn.cursor() as cursor:
                        await cursor.execute(
                            "UPDATE threads SET user_id = %s WHERE thread_id = %s",
                            (user_id, thread_id)
                        )
                        
            return success
        except Exception as e:
            logger.error(f"Error registering thread: {e}")
            return False
    
    async def get_state(self, thread_id: str, user_id: str) -> Optional[Any]:
        """
        Get conversation state with RLS enforcement.
        
        Args:
            thread_id: Thread ID
            user_id: User ID for RLS enforcement
            
        Returns:
            State data if found and accessible, None otherwise
        """
        # Create checkpointer
        checkpointer = await acreate_postgres_checkpointer(self.postgres_config)
        
        # Config with thread_id
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context 
                async with self.rls_context(conn, user_id):
                    # Get checkpoint data
                    state = await aget_postgres_checkpoint(self.postgres_config, config)
                    return state
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return None
    
    async def update_state(
        self, 
        thread_id: str, 
        user_id: str, 
        data: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update conversation state with RLS enforcement.
        
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
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        try:
            # Get connection
            async with checkpointer.conn.connection() as conn:
                # Set RLS context
                async with self.rls_context(conn, user_id):
                    # Store checkpoint
                    metadata = metadata or {}
                    metadata["user_id"] = user_id
                    
                    result = await aput_postgres_checkpoint(self.postgres_config, config, data, metadata)
                    return bool(result)
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False