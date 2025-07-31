#!/usr/bin/env python3
"""
Different streaming modes for Haive agents

Available stream modes:
1. "values" - Stream full state values
2. "updates" - Stream only the updates/changes
3. "messages" - Stream just the messages (good for chat)
4. "debug" - Stream detailed debug information
5. "custom" - Raw stream data without processing
"""

from typing import Any, AsyncGenerator

from pydantic import BaseModel

from .base.agent import Agent


class StreamingAgent(Agent):
    """Example agent showing different streaming modes"""

    def build_graph(self):
        # Your graph building logic
        pass

    async def stream_with_mode(
        self, input_data: Any, mode: str = "messages", thread_id: str = None
    ) -> AsyncGenerator[dict, None]:
        """Stream with different modes based on use case"""

        # Stream with specified mode
        async for chunk in self.astream(
            input_data, thread_id=thread_id, stream_mode=mode
        ):
            yield chunk


# Example schemas for different output types
class ChatMessage(BaseModel):
    """Schema for chat messages"""

    content: str
    role: str = "assistant"
    metadata: dict = {}


class AnalysisResult(BaseModel):
    """Schema for analysis results"""

    summary: str
    entities: list[str] = []
    sentiment: float = 0.0
    confidence: float = 0.0


class StreamUpdate(BaseModel):
    """Schema for streaming updates"""

    update_type: str  # "text", "data", "status", "error"
    content: Any
    progress: float = 0.0
    is_final: bool = False


# WebSocket message handler with flexible streaming
async def handle_stream_request(
    agent: Agent, message: dict, websocket: Any, thread_id: str
):
    """Handle different streaming modes based on request"""

    # Extract streaming preferences
    stream_config = message.get("stream_config", {})
    mode = stream_config.get("mode", "messages")
    format_output = stream_config.get("format", True)
    stream_config.get("metadata", False)

    # Choose streaming mode based on agent type and request
    if mode == "analysis":
        # Stream with updates for analysis
        async for chunk in agent.astream(
            message["content"], thread_id=thread_id, stream_mode="updates"
        ):
            # Format for analysis display
            if "summary" in chunk:
                await websocket.send_json(
                    {
                        "type": "analysis_update",
                        "content": chunk["summary"],
                        "partial": True,
                    }
                )
            elif "entities" in chunk:
                await websocket.send_json(
                    {"type": "entities_found", "content": chunk["entities"]}
                )

    elif mode == "chat":
        # Stream messages for chat
        async for chunk in agent.astream(
            message["content"], thread_id=thread_id, stream_mode="messages"
        ):
            if "messages" in chunk and chunk["messages"]:
                last_msg = chunk["messages"][-1]
                await websocket.send_json(
                    {
                        "type": "chat_response",
                        "content": (
                            last_msg.content
                            if hasattr(last_msg, "content")
                            else str(last_msg)
                        ),
                        "role": getattr(last_msg, "role", "assistant"),
                    }
                )

    elif mode == "structured":
        # Stream with full state for structured data
        async for chunk in agent.astream(
            message["content"], thread_id=thread_id, stream_mode="values"
        ):
            # Validate against output schema if available
            if hasattr(agent, "output_schema") and format_output:
                try:
                    validated = agent.output_schema(**chunk)
                    await websocket.send_json(
                        {
                            "type": "structured_update",
                            "content": validated.dict(),
                            "valid": True,
                        }
                    )
                except Exception as e:
                    await websocket.send_json(
                        {
                            "type": "structured_update",
                            "content": chunk,
                            "valid": False,
                            "error": str(e),
                        }
                    )
            else:
                await websocket.send_json({"type": "data_update", "content": chunk})

    elif mode == "debug":
        # Stream everything for debugging
        async for chunk in agent.astream(
            message["content"], thread_id=thread_id, stream_mode="debug"
        ):
            await websocket.send_json(
                {
                    "type": "debug",
                    "content": chunk,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    else:
        # Default streaming
        async for chunk in agent.astream(
            message["content"], thread_id=thread_id, stream_mode=mode
        ):
            await websocket.send_json(
                {"type": "stream_chunk", "content": chunk, "mode": mode}
            )


# Enhanced WebSocket configuration
class EnhancedAgentChatConfig(BaseModel):
    """Enhanced configuration for agent chat with streaming options"""

    agent_name: str
    provider: str = "azure"
    model: str = "gpt-4o"
    stream: bool = True
    stream_mode: str = "messages"  # "messages", "values", "updates", "debug", "custom"
    stream_format: str = "auto"  # "auto", "json", "text", "structured"
    persistent: bool = True
    buffer_size: int = 1  # How many chunks to buffer before sending
    throttle_ms: int = 0  # Milliseconds to wait between chunks
    include_state: bool = False  # Include full state in responses
    validate_output: bool = True  # Validate against output schema
