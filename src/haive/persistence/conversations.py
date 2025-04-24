# haive_dataflow/persistence/conversations.py
from typing import Optional, Dict, Any, List
import logging
import uuid
import datetime
from pydantic import BaseModel

from supabase import create_client
from haive.dataflow.config.environment import get_supabase_server_config
from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

logger = logging.getLogger(__name__)

class ConversationMetadata(BaseModel):
    """Metadata for a conversation."""
    agent_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_data: Optional[Dict[str, Any]] = None

class ConversationManager:
    """Manager for conversations with LangGraph integration."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.supabase_config = get_supabase_server_config()
        self.persistence = SupabasePersistence()
        self._client = None
        
    @property
    def client(self):
        """Lazy-loaded Supabase admin client."""
        if self._client is None:
            self._client = create_client(
                self.supabase_config.url, 
                self.supabase_config.service_role_key.get_secret_value()
            )
        return self._client
    
    async def create_conversation(
        self, 
        user_id: str, 
        metadata: ConversationMetadata
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new conversation.
        
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
            response = await self.client.from_("user_data.conversations") \
                .insert({
                    "id": conversation_id,
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "agent_id": metadata.agent_id,
                    "title": metadata.title or f"Conversation {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat()
                }) \
                .execute()
                
            if not response.data:
                logger.error("Failed to create conversation record")
                return None
                
            # Register LangGraph thread
            thread_metadata = {
                "conversation_id": conversation_id,
                "agent_id": metadata.agent_id
            }
            
            # Add custom metadata if provided
            if metadata.custom_data:
                thread_metadata.update(metadata.custom_data)
                
            # Register thread
            success = await self.persistence.register_thread(thread_id, user_id, thread_metadata)
            
            if not success:
                logger.error(f"Failed to register thread: {thread_id}")
                # Rollback conversation
                await self.client.from_("user_data.conversations") \
                    .delete() \
                    .eq("id", conversation_id) \
                    .execute()
                return None
                
            return {
                "conversation_id": conversation_id,
                "thread_id": thread_id,
                "title": metadata.title,
                "agent_id": metadata.agent_id
            }
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    async def get_conversation(
        self, 
        thread_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation details.
        
        Args:
            thread_id: Thread ID
            user_id: User ID
            
        Returns:
            Conversation details if found, None otherwise
        """
        try:
            # Get conversation record
            response = await self.client.from_("user_data.conversations") \
                .select("*") \
                .eq("thread_id", thread_id) \
                .eq("user_id", user_id) \
                .limit(1) \
                .execute()
                
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
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List conversations for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        try:
            # Get conversations
            response = await self.client.from_("user_data.conversations") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("updated_at", options={"ascending": False}) \
                .range(offset, offset + limit - 1) \
                .execute()
                
            if not response.data:
                return []
                
            return response.data
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []