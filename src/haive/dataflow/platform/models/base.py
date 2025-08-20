# haive-dataflow/src/haive/dataflow/platform/models/base.py
"""
Base Platform Models - Foundation Layer

This module provides the foundation platform model for all Haive systems with intelligent inheritance patterns.
All platform models inherit from BasePlatform to ensure consistent behavior and capabilities.

Key Features:
- Pure Pydantic models (no __init__ methods)
- Platform-based inheritance architecture
- Intelligent design patterns with composition
- Comprehensive validation and field management
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlatformStatus(str, Enum):
    """Platform operational status."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    INACTIVE = "inactive"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class BasePlatform(BaseModel):
    """Foundation platform model for all Haive systems.
    
    This is the base class that all platform models inherit from, providing:
    - Core platform identification and metadata
    - Standard configuration and state management
    - Lifecycle tracking (created_at, updated_at, status)
    - Capability flags for different platform features
    - Comprehensive validation for platform fields
    
    Design Philosophy:
    - Pure Pydantic model (no __init__ method)
    - All configuration via Field definitions
    - Validation through field validators
    - Extensible through inheritance
    
    Examples:
        Basic platform creation::
        
            platform = BasePlatform(
                platform_id="my-platform",
                platform_name="My Platform",
                description="A sample platform"
            )
            
        With capabilities::
        
            platform = BasePlatform(
                platform_id="advanced-platform", 
                platform_name="Advanced Platform",
                description="Platform with enhanced capabilities",
                supports_discovery=True,
                supports_health_monitoring=True,
                supports_authentication=True
            )
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        json_schema_extra={
            "examples": [
                {
                    "platform_id": "haive-platform",
                    "platform_name": "Haive Platform",
                    "description": "Core Haive platform instance",
                    "supports_discovery": True,
                    "supports_health_monitoring": True
                }
            ]
        }
    )
    
    # Core platform identification
    platform_id: str = Field(
        ..., 
        description="Unique platform identifier (lowercase alphanumeric with - and _)",
        examples=["haive-mcp-platform", "haive_dataflow_v2"]
    )
    platform_name: str = Field(
        ...,
        description="Human-readable platform name",
        examples=["Haive MCP Platform", "Haive Dataflow Registry"]
    )
    version: str = Field(
        default="1.0.0",
        description="Platform version following semantic versioning (X.Y.Z)",
        examples=["1.0.0", "2.1.3", "1.0.0-beta.1"]
    )
    description: str = Field(
        ...,
        description="Detailed platform description",
        examples=["Unified MCP management platform", "Enterprise data flow orchestrator"]
    )
    
    # Core platform capabilities - subclasses can override defaults
    supports_discovery: bool = Field(
        default=False,
        description="Whether platform supports service/resource discovery"
    )
    supports_health_monitoring: bool = Field(
        default=False,
        description="Whether platform supports health check monitoring"
    )
    supports_authentication: bool = Field(
        default=False,
        description="Whether platform supports authentication mechanisms"
    )
    supports_caching: bool = Field(
        default=False,
        description="Whether platform supports caching mechanisms"
    )
    
    # Configuration and state management
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Platform-specific configuration settings"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional platform metadata"
    )
    
    # Timestamps and lifecycle tracking
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Platform creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last platform update timestamp"
    )
    status: PlatformStatus = Field(
        default=PlatformStatus.INITIALIZING,
        description="Current platform operational status"
    )
    
    @field_validator("platform_id")
    @classmethod
    def validate_platform_id(cls, v: str) -> str:
        """Validate platform ID format.
        
        Platform IDs must be:
        - Lowercase only
        - Alphanumeric characters
        - Hyphens (-) and underscores (_) allowed
        - No spaces or special characters
        
        Args:
            v: Platform ID to validate
            
        Returns:
            Validated platform ID
            
        Raises:
            ValueError: If platform ID format is invalid
        """
        if not re.match(r'^[a-z0-9_-]+$', v):
            raise ValueError("Platform ID must be lowercase alphanumeric with - and _")
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate semantic version format.
        
        Versions must follow semantic versioning (semver) format:
        - MAJOR.MINOR.PATCH
        - Optional pre-release: 1.0.0-beta.1
        - Optional build metadata: 1.0.0+20210101
        
        Args:
            v: Version string to validate
            
        Returns:
            Validated version string
            
        Raises:
            ValueError: If version format is invalid
        """
        if not re.match(r'^\d+\.\d+\.\d+', v):
            raise ValueError("Version must follow semantic versioning (X.Y.Z)")
        return v
    
    def update_status(self, new_status: PlatformStatus, update_timestamp: bool = True) -> None:
        """Update platform status and optionally timestamp.
        
        Args:
            new_status: New platform status
            update_timestamp: Whether to update the updated_at timestamp
        """
        self.status = new_status
        if update_timestamp:
            self.updated_at = datetime.utcnow()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry to platform.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_capability_summary(self) -> Dict[str, bool]:
        """Get summary of all platform capabilities.
        
        Returns:
            Dictionary mapping capability names to their status
        """
        return {
            "discovery": self.supports_discovery,
            "health_monitoring": self.supports_health_monitoring,
            "authentication": self.supports_authentication,
            "caching": self.supports_caching,
        }