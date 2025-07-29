"""WebSocket and REST API endpoints for agent interactions.

This module provides WebSocket-based communication with Haive agents, enabling
real-time interactions, streaming responses, and persistent conversation state.
It also includes REST endpoints for agent management and configuration.

The WebSocket protocol supports different message types for user messages,
agent responses, status updates, and error handling. Connections are managed
per thread, allowing multiple concurrent agent sessions.

Key components:
- WebSocket connection manager for handling multiple clients
- Message types and formats for structured communication
- Authentication and authorization using Supabase
- Agent configuration and customization options
- Streaming response support for real-time feedback

Typical usage example:

    ```python
    # Client-side WebSocket example
    import websockets
    import json
    import asyncio

    async def connect_to_agent():
        uri = "ws://localhost:8000/api/ws/agent/chat?token=YOUR_AUTH_TOKEN"
        async with websockets.connect(uri) as websocket:
            # Send initial configuration
            await websocket.send(json.dumps({
                "type": "config",
                "content": {
                    "agent_name": "TextAnalyzer",
                    "provider": "openai",
                    "model": "gpt-4",
                    "stream": True
                }
            }))

            # Send a message to the agent
            await websocket.send(json.dumps({
                "type": "message",
                "content": "Analyze this text for sentiment"
            }))

            # Receive streaming responses
            while True:
                response = json.loads(await websocket.recv())
                if response["type"] == "response":
                    print(response["content"])
                elif response["type"] == "state_complete":
                    break

    asyncio.run(connect_to_agent())
    ```
"""

import asyncio
import importlib.util
import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.websockets import WebSocketState
from pydantic import BaseModel, Field

from .auth.dependencies import require_auth
from .auth.supabase import SupabaseAuth

# Authentication imports
from .engine.agent.config import AgentConfig
from .engine.aug_llm import AugLLMConfig
from .models.llm.base import (
    AnthropicLLMConfig,
    AzureLLMConfig,
    DeepSeekLLMConfig,
    GeminiLLMConfig,
    MistralLLMConfig,
    OpenAILLMConfig,
)
from .models.llm.provider_types import LLMProvider

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/ws",
    tags=["WebSocket Chat"],
    responses={401: {"description": "Not authenticated"}},
)


# Message types
class WSMessageType(str, Enum):
    """WebSocket message types for agent communication.

    This enumeration defines the different types of messages that can be
    exchanged over the WebSocket connection. Each type has a specific
    purpose and expected format.

    Attributes:
        MESSAGE: User message sent to the agent
        RESPONSE: Agent response sent back to the user
        STATUS: System status updates (connection, processing, etc.)
        ERROR: Error messages for exception handling
        STATE: Incremental agent state updates during processing
        STATE_COMPLETE: Final agent state after processing completes
    """

    MESSAGE = "message"  # User message
    RESPONSE = "response"  # Agent response
    STATUS = "status"  # System status
    ERROR = "error"  # Error message
    STATE = "state"  # Agent state update
    STATE_COMPLETE = "state_complete"  # Final agent state


