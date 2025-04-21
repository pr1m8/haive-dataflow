"""Integration between Supabase authentication and Haive persistence layer.

This module provides a bridge between Supabase authentication and the Haive
core persistence layer, enabling user-thread association and ownership management.
"""

import logging
import os
import uuid
from typing import Any

from haive.dataflow.supabase import get_auth_manager

# Set up logging
logger = logging.getLogger(__name__)

# Import from haive-core if available
try:
    from haive_core.engine.agent.persistence.manager import PersistenceManager
    PERSISTENCE_AVAILABLE = True
except ImportError:
    logger.warning("Haive core PersistenceManager not available. Some functionality will be limited.")
    PERSISTENCE_AVAILABLE = False

class SupabasePersistenceIntegration:
    """Integrates Supabase authentication with Haive's persistence layer.
    
    This class serves as a bridge between Supabase authentication and
    the PersistenceManager from haive-core, enabling:
    
    1. Thread ownership management
    2. User-specific thread listing and filtering
    3. Permission-controlled thread access
    4. Authentication-aware persistence configuration
    """

    def __init__(self):
        """Initialize the integration."""
        self.auth_manager = get_auth_manager()

        # Initialize persistence manager if available
        self.persistence_manager = None
        if PERSISTENCE_AVAILABLE:
            try:
                # Initialize from standard PostgreSQL connection parameters
                db_config = {
                    "db_host": os.environ.get("POSTGRES_HOST", "localhost"),
                    "db_port": int(os.environ.get("POSTGRES_PORT", "5432")),
                    "db_name": os.environ.get("POSTGRES_DB", "postgres"),
                    "db_user": os.environ.get("POSTGRES_USER", "postgres"),
                    "db_pass": os.environ.get("POSTGRES_PASSWORD", "postgres"),
                    "ssl_mode": os.environ.get("POSTGRES_SSL_MODE", "prefer"),
                    "use_pool": os.environ.get("POSTGRES_USE_POOL", "true").lower() == "true",
                    "setup_needed": True  # Ensure tables are created if needed
                }

                self.persistence_manager = PersistenceManager.from_config(**db_config)
                logger.info("PersistenceManager initialized with PostgreSQL database")
            except Exception as e:
                logger.error(f"Failed to initialize PersistenceManager: {e}")

    def prepare_for_agent_run(
        self,
        thread_id: str | None = None,
        user_info: dict[str, Any] | None = None,
        **kwargs
    ) -> tuple[dict[str, Any], str]:
        """Prepare for an agent run with authentication context.
        
        Args:
            thread_id: Optional thread ID
            user_info: Optional user information from auth
            **kwargs: Additional runnable configuration
            
        Returns:
            Tuple of (RunnableConfig, current_thread_id)
        """
        if not PERSISTENCE_AVAILABLE or not self.persistence_manager:
            # Create a simple runnable config without persistence integration
            from langchain_core.runnables import RunnableConfig

            current_thread_id = thread_id or str(uuid.uuid4())
            config = RunnableConfig(
                configurable={
                    "thread_id": current_thread_id,
                    "auth_info": user_info or {}
                }
            )
            return config, current_thread_id

        # Format user_info for persistence manager
        auth_info = None
        if user_info:
            auth_info = {
                "supabase_user_id": user_info.get("id"),
                "email": user_info.get("email"),
                "username": user_info.get("metadata", {}).get("username"),
                "permissions": user_info.get("permissions", [])
            }

        # Use persistence manager
        return self.persistence_manager.prepare_for_agent_run(
            thread_id=thread_id,
            user_info=auth_info,
            **kwargs
        )

    def register_thread(self, thread_id: str, user_info: dict[str, Any] | None = None) -> bool:
        """Register a thread with user ownership.
        
        Args:
            thread_id: Thread ID to register
            user_info: Optional user information
            
        Returns:
            True if registration succeeded, False otherwise
        """
        if not PERSISTENCE_AVAILABLE or not self.persistence_manager:
            logger.warning("Thread registration not available - persistence manager not initialized")
            return False

        # Format user_info for persistence manager
        auth_info = None
        if user_info:
            auth_info = {
                "supabase_user_id": user_info.get("id"),
                "email": user_info.get("email"),
                "username": user_info.get("metadata", {}).get("username"),
                "permissions": user_info.get("permissions", [])
            }

        # Register thread
        return self.persistence_manager.register_thread(thread_id, auth_info)

    def list_user_threads(self, user_id: str, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """List threads owned by a user.
        
        Args:
            user_id: Supabase user ID
            limit: Maximum number of threads to return
            offset: Offset for pagination
            
        Returns:
            List of thread information dictionaries
        """
        if not PERSISTENCE_AVAILABLE or not self.persistence_manager:
            logger.warning("Thread listing not available - persistence manager not initialized")
            return []

        # List threads
        return self.persistence_manager.list_threads(user_id=user_id, limit=limit, offset=offset)

    def check_thread_ownership(self, thread_id: str, user_id: str) -> bool:
        """Check if a thread is owned by a user.
        
        Args:
            thread_id: Thread ID to check
            user_id: User ID to check ownership against
            
        Returns:
            True if thread is owned by user, False otherwise
        """
        if not PERSISTENCE_AVAILABLE or not self.persistence_manager:
            logger.warning("Thread ownership check not available - persistence manager not initialized")
            return False

        # Get thread information
        threads = self.persistence_manager.list_threads(thread_id=thread_id, limit=1)
        if not threads:
            return False

        # Check ownership
        thread_info = threads[0]
        return thread_info.get("user_id") == user_id

    def delete_thread(self, thread_id: str, user_id: str | None = None) -> bool:
        """Delete a thread, optionally checking ownership.
        
        Args:
            thread_id: Thread ID to delete
            user_id: Optional user ID to check ownership
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        if not PERSISTENCE_AVAILABLE or not self.persistence_manager:
            logger.warning("Thread deletion not available - persistence manager not initialized")
            return False

        # Check ownership if user_id provided
        if user_id and not self.check_thread_ownership(thread_id, user_id):
            logger.warning(f"User {user_id} does not own thread {thread_id}")
            return False

        # Delete thread
        return self.persistence_manager.delete_thread(thread_id)

    def get_user_context(self, user_info: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant user context for agent runs.
        
        Args:
            user_info: User information dictionary
            
        Returns:
            Dictionary with user context
        """
        # Extract user context
        context = {
            "user_id": user_info.get("id"),
            "email": user_info.get("email"),
            "username": user_info.get("metadata", {}).get("username", "User"),
            "permissions": user_info.get("permissions", []),
            "is_authenticated": True
        }

        # Add any other relevant context
        roles = user_info.get("app_metadata", {}).get("roles", [])
        if roles:
            context["roles"] = roles
            context["is_admin"] = "admin" in roles

        return context

# Singleton instance
_persistence_integration = None

def get_persistence_integration() -> SupabasePersistenceIntegration:
    """Get or create the persistence integration singleton."""
    global _persistence_integration
    if _persistence_integration is None:
        _persistence_integration = SupabasePersistenceIntegration()
    return _persistence_integration
