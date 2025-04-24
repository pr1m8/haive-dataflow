# haive_dataflow/config/settings.py
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class APISettings(BaseModel):
    """API-specific settings."""
    debug: bool = Field(default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true")
    title: str = Field(default_factory=lambda: os.getenv("API_TITLE", "Haive API"))
    prefix: str = Field(default_factory=lambda: os.getenv("API_PREFIX", "/api"))
    cors_origins: List[str] = Field(default_factory=lambda: 
        os.getenv("CORS_ORIGINS", "*").split(","))
    rate_limit: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT", "60")))

class AgentSettings(BaseModel):
    """Agent-specific settings."""
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
    """Application-wide settings."""
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
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