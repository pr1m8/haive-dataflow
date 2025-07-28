"""Conversation persistence for the Haive framework.

This module provides functionality for persisting and retrieving conversations
between users and agents. It includes classes for managing conversation metadata,
messages, and the overall conversation lifecycle.

The conversation system uses Supabase as the storage backend, providing
reliable persistence with proper authentication and access control. It supports
operations like creating conversations, adding messages, retrieving history,
and deleting conversations.

Typical usage example:

    ```python
    from haive.dataflow.persistence.conversations import ConversationManager, ConversationMetadata

    # Create a conversation manager
    manager = ConversationManager()

    # Create a new conversation
    conversation_id = await manager.create_conversation(
        user_id="user-123",
        metadata=ConversationMetadata(
            agent_id="agent-456",
            title="Technical Support",
            tags=["support", "technical"]
        )
    )

    # Add messages to the conversation
    await manager.add_message(
        conversation_id=conversation_id,
        content="How do I reset my pass
        role="user",
        user_id="user-123"
    )

    # Get conversation messages
    messages = await manager.get_messages(conversation_id)
    ```
"""

import datetime
import logging
import uuid
from typing import Any

from pydantic import BaseModel
from supabase import create_client

from .config.environment import get_supabase_server_config
from .persistence.supabase_adapter import SupabasePersistence

logger = logging.getLogger(__name__)


class ConversationMetadata(BaseModel):
    """Metadata for a conversation.

    This model defines the metadata associated with a conversation, including
    the agent used, title, description, and custom data. It provides a
    structured way to store and retrieve conversation context.

    Attributes:
        agent_id: ID of the agent associated with the conversation
        title: Optional title for the conversation
        description: Optional detailed description of the conversation
        tags: Optional list of tags for categorizing the conversation
        custom_data: Optional dictionary of additional custom data

    Example:
        >>> metadata = ConversationMetadata(
        ...     agent_id="agent-123",
        ...     title="Customer Support",
        ...     tags=["support", "billing"],
        ...     custom_data={"priority": "high"}
        ... )
    """

    agent_id: str
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    custom_data: dict[str, Any] | None = None


class ConversationManager:
    """Manager for conversations with LangGraph integration.

    This class provides methods for creating, retrieving, updating, and deleting
    conversations and their messages. It integrates with LangGraph for storing
    agent state and conversation history, and uses Supabase as the persistence
    backend.

    The conversation manager handles:
    - Creating and retrieving conversations
    - Adding and retrieving messages
    - Managing conversation metadata
    - Integrating with LangGraph for state persistence
    - Enforcing access control

    Attributes:
        supabase_config: Configuration for the Supabase connection
        persistence: Adapter for Supabase persistence
        _client: Lazy-loaded Supabase client instance
    """

    def __init__(self):
        """Initialize the conversation manager.

        Sets up the Supabase configuration and persistence adapter.
        The actual Supabase client is lazy-loaded when first needed.
        """
        self.supabase_config = get_supabase_server_config()
        self.persistence = SupabasePersistence()
        self._client = None

    @property
    def client(self):
        """Lazy-loaded Supabase admin client.

        This property provides access to the Supabase client, initializing it
        on first access if needed. It uses the service role key to ensure
        administrative access to the database.

        Returns:
            The initialized Supabase client instance

        Note:
            This uses the service role key, which has elevated privileges.
            Use with caution and ensure proper access control.
        """
        if self._client is None:
            self._client = create_client(
                self.supabase_config.url,
                self.supabase_config.service_role_key.get_secret_value(),
            )
        return self._client

    async def create_conversation(
        self, user_id: str, metadata: ConversationMetadata
    ) -> dict[str, Any] | None:
        """Create a new conversation.

        Args:
            user_id: User ID
            metadata: Conversation metadata

        Returns:
            Conversation details if created successfully, None otherwise
        """
        try:
            # Generate IDs
            conversation_id = str(uuid.uuid4())
            thread_id = f"thread-{uuid.uuid4()}"

            # Create conversation record
            response = (
                await self.client.from_("user_data.conversations")
                .insert(
                    {
                        "id": conversation_id,
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "agent_id": metadata.agent_id,
                        "title": metadata.title
                        or f"Conversation {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "created_at": datetime.datetime.now().isoformat(),
                        "updated_at": datetime.datetime.now().isoformat(),
                    }
                )
                .execute()
            )

            if not response.data:
                logger.error("Failed to create conversation record")
                return None

            # Register LangGraph thread
            thread_metadata = {
                "conversation_id": conversation_id,
                "agent_id": metadata.agent_id,
            }

            # Add custom metadata if provided
            if metadata.custom_data:
                thread_metadata.update(metadata.custom_data)

            # Register thread
            success = await self.persistence.register_thread(
                thread_id, user_id, thread_metadata
            )

            if not success:
                logger.error(f"Failed to register thread: {thread_id}")
                # Rollback conversation
                await self.client.from_("user_data.conversations").delete().eq(
                    "id", conversation_id
                ).execute()
                return None

            return {
                "conversation_id": conversation_id,
                "thread_id": thread_id,
                "title": metadata.title,
                "agent_id": metadata.agent_id,
            }
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    async def get_conversation(
        self, thread_id: str, user_id: str
    ) -> dict[str, Any] | None:
        """Get conversation details.

        Args:
            thread_id: Thread ID
            user_id: User ID

        Returns:
            Conversation details if found, None otherwise
        """
        try:
            # Get conversation record
            response = (
                await self.client.from_("user_data.conversations")
                .select("*")
                .eq("thread_id", thread_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if not response.data:
                return None

            # Get conversation state
            state = await self.persistence.get_state(thread_id, user_id)

            # Return conversation details with state
            conversation = response.data[0]
            conversation["state"] = state or {}

            return conversation
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    async def list_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List conversations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Offset for pagination

        Returns:
            List of conversations
        """
        try:
            # Get conversations
            response = (
                await self.client.from_("user_data.conversations")
                .select("*")
                .eq("user_id", user_id)
                .order("updated_at", options={"ascending": False})
                .range(offset, offset + limit - 1)
                .execute()
            )

            if not response.data:
                return []

            return response.data
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []
