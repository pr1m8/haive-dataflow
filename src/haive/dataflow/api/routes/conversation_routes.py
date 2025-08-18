"""Conversation management API routes.

This module provides FastAPI routes for managing conversations between users
and agents. It supports operations like creating, listing, retrieving, and
deleting conversations, as well as adding messages to existing conversations.

The conversation system provides persistence for chat history, enabling
users to continue conversations across sessions. It also includes integration
with the credits system for tracking usage and enforcing limits.

Key features:
- Conversation CRUD operations
- Message management
- Usage tracking and credits
- Pagination for conversation listing
- Agent integration

Typical usage example:

            # Client-side code to create and use a conversation
            import requests

            # Create a new conversation
            response = requests.post(
                "http://localhost:8000/api/conversations",
                json={
                    "title": "My Conversation",
                    "agent_id": "agent-123",
                    "metadata": {"topic": "AI Ethics"}
                },
                headers={"Authorization": "Bearer YOUR_TOKEN"}
            )

            conversation_id = response.json()["id"]

            # Add a message to the conversation
            response = requests.post(
                f"http://localhost:8000/api/conversations/{conversation_id}/messages",
                json={
                    "content": "Tell me about AI ethics",
                    "role": "user"
                },
                headers={"Authorization": "Bearer YOUR_TOKEN"}
            )
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from haive.core.registry import AgentRegistry
from langchain_core.messages import HumanMessage

from haive.dataflow.api.routes.auth.credits import CreditsManager, UsageRecord
from haive.dataflow.api.routes.auth.dependencies import require_auth
from haive.dataflow.api.routes.config.settings import get_settings
from haive.dataflow.api.routes.persistence.conversations import ConversationManager
from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

# Try importing from your registry
try:
    from haive.dataflow.registry import AgentRegistry
except ImportError:
    # Mock registry for testing
    class AgentRegistry:
        @staticmethod
        async def get_agent(agent_id: str):
            """Get Agent.

Args:
    agent_id: [TODO: Add description]
"""
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
    limit: int = Query(20, ge=1, le=100),
):
    """List conversations for the current user.

    This endpoint retrieves a paginated list of conversations belonging to
    the authenticated user. Results can be paginated using offset and limit
    parameters.

    Args:
        user_id: The ID of the authenticated user (from auth dependency)
        offset: Number of conversations to skip (pagination offset)
        limit: Maximum number of conversations to return (pagination limit)

    Returns:
        dict: Object containing conversations list and pagination metadata

    Raises:
        HTTPException: If there's an error retrieving the conversations

    Examples:
                GET /api/conversations?offset=0&limit=20
    """
    conversations = await conversation_manager.list_conversations(
        user_id, limit=limit, offset=offset
    )

    return {
        "conversations": conversations,
        "total": len(conversations),  # This would be more efficient with a count query
        "offset": offset,
        "limit": limit,
    }


@router.get("/{thread_id}")
async def get_conversation(thread_id: str, user_id: str = Depends(require_auth)):
    """Get conversation details and state."""
    conversation = await conversation_manager.get_conversation(thread_id, user_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.post("/{thread_id}/messages")
async def add_message(
    thread_id: str, message: dict[str, Any], user_id: str = Depends(require_auth)
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
        if "messages" not in state:
            state["messages"] = []

        if isinstance(message, str):
            state["messages"].append(HumanMessage(content=message))
        elif isinstance(message, dict) and "content" in message:
            state["messages"].append(HumanMessage(content=message["content"]))

    # Create runnable config
    config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

    # Process message with agent
    result = await agent.ainvoke(state, config)

    # Update conversation state

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
            created_at=datetime.now(),
        )
    )

    return result