class WSMessage(BaseModel):
    """WebSocket message format for agent communication.

    This model defines the standard format for all messages exchanged over
    the WebSocket connection. It provides a consistent structure with
    metadata for message handling and tracking.

    Attributes:
        type: The type of message (from WSMessageType enum)
        content: The actual message content (type depends on message type)
        thread_id: Optional ID for persistent chat threads
        stream_index: Optional index for streaming response chunks
        timestamp: When the message was created (defaults to current time)

    Example:
        >>> message = WSMessage(
        ...     type=WSMessageType.MESSAGE,
        ...     content="Analyze this text",
        ...     thread_id="thread-123"
        ... )
        >>> json_str = message.json()
    """

    type: WSMessageType = Field(..., description="Message type")
    content: Any = Field(..., description="Message content")
    thread_id: str | None = Field(None, description="Thread ID for persistent chat")
    stream_index: int | None = Field(None, description="Stream chunk index")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentChatConfig(BaseModel):
    """Configuration for agent chat sessions via WebSocket.

    This model defines the configuration options for an agent chat session,
    including which agent to use, LLM settings, and behavior options like
    streaming and persistence.

    Attributes:
        agent_name: Name of the agent to use for this chat session
        provider: LLM provider to use (e.g., AZURE, OPENAI, ANTHROPIC)
        model: Specific model to use from the provider
        temperature: Sampling temperature for response generation (0.0-1.0)
        system_prompt: Optional override for the agent's system prompt
        persistent: Whether to persist chat state between messages
        stream: Whether to stream responses incrementally
        extra_params: Additional provider-specific parameters

    Example:
        >>> config = AgentChatConfig(
        ...     agent_name="TextAnalyzer",
        ...     provider=LLMProvider.OPENAI,
        ...     model="gpt-4",
        ...     temperature=0.5,
        ...     system_prompt="You are an expert text analyst.",
        ...     stream=True
        ... )
    """

    agent_name: str = Field(..., description="Agent to use")
    provider: LLMProvider = Field(default=LLMProvider.AZURE, description="LLM provider")
    model: str = Field(default="GPT-4 Turbo", description="Model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    system_prompt: str | None = Field(None, description="System prompt override")
    persistent: bool = Field(default=True, description="Whether to persist chat state")
    stream: bool = Field(default=True, description="Whether to stream responses")
    # Enhanced streaming options
    stream_mode: str = Field(
        default="messages",
        description="Stream mode: messages, values, updates, debug, custom",
    )
    stream_format: str = Field(
        default="auto", description="Output format: auto, json, text, structured"
    )
    progressive_updates: bool = Field(
        default=False, description="Send partial schema-valid results"
    )
    buffer_chunks: bool = Field(
        default=False, description="Buffer multiple chunks before sending"
    )
    chunk_size: int = Field(default=1, description="Number of chunks to buffer")
    extra_params: dict[str, Any] | None = Field(default=None)


class ConnectionManager:
    """Manages WebSocket connections for agent chat sessions.

    This class provides functionality for managing WebSocket connections,
    organizing them by thread, and handling connection lifecycle events.
    It supports multiple concurrent connections to the same thread,
    enabling features like shared sessions and observers.

    The connection manager maintains:
    - Active WebSocket connections grouped by thread ID
    - Metadata for each thread (configuration, state, etc.)
    - Thread-safe operations with asyncio locks

    Attributes:
        active_connections: Dictionary mapping thread IDs to lists of WebSocket connections
        thread_metadata: Dictionary mapping thread IDs to metadata dictionaries
        _lock: Asyncio lock for thread-safe operations on shared data structures
    """

    def __init__(self):
        """Initialize the connection manager.

        Creates empty dictionaries for tracking connections and metadata,
        and initializes the asyncio lock for thread safety.
        """
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.thread_metadata: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, thread_id: str, user_id: str) -> bool:
        """Connect a WebSocket to a thread.

        This method accepts a new WebSocket connection and associates it with
        the specified thread. If this is the first connection to the thread,
        it also initializes the thread metadata.

        Args:
            websocket: The WebSocket connection to add
            thread_id: The ID of the thread to connect to
            user_id: The ID of the user making the connection

        Returns:
            bool: True if the connection was successful, False otherwise

        Raises:
            WebSocketDisconnect: If the connection cannot be established

        Example:
            >>> manager = ConnectionManager()
            >>> success = await manager.connect(websocket, "thread-123", "user-456")
            >>> if success:
            ...     print("Connection established")
        """
        try:
            await websocket.accept()
            async with self._lock:
                if thread_id not in self.active_connections:
                    self.active_connections[thread_id] = []
                self.active_connections[thread_id].append(websocket)

                if thread_id not in self.thread_metadata:
                    self.thread_metadata[thread_id] = {
                        "created_at": datetime.utcnow().isoformat(),
                        "user_id": user_id,
                        "last_activity": datetime.utcnow().isoformat(),
                    }

            logger.info(f"WebSocket connected to thread {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            return False

    async def disconnect(self, websocket: WebSocket, thread_id: str):
        """Disconnect a WebSocket from a thread."""
        async with self._lock:
            if thread_id in self.active_connections:
                if websocket in self.active_connections[thread_id]:
                    self.active_connections[thread_id].remove(websocket)

                # Remove empty connection lists
                if not self.active_connections[thread_id]:
                    del self.active_connections[thread_id]
                    if thread_id in self.thread_metadata:
                        del self.thread_metadata[thread_id]

    async def broadcast_to_thread(self, thread_id: str, message: WSMessage):
        """Broadcast message to all connections in a thread."""
        if thread_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[thread_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_json(message.dict())
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected.append(connection)

            # Clean up disconnected sockets
            for conn in disconnected:
                await self.disconnect(conn, thread_id)

    async def update_activity(self, thread_id: str):
        """Update last activity timestamp for a thread."""
        if thread_id in self.thread_metadata:
            self.thread_metadata[thread_id][
                "last_activity"
            ] = datetime.utcnow().isoformat()


# Global connection manager
manager = ConnectionManager()


# Authentication helper function
def get_user_from_token(token: str) -> str | None:
    """Validate JWT token and return user ID."""
    # Development mode bypass
    import os

    haive_env = os.getenv("HAIVE_ENV")
    logger.info(f"HAIVE_ENV: {haive_env}, token: {token[:20]}...")
    if haive_env == "development" and token == "test":
        logger.warning("Using development bypass for authentication")
        return "test-user"

    try:
        auth = SupabaseAuth()
        user_id = auth.get_user_id(token)
        return user_id
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None


# Agent loading helper
async def load_agent_config(
    agent_name: str, user_id: str, thread_id: str
) -> AgentConfig | None:
    """Load agent configuration from package."""
    try:
        # Look for agent configuration
        agents_path = "/home/will/Projects/haive/backend/haive/packages/haive-agents"
        agent_path = os.path.join(agents_path, agent_name)

        if not os.path.exists(agent_path):
            logger.error(f"Agent directory not found: {agent_path}")
            return None

        # Try to load config file
        config_file = os.path.join(agent_path, "config.py")
        state_file = os.path.join(agent_path, "state.py")
        agent_file = os.path.join(agent_path, "agent.py")

        # Check for required files
        if not os.path.exists(config_file):
            logger.error(f"No config.py found in {agent_path}")
            return None

        try:
            # Load config module
            spec = importlib.util.spec_from_file_location("config", config_file)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)

            # Look for AgentConfig subclass
            config_instance = None
            for item_name in dir(config_module):
                item = getattr(config_module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, AgentConfig)
                    and item != AgentConfig
                ):

                    # Create instance with context information
                    config_instance = item()
                    break

            if not config_instance:
                logger.error(f"No AgentConfig subclass found in {config_file}")
                return None

            # Add context to config's metadata
            config_instance.metadata.update(
                {
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "agent_name": agent_name,
                    "agent_package_path": agent_path,
                }
            )

            # Set name to include context
            config_instance.name = f"{agent_name}_{thread_id[:8]}"

            # Set runnable config with thread_id
            config_instance.runnable_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "agent_id": config_instance.name,
                }
            }

            # Import and register agent if exists
            if os.path.exists(agent_file):
                try:
                    agent_spec = importlib.util.spec_from_file_location(
                        "agent", agent_file
                    )
                    agent_module = importlib.util.module_from_spec(agent_spec)
                    agent_spec.loader.exec_module(agent_module)

                    # Look for agent class and register it
                    for item_name in dir(agent_module):
                        item = getattr(agent_module, item_name)
                        if (
                            isinstance(item, type)
                            and hasattr(item, "__base__")
                            and item.__name__ != "Agent"
                        ):
                            # Register agent class for this config
                            item.config_class = type(config_instance)
                            from haive.core.engine.agent.agent import AGENT_REGISTRY

                            AGENT_REGISTRY[type(config_instance)] = item
                            logger.info(f"Registered agent class: {item_name}")
                            break
                except Exception as e:
                    logger.warning(f"Failed to load agent module: {e}")

            logger.info(
                f"Loaded agent config: {config_instance.__class__.__name__} for thread {thread_id}"
            )
            return config_instance

        except Exception as e:
            logger.error(f"Error loading config module: {e}")
            return None

    except Exception as e:
        logger.error(f"Error loading agent config: {e}")
        return None


