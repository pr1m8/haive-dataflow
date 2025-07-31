"""Application settings configuration for the Haive framework.

This module defines Pydantic models for application settings, providing
a type-safe and validated configuration system. Settings are automatically
loaded from environment variables with sensible defaults.

The settings hierarchy includes:
- AppSettings: Top-level application settings
- APISettings: API-specific settings
- AgentSettings: Agent-specific settings

Settings can be accessed using the get_settings() function, which returns
a singleton instance of the AppSettings class.

Typical usage example:

    ```python
    from haive.dataflow.config.settings import get_settings

    settings = get_settings()

    # Access settings properties
    api_prefix = settings.api.prefix
    is_production = settings.is_production
    agent_timeout = settings.agent.default_timeout

    # Use in application logic
    if settings.is_development:
        print(f"Running in development mode with debug={settings.api.debug}")
    ```
"""

import os

from pydantic import BaseModel, Field


class APISettings(BaseModel):
    """API-specific settings for the Haive framework.

    This model defines settings specific to the API server, including
    debug mode, CORS configuration, rate limits, and other HTTP-related
    settings. Values are loaded from environment variables with sensible
    defaults.

    Attributes:
        debug: Whether the API is running in debug mode
        title: The title of the API for OpenAPI documentation
        prefix: URL prefix for all API endpoints
        cors_origins: List of allowed origins for CORS
        rate_limit: Maximum requests per minute per client
    """

    debug: bool = Field(
        default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true"
    )
    title: str = Field(default_factory=lambda: os.getenv("API_TITLE", "Haive API"))
    prefix: str = Field(default_factory=lambda: os.getenv("API_PREFIX", "/api"))
    cors_origins: list[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    rate_limit: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT", "60")))


class AgentSettings(BaseModel):
    """Agent-specific settings for the Haive framework.

    This model defines settings specific to agent execution, including
    timeouts, streaming configuration, and usage costs. Values are loaded
    from environment variables with sensible defaults.

    Attributes:
        default_timeout: Default timeout in seconds for agent execution
        streaming_enabled: Whether streaming responses are enabled
        credit_cost_per_1k_tokens: Cost in credits per 1000 tokens processed
    """

    default_timeout: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_TIMEOUT", "60"))
    )
    streaming_enabled: bool = Field(
        default_factory=lambda: os.getenv("AGENT_STREAMING", "true").lower() == "true"
    )
    credit_cost_per_1k_tokens: float = Field(
        default_factory=lambda: float(os.getenv("AGENT_COST_PER_1K", "0.01"))
    )


class AppSettings(BaseModel):
    """Application-wide settings for the Haive framework.

    This is the top-level settings model that includes all other setting
    categories as nested models. It provides properties for determining
    the current environment and accessing environment-specific settings.

    Attributes:
        environment: The current environment (development, staging, production)
        api: API-specific settings
        agent: Agent-specific settings
    """

    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    api: APISettings = Field(default_factory=APISettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


def get_settings() -> AppSettings:
    """Get application settings."""
    return AppSettings()
