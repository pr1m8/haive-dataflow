# haive/dataflow/conversations/manager.py
import datetime
import logging
import uuid
from typing import Any

from pydantic import BaseModel

from haive.dataflow.config import SupabaseServerConfig

from .persistence.factory import (
    acreate_postgres_checkpointer,
    aget_postgres_checkpoint,
    aput_postgres_checkpoint,
    aregister_postgres_thread,
)
from .persistence.postgres_config import PostgresCheckpointerConfig

logger = logging.getLogger(__name__)


class ConversationMetadata(BaseModel):
    """Metadata for a conversation."""

    agent_id: str
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    custom_data: dict[str, Any] | None = None


class ConversationManager:
    """Manager for conversations with LangGraph integration (backend only)."""

    def __init__(
        self,
        server_config: SupabaseServerConfig | None = None,
        postgres_config: PostgresCheckpointerConfig | None = None,
    ):
        """Initialize with server-side configs."""
        self.server_config = server_config or SupabaseServerConfig()
        self.postgres_config = postgres_config or PostgresCheckpointerConfig.from_env()
        self._client = None

    @property
    def client(self):
        """Lazy-loaded Supabase admin client."""
        if self._client is None:
            from supabase import create_client

            self._client = create_client(
                self.server_config.url,
                self.server_config.service_role_key.get_secret_value(),
            )
        return self._client

    async def create_conversation(
        self, user_id: str, metadata: ConversationMetadata
    ) -> dict[str, Any] | None:
        """Create a new conversation (backend only)."""
        try:
            # Generate UUIDs
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
            checkpointer = await acreate_postgres_checkpointer(self.postgres_config)

            # Register using the factory function
            thread_metadata = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "agent_id": metadata.agent_id,
            }

            # Add custom metadata if provided
            if metadata.custom_data:
                thread_metadata.update(metadata.custom_data)

            # Register thread
            success = await aregister_postgres_thread(
                checkpointer, thread_id, thread_metadata
            )

            if not success:
                logger.error(f"Failed to register LangGraph thread: {thread_id}")
                # Try to rollback conversation
                await self.client.from_("user_data.conversations").delete().eq(
                    "id", conversation_id
                ).execute()
                return None

            return {
                "conversation_id": conversation_id,
                "thread_id": thread_id,
                "title": metadata.title,
            }
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    async def get_conversation_state(
        self, thread_id: str, user_id: str
    ) -> dict[str, Any] | None:
        """Get conversation state from LangGraph checkpoints (backend only)."""
        try:
            # Verify ownership first
            response = (
                await self.client.from_("user_data.conversations")
                .select("id")
                .eq("thread_id", thread_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if not response.data:
                logger.warning(
                    f"User {user_id} attempted to access unauthorized thread: {thread_id}"
                )
                return None

            # Get checkpoint data
            config = {"configurable": {"thread_id": thread_id}}

            state = await aget_postgres_checkpoint(self.postgres_config, config)
            return state
        except Exception as e:
            logger.error(f"Error getting conversation state: {e}")
            return None

    async def update_conversation_state(
        self,
        thread_id: str,
        user_id: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update conversation state (backend only)."""
        try:
            # Verify ownership first
            response = (
                await self.client.from_("user_data.conversations")
                .select("id")
                .eq("thread_id", thread_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if not response.data:
                logger.warning(
                    f"User {user_id} attempted to update unauthorized thread: {thread_id}"
                )
                return False

            # Get conversation ID for metadata
            conversation_id = response.data[0]["id"]

            # Update last_access in conversations
            await self.client.from_("user_data.conversations").update(
                {"updated_at": datetime.datetime.now().isoformat()}
            ).eq("id", conversation_id).execute()

            # Store checkpoint
            config = {"configurable": {"thread_id": thread_id}}

            # Add user_id and conversation_id to metadata
            if metadata is None:
                metadata = {}

            metadata["user_id"] = user_id
            metadata["conversation_id"] = conversation_id

            # Store checkpoint
            result = await aput_postgres_checkpoint(
                self.postgres_config, config, data, metadata
            )
            return bool(result)
        except Exception as e:
            logger.error(f"Error updating conversation state: {e}")
            return False
