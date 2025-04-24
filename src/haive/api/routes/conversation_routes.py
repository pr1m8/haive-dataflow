# haive_dataflow/api/routes/conversation_routes.py
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from datetime import datetime
from decimal import Decimal

from haive.dataflow.auth.dependencies import require_auth
from haive.dataflow.auth.credits import CreditsManager, UsageRecord
from haive.dataflow.persistence.conversations import ConversationManager
from haive.dataflow.config.settings import get_settings

# Try importing from your registry
try:
    from haive.dataflow.registry import AgentRegistry
except ImportError:
    # Mock registry for testing
    class AgentRegistry:
        @staticmethod
        async def get_agent(agent_id: str):
            return None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["Conversations"])
credits_manager = CreditsManager()
conversation_manager = ConversationManager()
settings = get_settings()

@router.get("/")
async def list_conversations(
    user_id: str = Depends(require_auth),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List conversations for the current user."""
    conversations = await conversation_manager.list_conversations(
        user_id, 
        limit=limit, 
        offset=offset
    )
    
    return {
        "conversations": conversations,
        "total": len(conversations),  # This would be more efficient with a count query
        "offset": offset,
        "limit": limit
    }

@router.get("/{thread_id}")
async def get_conversation(
    thread_id: str,
    user_id: str = Depends(require_auth)
):
    """Get conversation details and state."""
    conversation = await conversation_manager.get_conversation(thread_id, user_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    return conversation

@router.post("/{thread_id}/messages")
async def add_message(
    thread_id: str,
    message: Dict[str, Any],
    user_id: str = Depends(require_auth)
):
    """Add a message to a conversation and get a response."""
    # Get conversation details
    conversation = await conversation_manager.get_conversation(thread_id, user_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Extract agent_id from conversation
    agent_id = conversation.get("agent_id")
    
    # Load the agent
    agent = await AgentRegistry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check credits
    has_credits = await credits_manager.check_credits(user_id)
    if not has_credits:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Get current state
    state = conversation.get("state", {})
    
    # Add user message to state
    if isinstance(state, dict):
        from langchain_core.messages import HumanMessage
        
        if "messages" not in state:
            state["messages"] = []
            
        if isinstance(message, str):
            state["messages"].append(HumanMessage(content=message))
        elif isinstance(message, dict) and "content" in message:
            state["messages"].append(HumanMessage(content=message["content"]))
    
    # Create runnable config
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    # Process message with agent
    result = await agent.ainvoke(state, config)
    
    # Update conversation state
    from haive.dataflow.persistence.supabase_adapter import SupabasePersistence
    persistence = SupabasePersistence()
    await persistence.update_state(thread_id, user_id, result)
    
    # Get token usage from result if available
    token_count = 0
    if isinstance(result, dict) and "token_usage" in result:
        token_count = result["token_usage"].get("total_tokens", 0)
    
    # Calculate cost based on token usage
    cost_per_1k = settings.agent.credit_cost_per_1k_tokens
    cost = Decimal(token_count) / 1000 * Decimal(cost_per_1k)
    
    # Log usage and deduct credits
    await credits_manager.deduct_credits(user_id, float(cost))
    await credits_manager.log_usage(
        UsageRecord(
            agent_id=agent_id,
            user_id=user_id,
            conversation_id=thread_id,
            token_count=token_count,
            cost=cost,
            created_at=datetime.now()
        )
    )
    
    return result