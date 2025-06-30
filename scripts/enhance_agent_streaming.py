#!/usr/bin/env python3
"""
Enhanced streaming support for agent routes

This shows how to modify the agent_routes.py to support:
1. Multiple streaming modes
2. Schema-aware streaming
3. Custom formatting options
4. Progressive/incremental updates
"""

# Key changes to make in agent_routes.py:

from typing import Any, Literal

# 1. Update AgentChatConfig to include streaming options
from pydantic import BaseModel, Field


class EnhancedAgentChatConfig(BaseModel):
    """Enhanced chat configuration with streaming options"""

    agent_name: str
    provider: str = "azure"
    model: str = "gpt-4o"
    temperature: float = 0.7
    stream: bool = True

    # New streaming options
    stream_mode: Literal["messages", "values", "updates", "debug", "custom"] = (
        "messages"
    )
    stream_format: Literal["auto", "json", "text", "structured", "markdown"] = "auto"
    buffer_chunks: bool = False  # Buffer multiple small chunks before sending
    chunk_size: int = 1  # How many updates to buffer
    include_metadata: bool = False
    validate_schema: bool = True
    progressive_updates: bool = True  # Send partial results as they build

    extra_params: dict[str, Any] | None = None


# 2. Enhanced stream processing in the WebSocket handler
async def enhanced_websocket_handler(
    websocket: WebSocket,
    agent: Any,
    message_content: str,
    chat_config: EnhancedAgentChatConfig,
    execution_context: dict,
):
    """Enhanced WebSocket handler with flexible streaming"""

    if chat_config.stream:
        stream_index = 0
        buffer = []

        # Send streaming start
        await websocket.send_json(
            {
                "type": "status",
                "content": {
                    "status": "streaming",
                    "mode": chat_config.stream_mode,
                    "format": chat_config.stream_format,
                },
            }
        )

        # Stream with specified mode
        async for chunk in agent.astream(
            message_content,
            thread_id=execution_context["configurable"]["thread_id"],
            stream_mode=chat_config.stream_mode,
            config=execution_context,
        ):
            # Process chunk based on format
            formatted_chunk = await format_stream_chunk(
                chunk,
                chat_config,
                agent.output_schema if hasattr(agent, "output_schema") else None,
            )

            if chat_config.buffer_chunks:
                buffer.append(formatted_chunk)
                if len(buffer) >= chat_config.chunk_size:
                    # Send buffered chunks
                    await websocket.send_json(
                        {
                            "type": "response_batch",
                            "chunks": buffer,
                            "stream_index": stream_index,
                        }
                    )
                    buffer = []
                    stream_index += 1
            else:
                # Send immediately
                await websocket.send_json(
                    {
                        "type": "response",
                        "content": formatted_chunk,
                        "stream_index": stream_index,
                        "mode": chat_config.stream_mode,
                    }
                )
                stream_index += 1

        # Send any remaining buffered chunks
        if buffer:
            await websocket.send_json(
                {
                    "type": "response_batch",
                    "chunks": buffer,
                    "stream_index": stream_index,
                }
            )

        # Send completion
        await websocket.send_json(
            {
                "type": "status",
                "content": {"status": "complete", "total_chunks": stream_index},
            }
        )


async def format_stream_chunk(
    chunk: Any, config: EnhancedAgentChatConfig, output_schema: Any = None
) -> Any:
    """Format stream chunk based on configuration"""

    if config.stream_format == "structured" and output_schema:
        # Try to validate against schema
        try:
            if isinstance(chunk, dict):
                validated = output_schema(**chunk)
                return {
                    "data": validated.dict(),
                    "valid": True,
                    "schema": output_schema.__name__,
                }
        except Exception as e:
            return {"data": chunk, "valid": False, "error": str(e)}

    elif config.stream_format == "markdown":
        # Format as markdown
        if isinstance(chunk, dict) and "content" in chunk:
            return f"**Update**: {chunk['content']}\n"
        return str(chunk)

    elif config.stream_format == "text":
        # Extract text content only
        if isinstance(chunk, dict):
            if "messages" in chunk and chunk["messages"]:
                last_msg = chunk["messages"][-1]
                return getattr(last_msg, "content", str(last_msg))
            elif "content" in chunk:
                return chunk["content"]
            elif "text" in chunk:
                return chunk["text"]
        return str(chunk)

    elif config.stream_format == "json":
        # Ensure JSON serializable
        if hasattr(chunk, "dict"):
            return chunk.dict()
        elif hasattr(chunk, "__dict__"):
            return chunk.__dict__
        return chunk

    # Auto format - return as is
    return chunk


# 3. Schema-aware streaming example
class SchemaAwareStreamProcessor:
    """Process streams based on agent output schema"""

    def __init__(self, agent):
        self.agent = agent
        self.output_schema = getattr(agent, "output_schema", None)
        self.partial_data = {}

    async def process_stream(
        self, stream_generator: AsyncGenerator, progressive: bool = True
    ) -> AsyncGenerator[dict, None]:
        """Process stream with schema awareness"""

        async for chunk in stream_generator:
            if self.output_schema and progressive:
                # Build partial results progressively
                self.update_partial_data(chunk)

                # Try to create partial schema instance
                partial_valid = self.validate_partial()

                yield {
                    "type": "progressive",
                    "data": self.partial_data,
                    "complete_fields": self.get_complete_fields(),
                    "valid_partial": partial_valid,
                }
            else:
                # Just pass through
                yield chunk

    def update_partial_data(self, chunk: dict):
        """Update partial data with new chunk"""
        if isinstance(chunk, dict):
            for key, value in chunk.items():
                if value is not None:
                    self.partial_data[key] = value

    def validate_partial(self) -> bool:
        """Check if partial data is valid so far"""
        if not self.output_schema:
            return True

        try:
            # Get required fields
            required_fields = []
            if hasattr(self.output_schema, "__fields__"):
                for name, field in self.output_schema.__fields__.items():
                    if field.required:
                        required_fields.append(name)

            # Check if all required fields are present
            for field in required_fields:
                if field not in self.partial_data:
                    return False

            # Try to create instance
            self.output_schema(**self.partial_data)
            return True
        except:
            return False

    def get_complete_fields(self) -> list[str]:
        """Get list of fields that have been populated"""
        return list(self.partial_data.keys())


# Usage example in your WebSocket endpoint
"""
# In agent_routes.py, modify the streaming section:

if chat_config.stream:
    # Create schema-aware processor
    processor = SchemaAwareStreamProcessor(agent)
    
    # Stream with processing
    stream_gen = agent.astream(
        message_content,
        thread_id=thread_id,
        stream_mode=chat_config.stream_mode,
        config=execution_context,
    )
    
    async for processed_chunk in processor.process_stream(
        stream_gen,
        progressive=chat_config.progressive_updates
    ):
        await websocket.send_json({
            "type": "stream_update",
            "content": processed_chunk,
            "format": chat_config.stream_format
        })
"""
