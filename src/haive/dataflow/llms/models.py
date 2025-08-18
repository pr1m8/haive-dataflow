"""LLM Provider and Model Data Models.

This module defines Pydantic models for representing LLM providers, models,
and their capabilities within the Haive dataflow system. These models are
used for provider registration, capability tracking, and cost management.

Key Components:
    - Provider: LLM provider information and availability
    - Model: Comprehensive model specifications with capabilities
    - ModelCapabilities: Feature support matrix for each model
    - Pricing: Token-based pricing information
    - SearchPricing: Search-specific pricing tiers

Examples:
    Basic usage::

        from haive.dataflow.llms.models import Provider, Model, ModelCapabilities

        # Create a provider
        provider = Provider(
            name="OpenAI",
            is_available=True,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )

        # Define model capabilities
        capabilities = ModelCapabilities(
            supports_function_calling=True,
            supports_vision=True,
            supports_response_schema=True
        )

        # Create a model entry
        model = Model(
            model_id="gpt-4-vision-preview",
            provider="OpenAI",
            mode="chat",
            litellm_provider="openai",
            max_tokens=128000,
            max_input_tokens=120000,
            max_output_tokens=8000,
            capabilities=capabilities
        )

Advanced Usage:
    With pricing information::

        from haive.dataflow.llms.models import Pricing

        pricing = Pricing(
            input_cost_per_token=0.00001,
            output_cost_per_token=0.00003,
            cache_read_input_token_cost=0.000005
        )

        model = Model(
            model_id="claude-3-opus",
            provider="Anthropic",
            mode="chat",
            litellm_provider="anthropic",
            max_tokens=200000,
            max_input_tokens=180000,
            max_output_tokens=20000,
            pricing=pricing
        )

See Also:
    - haive.dataflow.registry: Model registration and discovery
    - haive.core.engine: Engine configuration using these models
    - haive.dataflow.providers: Provider implementation details

Notes:
    - All token counts are measured in the model's native tokenization
    - Pricing is in USD per token for standardized cost calculations
    - Capabilities enable automatic feature detection and routing
"""

from pydantic import BaseModel, Field


class Provider(BaseModel):
    name: str = Field(
        ..., description="Name of the LLM provider (e.g., OpenAI, Anthropic)"
    )
    is_available: bool = Field(
        ..., description="Indicates whether the provider is currently available for use"
    )
    created_at: str = Field(
        ..., description="Timestamp when the provider entry was created"
    )
    updated_at: str = Field(
        ..., description="Timestamp when the provider entry was last updated"
    )


class ModelCapabilities(BaseModel):
    supports_function_calling: bool = Field(
        False, description="Supports standard function/tool calling"
    )
    supports_parallel_function_calling: bool = Field(
        False, description="Supports calling multiple tools in parallel"
    )
    supports_vision: bool = Field(
        False, description="Can process visual input (e.g., images, video frames)"
    )
    supports_audio_input: bool = Field(
        False, description="Can accept audio input (e.g., speech-to-text)"
    )
    supports_audio_output: bool = Field(
        False, description="Can generate audio output (e.g., text-to-speech)"
    )
    supports_prompt_caching: bool = Field(
        False, description="Supports caching of prompts for performance optimization"
    )
    supports_response_schema: bool = Field(
        False,
        description="Supports structured response schemas (e.g., Pydantic parsing)",
    )
    supports_system_messages: bool = Field(
        False,
        description="Understands and utilizes system messages in conversation context",
    )
    supports_web_search: bool = Field(
        False, description="Can retrieve information from the web during inference"
    )
    supports_tool_choice: bool = Field(
        False, description="Can intelligently select from a list of available tools"
    )


class Pricing(BaseModel):
    input_cost_per_token: float = Field(0, description="Cost per input token (USD)")
    output_cost_per_token: float = Field(0, description="Cost per output token (USD)")
    input_cost_per_token_batches: float | None = Field(
        0, description="Discounted input cost for batched requests"
    )
    output_cost_per_token_batches: float | None = Field(
        0, description="Discounted output cost for batched requests"
    )
    input_cost_per_audio_token: float | None = Field(
        0, description="Cost per audio input token (e.g., for speech-to-text)"
    )
    output_cost_per_audio_token: float | None = Field(
        0, description="Cost per audio output token (e.g., for TTS)"
    )
    cache_read_input_token_cost: float | None = Field(
        0, description="Cost for reading cached prompt tokens, if applicable"
    )


class SearchPricing(BaseModel):
    search_context_size_low: float = Field(
        0, description="Estimated cost or latency for small-context search tasks"
    )
    search_context_size_medium: float = Field(
        0, description="Estimated cost or latency for medium-context search tasks"
    )
    search_context_size_high: float = Field(
        0, description="Estimated cost or latency for high-context search tasks"
    )


class Model(BaseModel):
    model_id: str = Field(
        ...,
        description="Unique identifier for the LLM model (e.g., 'gpt-4', 'claude-3-opus')",
    )
    provider: str = Field(
        ..., description="The provider offering the model (must match a provider name)"
    )
    mode: str = Field(
        ..., description="The model's usage mode (e.g., chat, completion, embedding)"
    )
    litellm_provider: str = Field(
        ..., description="Internal identifier for LiteLLM routing or API selection"
    )
    max_tokens: int = Field(
        ..., description="Total maximum tokens (input + output) the model can handle"
    )
    max_input_tokens: int = Field(
        ..., description="Maximum number of tokens that can be sent as input"
    )
    max_output_tokens: int = Field(
        ..., description="Maximum number of tokens that can be generated as output"
    )
    deprecation_date: str | None = Field(
        None, description="Optional deprecation or sunset date for the model"
    )
    capabilities: ModelCapabilities | None = Field(
        None, description="Feature support map for the model"
    )
    pricing: Pricing | None = Field(
        None, description="Pricing information for token or usage cost"
    )
    search_pricing: SearchPricing | None = Field(
        None, description="Search task-related pricing details"
    )