# Configure agent with LLM settings
async def configure_agent(
    config: AgentConfig, chat_config: AgentChatConfig
) -> AgentConfig:
    """Configure agent with LLM settings."""
    try:
        # Get environment API key based on provider
        env_key_map = {
            LLMProvider.AZURE.value: "AZURE_OPENAI_API_KEY",
            LLMProvider.OPENAI.value: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC.value: "ANTHROPIC_API_KEY",
            LLMProvider.GEMINI.value: "GOOGLE_API_KEY",
            LLMProvider.DEEPSEEK.value: "DEEPSEEK_API_KEY",
            LLMProvider.MISTRALAI.value: "MISTRAL_API_KEY",
        }

        env_var = env_key_map.get(chat_config.provider.value)
        api_key = os.getenv(env_var) if env_var else None

        if not api_key:
            raise ValueError(f"No API key found for provider {chat_config.provider}")

        # Select provider configuration
        llm_config_map = {
            LLMProvider.AZURE.value: AzureLLMConfig,
            LLMProvider.OPENAI.value: OpenAILLMConfig,
            LLMProvider.ANTHROPIC.value: AnthropicLLMConfig,
            LLMProvider.GEMINI.value: GeminiLLMConfig,
            LLMProvider.DEEPSEEK.value: DeepSeekLLMConfig,
            LLMProvider.MISTRALAI.value: MistralLLMConfig,
        }

        LLMConfigClass = llm_config_map.get(chat_config.provider.value)
        if not LLMConfigClass:
            raise ValueError(f"Unsupported provider: {chat_config.provider}")

        llm_config = LLMConfigClass(
            model=chat_config.model,
            api_key=api_key,
            parameters={
                "temperature": chat_config.temperature,
                **(chat_config.extra_params or {}),
            },
        )

        # Create AugLLM configuration with context
        aug_llm_config = AugLLMConfig(
            llm_config=llm_config, prompt_template=None  # Use default template
        )

        # Preserve metadata when updating engine
        aug_llm_config.metadata = config.metadata.copy()

        # Update agent engine if it doesn't already have one
        if not hasattr(config, "engine") or config.engine is None:
            config.engine = aug_llm_config

        # Handle checkpoint mode based on persistent setting
        config.checkpoint_mode = "sync" if chat_config.persistent else "none"

        # Update metadata with LLM config
        config.metadata.update(
            {
                "provider": chat_config.provider.value,
                "model": chat_config.model,
                "configured_at": datetime.utcnow().isoformat(),
            }
        )

        return config

    except Exception as e:
        logger.error(f"Error configuring agent: {e}")
        raise


