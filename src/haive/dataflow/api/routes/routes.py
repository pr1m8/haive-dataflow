"""ReactAgent API routes for agent-based interactions.

This module provides FastAPI routes for interacting with ReactAgent instances
configured with InMemorySaver checkpointers for stateful conversations.
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from haive.dataflow.auth.dependencies import require_auth
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.messages import HumanMessage, SystemMessage

# Import ReactAgent
from haive.agents.react.agent import ReactAgent
from haive.dataflow.persistence.conversations import ConversationManager, ConversationMetadata
from haive.core.engine.aug_llm import AugLLMConfig
from haive.core.models.llm.base import (
    AnthropicLLMConfig,
    AzureLLMConfig,
    DeepSeekLLMConfig,
    GeminiLLMConfig,
    MistralLLMConfig,
    OpenAILLMConfig,
)
from haive.core.models.llm.provider_types import LLMProvider
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Authentication temporarily disabled for testing
# from haive.dataflow.auth.middleware import require_auth

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/react-agent",
    tags=["ReactAgent"],
    # Temporarily remove auth requirement for testing
    # responses={401: {"description": "Not authenticated"}},
)


class ReactAgentRequest(BaseModel):
    """Request model for ReactAgent configuration"""

    provider: LLMProvider = Field(
        default=LLMProvider.AZURE,
        description="The LLM provider to use",
        examples=list(LLMProvider),
    )
    model: str = Field(
        default="gpt-4o",
        description="Specific model to use from the selected provider",
        examples=["gpt-4o", "claude-3-opus", "gpt-35-turbo", "mistral-large-latest"],
    )
    api_key: str | None = Field(
        default=None,
        description="Optional API key for the selected provider. If not provided, will use environment variables.",
    )
    temperature: float | None = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Controls randomness in generation. Lower values make output more focused, higher values more random.",
    )
    system_prompt: str | None = Field(
        default="You are a helpful AI assistant with access to tools. Use these tools to help the user with their request.",
        description="Initial instruction for the ReactAgent to set its behavior",
    )
    thread_id: str | None = Field(
        default=None,
        description="Optional thread ID for conversation persistence. If not provided, a new thread will be created.",
    )
    extra_params: dict[str, Any] | None = Field(
        default=None, description="Additional parameters to pass to the LLM"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "azure",
                "model": "gpt-4o",
                "temperature": 0.7,
                "system_prompt": "You are a helpful assistant that can analyze data and provide insights.",
                "thread_id": "e16b93ec-9081-4ff0-a0cc-0753f546b1e9",
            }
        }
    )


class ReactAgentResponse(BaseModel):
    """Response model for ReactAgent generation"""

    response: str = Field(..., description="Generated response from the ReactAgent")
    model: str = Field(..., description="Model used for generation")
    provider: LLMProvider = Field(..., description="Provider of the LLM")
    thread_id: str = Field(..., description="Thread ID for conversation persistence")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "I can help you with that. Let me analyze the information and provide you with insights.",
                "model": "gpt-4o",
                "provider": "azure",
                "thread_id": "e16b93ec-9081-4ff0-a0cc-0753f546b1e9",
            }
        }
    )


class CreateThreadRequest(BaseModel):
    """Request model for creating a new thread"""
    
    agent_id: str = Field(..., description="ID of the agent to associate with the thread")
    title: str | None = Field(None, description="Optional title for the thread")
    description: str | None = Field(None, description="Optional description for the thread")
    tags: list[str] | None = Field(None, description="Optional tags for the thread")
    custom_data: dict[str, Any] | None = Field(None, description="Optional custom data for the thread")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agent_id": "react-agent",
                "title": "New Conversation",
                "description": "A conversation about data analysis",
                "tags": ["analysis", "data"],
                "custom_data": {"priority": "high"}
            }
        }
    )


class CreateThreadResponse(BaseModel):
    """Response model for thread creation"""
    
    conversation_id: str = Field(..., description="ID of the created conversation")
    thread_id: str = Field(..., description="ID of the created thread")
    title: str | None = Field(None, description="Title of the thread")
    agent_id: str = Field(..., description="ID of the associated agent")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000",
                "thread_id": "thread-456e7890-e89b-12d3-a456-426614174000",
                "title": "New Conversation",
                "agent_id": "react-agent"
            }
        }
    )


def get_env_api_key(provider: LLMProvider) -> str | None:
    """Get API key from environment variables based on provider."""
    import os
    
    env_key_map = {
        LLMProvider.AZURE.value: "AZURE_OPENAI_API_KEY",
        LLMProvider.OPENAI.value: "OPENAI_API_KEY", 
        LLMProvider.ANTHROPIC.value: "ANTHROPIC_API_KEY",
        LLMProvider.GEMINI.value: "GEMINI_API_KEY",
        LLMProvider.DEEPSEEK.value: "DEEPSEEK_API_KEY",
        LLMProvider.MISTRALAI.value: "MISTRAL_API_KEY",
    }
    
    env_key = env_key_map.get(provider.value)
    return os.getenv(env_key) if env_key else None


@router.post(
    "/generate",
    response_model=ReactAgentResponse,
    summary="Generate a response using ReactAgent with InMemorySaver",
    description="Generate a response using ReactAgent configured with InMemorySaver checkpointer for conversation persistence",
)
async def generate_react_response(
    request: ReactAgentRequest,
    query: str = Query(
        ..., description="The input query or message to send to the ReactAgent"
    ),
    user_id: str = Depends(require_auth),
):
    """Generate a response using ReactAgent with InMemorySaver checkpointer

    Args:
        request: ReactAgent configuration details
        query: User's input query
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(f"Received request: {request}")
    logger.warning(f"Query parameter: {query}")

    try:
        # Select the appropriate LLM configuration based on provider
        extra_params = request.extra_params or {}
        extra_params["temperature"] = request.temperature

        # Dynamic LLM config selection
        llm_config_map = {
            LLMProvider.AZURE.value: AzureLLMConfig,
            LLMProvider.OPENAI.value: OpenAILLMConfig,
            LLMProvider.ANTHROPIC.value: AnthropicLLMConfig,
            LLMProvider.GEMINI.value: GeminiLLMConfig,
            LLMProvider.DEEPSEEK.value: DeepSeekLLMConfig,
            LLMProvider.MISTRALAI.value: MistralLLMConfig,
        }

        # Get the configuration class
        LLMConfigClass = llm_config_map.get(request.provider.value)

        if not LLMConfigClass:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider: {request.provider}"
            )

        # Determine API key - prioritize provided key, then environment variable
        api_key = request.api_key or get_env_api_key(request.provider)

        # Raise error if no API key is found
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail=f"No API key found for provider {request.provider}. "
                "Please provide an API key or set the corresponding environment variable.",
            )

        # Create LLM configuration
        llm_config = LLMConfigClass(
            model=request.model, api_key=api_key, parameters=extra_params
        )

        # Create prompt template with system and human messages
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=request.system_prompt or "You are a helpful AI assistant with access to tools."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Create AugLLMConfig for the ReactAgent
        aug_llm_config = AugLLMConfig(
            llm_config=llm_config, prompt_template=prompt_template
        )

        # Create ReactAgent with the engine directly
        react_agent = ReactAgent(
            name=f"react_agent_{user_id}",
            engine=aug_llm_config,
        )
        
        # Set a default state schema if not already set
        if not hasattr(react_agent.graph, 'state_schema') or react_agent.graph.state_schema is None:
            from haive.core.schema.state_schema import StateSchema
            react_agent.graph.state_schema = StateSchema

        # Set up InMemorySaver checkpointer using proper abstraction
        from haive.core.persistence.memory import MemoryCheckpointerConfig
        memory_config = MemoryCheckpointerConfig()
        memory_saver = memory_config.create_checkpointer()
        react_agent.checkpointer = memory_saver

        # Compile the agent (this sets up the internal _app attribute)
        react_agent.compile()

        # Generate thread ID if not provided (following developer's pattern)
        if not request.thread_id:
            # Create conversation using the developer's pattern
            conversation_manager = ConversationManager()
            metadata = ConversationMetadata(
                agent_id="react-agent",
                title=f"React Chat {datetime.now().strftime('%H:%M')}"
            )
            result = await conversation_manager.create_conversation(user_id, metadata)
            thread_id = result["thread_id"] if result else str(uuid.uuid4())
        else:
            thread_id = request.thread_id

        # Run the ReactAgent
        input_message = HumanMessage(content=query)
        response = react_agent.run(
            input_data={"messages": [input_message]},
            thread_id=thread_id
        )

        # Extract the response content
        response_content = "No response generated"
        
        # Handle different response formats
        if hasattr(response, "messages") and response.messages:
            # Get the last AI message from the agent
            messages = response.messages
            for msg in reversed(messages):
                if hasattr(msg, "content") and hasattr(msg, "__class__"):
                    # Skip tool messages and get the last AI message
                    if msg.__class__.__name__ == "AIMessage" and msg.content:
                        response_content = msg.content
                        break
        elif isinstance(response, dict) and "messages" in response:
            # Handle dict format
            messages = response["messages"]
            for msg in reversed(messages):
                if hasattr(msg, "content") and hasattr(msg, "__class__"):
                    if msg.__class__.__name__ == "AIMessage" and msg.content:
                        response_content = msg.content
                        break
        else:
            # Fallback to string representation
            response_content = str(response)

        # Return the response
        return ReactAgentResponse(
            response=response_content,
            model=request.model,
            provider=request.provider,
            thread_id=thread_id,
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions as is
        logger.error(f"HTTPException in generate_react_response: {e}")
        raise e
    except Exception as e:
        # Log the full traceback
        logger.error(f"Error in generate_react_response: {e}")
        logger.error(traceback.format_exc())

        # Raise an HTTP exception with more detailed error
        raise HTTPException(status_code=500, detail=str(e))
