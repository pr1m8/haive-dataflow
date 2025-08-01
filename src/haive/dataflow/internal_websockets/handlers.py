# haive_dataflow/api/websockets/handlers.py

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage

from haive.dataflow.internal_websockets.auth.credits import CreditsManager, UsageRecord
from haive.dataflow.internal_websockets.config.settings import get_settings
from haive.dataflow.internal_websockets.internal_websockets.manager import (
    ConnectionManager,
)
from haive.dataflow.internal_websockets.persistence.conversations import (
    ConversationManager,
)
from haive.dataflow.persistence.supabase_adapter import SupabasePersistence
from haive.dataflow.registry import AgentRegistry

# Try importing from your registry
try:
    from dataflow.registry import AgentRegistry
except ImportError:
    # Mock registry for testing
    class AgentRegistry:
        @staticmethod
        async def get_agent(agent_id: str):
            return None


logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSockets"])
connection_manager = ConnectionManager()
conversation_manager = ConversationManager()
credits_manager = CreditsManager()
settings = get_settings()


@router.websocket("/ws/conversations/{thread_id}/stream")
async def stream_agent_response(websocket: WebSocket, thread_id: str):
    """Stream agent responses via WebSocket."""
    connection_id = await connection_manager.connect(websocket, thread_id)

    if not connection_id:
        # Connection failed (authentication error)
        return

    try:
        # Get user ID from websocket state
        user_id = websocket.state.user_id

        # Get conversation details
        conversation = await conversation_manager.get_conversation(thread_id, user_id)
        if not conversation:
            await websocket.send_json(
                {"type": "error", "detail": "Conversation not found"}
            )
            await websocket.close(code=1008, reason="Conversation not found")
            return

        # Extract agent_id from conversation
        agent_id = conversation.get("agent_id")

        # Load the agent
        agent = await AgentRegistry.get_agent(agent_id)
        if not agent:
            await websocket.send_json({"type": "error", "detail": "Agent not found"})
            await websocket.close(code=1008, reason="Agent not found")
            return

        # Check credits
        has_credits = await credits_manager.check_credits(user_id)
        if not has_credits:
            await websocket.send_json(
                {"type": "error", "detail": "Insufficient credits"}
            )
            await websocket.close(code=1008, reason="Insufficient credits")
            return

        # Send initial state
        await websocket.send_json(
            {
                "type": "initial_state",
                "conversation": {
                    "id": conversation.get("id"),
                    "thread_id": thread_id,
                    "agent_id": agent_id,
                    "title": conversation.get("title"),
                },
            }
        )

        # Listen for messages
        while True:
            # Receive message from client
            message_data = await websocket.receive_text()
            message = json.loads(message_data)

            # Get message content
            if "content" not in message:
                await websocket.send_json(
                    {"type": "error", "detail": "Message content is required"}
                )
                continue

            # Get current state
            state = conversation.get("state", {})
            if not state:
                state = {"messages": []}

            # Add the user message to state
            message_content = message["content"]

            if isinstance(state, dict) and "messages" in state:
                state["messages"].append(HumanMessage(content=message_content))

            # Create runnable config
            config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

            # Start streaming
            await websocket.send_json({"type": "stream_start"})

            # Track token usage
            token_count = 0

            try:
                # Stream response in real-time
                for chunk in agent.stream(state, config):
                    # Update token count if available
                    if isinstance(chunk, dict) and "token_usage" in chunk:
                        token_count += chunk["token_usage"].get("completion_tokens", 0)

                    # Format chunk for client
                    formatted_chunk = format_chunk_for_client(chunk)
                    await websocket.send_json(formatted_chunk)

                # Get final state after streaming
                final_state = await agent.ainvoke(state, config)

                # Update conversation state

                persistence = SupabasePersistence()
                success = await persistence.update_state(
                    thread_id, user_id, final_state
                )

                if not success:
                    logger.error(f"Failed to update state for thread {thread_id}")

                # Calculate cost
                cost_per_1k = settings.agent.credit_cost_per_1k_tokens
                cost = Decimal(token_count) / 1000 * Decimal(cost_per_1k)

                # Deduct credits and log usage
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

                # Send completion message
                await websocket.send_json(
                    {
                        "type": "stream_end",
                        "token_count": token_count,
                        "cost": float(cost),
                    }
                )

            except Exception as e:
                logger.exception(f"Error in streaming: {e}")
                await websocket.send_json({"type": "error", "detail": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {thread_id}/{connection_id}")
        connection_manager.disconnect(thread_id, connection_id)
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "detail": str(e)})
            await websocket.close()
        except BaseException:
            pass
        connection_manager.disconnect(thread_id, connection_id)


def format_chunk_for_client(chunk: Any) -> dict[str, Any]:
    """Format a streaming chunk for client consumption."""
    if isinstance(chunk, dict):
        # For structured data
        return {"type": "chunk", "data": chunk}
    # For text chunks
    return {"type": "chunk", "data": {"text": str(chunk)}}