# WebSocket endpoint for agent chat
@router.websocket("/chat/{agent_name}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    agent_name: str,
    token: str = Query(..., description="JWT authentication token"),
    thread_id: str | None = Query(
        None, description="Existing thread ID for persistence"
    ),
    config: str | None = Query(None, description="JSON encoded chat configuration"),
):
    """WebSocket endpoint for real-time chat with an agent.

    Args:
        websocket: WebSocket connection
        agent_name: Name of the agent to chat with
        token: JWT authentication token
        thread_id: Optional thread ID for persistent chat
        config: Optional JSON-encoded chat configuration
    """
    user_id = None

    try:
        # Authenticate user
        user_id = get_user_from_token(token)
        if not user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Generate thread ID if not provided
        if not thread_id:
            thread_id = str(uuid.uuid4())

        # Parse chat configuration
        chat_config = (
            AgentChatConfig.parse_obj(json.loads(config))
            if config
            else AgentChatConfig(agent_name=agent_name)
        )

        # Connect to connection manager
        if not await manager.connect(websocket, thread_id, user_id):
            await websocket.close(code=1013, reason="Connection failed")
            return

        # Load agent configuration with context
        agent_config = await load_agent_config(agent_name, user_id, thread_id)
        if not agent_config:
            await websocket.close(code=1002, reason=f"Agent '{agent_name}' not found")
            return

        # Configure agent with Supabase checkpointing
        agent_config = await configure_agent(agent_config, chat_config)

        # Set up Supabase checkpointing for authenticated users
        checkpointer = None
        if chat_config.persistent and user_id:
            from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

            # Create Supabase persistence adapter
            persistence = SupabasePersistence()

            # Get checkpointer for the agent
            checkpointer = await persistence.get_checkpointer()

            # Register thread with user ownership
            await persistence.register_thread(
                thread_id=thread_id,
                user_id=user_id,
                metadata={
                    "agent_name": agent_name,
                    "chat_config": chat_config.dict(),
                    "created_via": "websocket_api",
                },
            )

            # Update agent config metadata
            agent_config.metadata.update(
                {
                    "persistence_backend": "supabase",
                    "thread_id": thread_id,
                    "user_id": user_id,
                }
            )

            # Set the checkpointer in the agent's runnable config
            if (
                not hasattr(agent_config, "runnable_config")
                or agent_config.runnable_config is None
            ):
                agent_config.runnable_config = {}
            if "configurable" not in agent_config.runnable_config:
                agent_config.runnable_config["configurable"] = {}
            agent_config.runnable_config["configurable"]["checkpointef"] = checkpointer

        # Send welcome message with context
        welcome_msg = WSMessage(
            type=WSMessageType.STATUS,
            content={
                "status": "connected",
                "thread_id": thread_id,
                "agent": agent_name,
                "user_id": user_id,
                "agent_id": agent_config.name,
                "metadata": agent_config.metadata,
            },
        )
        await websocket.send_json(welcome_msg.dict())

        # Main chat loop
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()

                try:
                    # Parse incoming message
                    incoming_msg = json.loads(data)
                    message_content = incoming_msg.get("content", "")

                    # Update activity timestamp
                    await manager.update_activity(thread_id)

                    # Build agent and get response
                    agent = agent_config.build_agent()

                    # Add context to the agent execution
                    execution_context = {
                        "configurable": {
                            "thread_id": thread_id,
                            "user_id": user_id,
                            "agent_id": agent_config.name,
                            "debug": (
                                chat_config.extra_params.get("debug", False)
                                if chat_config.extra_params
                                else False
                            ),
                        }
                    }

                    # Add checkpointer if available
                    if checkpointer:
                        execution_context["configurable"]["checkpointef"] = checkpointer

                    if chat_config.stream:
                        # Stream response
                        stream_index = 0

                        # Send streaming start notification
                        start_msg = WSMessage(
                            type=WSMessageType.STATUS,
                            content={
                                "status": "streaming",
                                "stream_index": stream_index,
                                "thread_id": thread_id,
                            },
                        )
                        await websocket.send_json(start_msg.dict())

                        # Stream agent response with configured mode
                        async for chunk in agent.astream(
                            message_content,
                            thread_id=thread_id,
                            stream_mode=chat_config.stream_mode,
                            config=execution_context,
                        ):
                            # Process chunk based on stream format
                            content = None

                            if chat_config.stream_format == "text":
                                # Extract text content only
                                if isinstance(chunk, dict):
                                    if chunk.get("messages"):
                                        messages = chunk["messages"]
                                        if messages and hasattr(
                                            messages[-1], "content"
                                        ):
                                            content = messages[-1].content
                                    elif "content" in chunk:
                                        content = chunk["content"]
                                    elif "text" in chunk:
                                        content = chunk["text"]
                                else:
                                    content = str(chunk)
                            elif chat_config.stream_format == "json":
                                # Send full chunk as JSON
                                content = chunk
                            elif chat_config.stream_format == "structured":
                                # Include type information
                                content = {
                                    "data": chunk,
                                    "type": (
                                        type(chunk).__name__
                                        if hasattr(chunk, "__class__")
                                        else "dict"
                                    ),
                                }
                            # Default behavior - extract messages for message mode
                            elif (
                                chat_config.stream_mode == "messages"
                                and isinstance(chunk, dict)
                                and "messages" in chunk
                            ):
                                messages = chunk["messages"]
                                if messages and hasattr(messages[-1], "content"):
                                    content = messages[-1].content
                            else:
                                content = chunk

                            if content is not None:
                                response_msg = WSMessage(
                                    type=WSMessageType.RESPONSE,
                                    content=content,
                                    thread_id=thread_id,
                                    stream_index=stream_index,
                                )
                                await websocket.send_json(response_msg.dict())
                                stream_index += 1

                        # Send stream completion
                        complete_msg = WSMessage(
                            type=WSMessageType.STATUS,
                            content={
                                "status": "complete",
                                "stream_index": stream_index,
                                "thread_id": thread_id,
                            },
                        )
                        await websocket.send_json(complete_msg.dict())
                    else:
                        # Single response
                        result = await agent.arun(
                            message_content,
                            thread_id=thread_id,
                            config=execution_context,
                        )

                        response_msg = WSMessage(
                            type=WSMessageType.RESPONSE,
                            content=result,
                            thread_id=thread_id,
                        )
                        await websocket.send_json(response_msg.dict())

                    # Get final state if needed for debugging
                    if chat_config.extra_params and chat_config.extra_params.get(
                        "send_state", False
                    ):
                        try:
                            # Get state instead of just inspecting it
                            state = agent.app.get_state(config=execution_context)
                            if state:
                                state_msg = WSMessage(
                                    type=WSMessageType.STATE_COMPLETE,
                                    content=state,
                                    thread_id=thread_id,
                                )
                                await websocket.send_json(state_msg.dict())
                        except Exception as e:
                            logger.error(f"Error getting state: {e}")

                except json.JSONDecodeError:
                    error_msg = WSMessage(
                        type=WSMessageType.ERROR,
                        content={"error": "Invalid JSON format"},
                    )
                    await websocket.send_json(error_msg.dict())

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_msg = WSMessage(
                        type=WSMessageType.ERROR, content={"error": str(e)}
                    )
                    await websocket.send_json(error_msg.dict())

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for thread {thread_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            error_msg = WSMessage(type=WSMessageType.ERROR, content={"error": str(e)})
            try:
                await websocket.send_json(error_msg.dict())
            except:
                pass
        finally:
            # Cleanup
            await manager.disconnect(websocket, thread_id)
            try:
                await websocket.close()
            except:
                pass

    except Exception as e:
        logger.error(f"Fatal error in WebSocket chat: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


# Add REST endpoint to reset thread using authentication
@router.post("/chat/thread/{thread_id}/reset")
async def reset_thread(thread_id: str, user_id: str = Depends(require_auth)):
    """Reset/clear a chat thread."""
    try:
        # Verify thread ownership
        if thread_id in manager.thread_metadata:
            thread_metadata = manager.thread_metadata[thread_id]
            if thread_metadata.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Access denied")

        # Reset agent state
        # This would need to be implemented to clear PostgreSQL checkpoint
        # For now, just return success

        return {
            "status": "success",
            "message": f"Thread {thread_id} reset successfully",
            "thread_id": thread_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))
