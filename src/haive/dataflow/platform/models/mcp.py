# haive-dataflow/src/haive/dataflow/platform/models/mcp.py
"""
MCP Platform Models - Specialized Platform for MCP Operations

This module provides specialized platform models for MCP (Model Context Protocol) operations,
inheriting from BasePlatform and extending with MCP-specific capabilities.

Key Features:
- Inherits all BasePlatform capabilities
- MCP-specific configuration and capabilities
- Plugin management system
- API and discovery configuration
- Server management capabilities
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import BasePlatform, PlatformStatus


class MCPTransport(str, Enum):
    """MCP transport protocols."""
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"
    WEBSOCKET = "websocket"


class ServerSource(str, Enum):
    """Where the server came from."""
    DOWNLOADED = "downloaded"  # Our 63 bulk downloaded servers
    REGISTRY = "registry"      # haive-dataflow registry
    HAP_AGENT = "hap_agent"    # haive-agp exposed agents
    NPM_PACKAGE = "npm"        # npm installed
    PIP_PACKAGE = "pip"        # pip installed
    LOCAL_CONFIG = "config"    # Local configuration
    DISCOVERED = "discovered"  # Auto-discovered


class ServerStatus(str, Enum):
    """Server operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


class PluginConfig(BaseModel):
    """Plugin configuration model."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(..., description="Plugin unique name")
    entry_point: str = Field(..., description="Plugin entry point in format 'module:class'")
    enabled: bool = Field(default=True, description="Whether plugin is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific configuration")
    routes_prefix: str = Field(default="", description="API routes prefix for plugin")
    priority: int = Field(default=100, description="Loading priority (lower = first)")
    
    @field_validator("entry_point")
    @classmethod
    def validate_entry_point(cls, v: str) -> str:
        """Validate entry point format."""
        if ":" not in v:
            raise ValueError("Entry point must be in format 'module:class'")
        return v


class APIConfig(BaseModel):
    """FastAPI application configuration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    title: str = Field(default="Haive MCP Platform", description="API title")
    description: str = Field(
        default="Unified MCP management across the Haive ecosystem",
        description="API description"
    )
    version: str = Field(default="1.0.0", description="API version")
    host: str = Field(default="0.0.0.0", description="API host address")
    port: int = Field(default=8080, description="API port", ge=1, le=65535)
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins"
    )
    
    # Additional API configuration
    docs_url: str = Field(default="/docs", description="OpenAPI docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI schema URL")


class DiscoveryConfig(BaseModel):
    """Discovery system configuration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    auto_discover: bool = Field(default=True, description="Enable automatic discovery")
    scan_intervals: Dict[str, int] = Field(
        default_factory=lambda: {
            "local_servers": 300,    # 5 minutes
            "registry_servers": 600, # 10 minutes
            "health_checks": 120     # 2 minutes
        },
        description="Discovery scan intervals in seconds"
    )
    discovery_sources: List[str] = Field(
        default_factory=lambda: [
            "downloaded_servers",  # Our 63 servers
            "registry_entities",   # haive-dataflow registry
            "hap_agents",         # haive-agp HAP servers
            "npm_packages",
            "pip_packages"
        ],
        description="Sources to scan for servers"
    )
    max_concurrent_scans: int = Field(default=10, description="Max concurrent discovery scans")
    timeout_seconds: int = Field(default=30, description="Discovery timeout per source")


class ServerManagementConfig(BaseModel):
    """Server management configuration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    auto_start: bool = Field(default=False, description="Auto-start servers on platform startup")
    max_servers: int = Field(default=100, description="Maximum number of concurrent servers")
    health_check_interval: int = Field(default=60, description="Health check interval in seconds")
    restart_on_failure: bool = Field(default=True, description="Restart servers on failure")
    max_restart_attempts: int = Field(default=3, description="Maximum restart attempts")
    startup_timeout: int = Field(default=60, description="Server startup timeout in seconds")


class MCPPlatform(BasePlatform):
    """Specialized platform for MCP operations - inherits all base capabilities.
    
    This platform extends BasePlatform with MCP-specific functionality:
    - Plugin management system
    - Server discovery and management
    - API configuration
    - MCP transport protocol support
    
    Inheritance Features:
    - Inherits all BasePlatform fields and validation
    - Extends capability flags with MCP-specific ones
    - Adds MCP-specific configuration models
    - Maintains platform inheritance patterns
    
    Examples:
        Basic MCP platform::
        
            platform = MCPPlatform()
            # Uses all defaults, inherits platform_id from class default
            
        With custom plugins::
        
            platform = MCPPlatform(
                plugins=[
                    PluginConfig(
                        name="mcp-browser",
                        entry_point="haive.mcp:MCPBrowserPlugin"
                    ),
                    PluginConfig(
                        name="hap-agents",
                        entry_point="haive.agp:HAPPlugin"
                    )
                ]
            )
            
        Full configuration::
        
            platform = MCPPlatform(
                platform_id="production-mcp",
                platform_name="Production MCP Platform",
                description="Production MCP management system",
                api_config=APIConfig(host="mcp.company.com", port=443),
                discovery_config=DiscoveryConfig(auto_discover=True)
            )
    """
    
    # Override base platform identification with MCP defaults
    platform_id: str = Field(default="haive-mcp-platform")
    platform_name: str = Field(default="Haive MCP Platform")
    description: str = Field(default="Unified MCP management across the Haive ecosystem")
    
    # MCP-specific capabilities (inherited base + new)
    supports_discovery: bool = Field(default=True)  # Override base default
    supports_health_monitoring: bool = Field(default=True)  # Override base default
    supports_authentication: bool = Field(default=True)  # Override base default
    supports_server_management: bool = Field(default=True, description="MCP server lifecycle management")
    supports_tool_execution: bool = Field(default=True, description="MCP tool execution")
    supports_bulk_operations: bool = Field(default=True, description="Bulk server operations")
    
    # MCP-specific configuration
    plugins: List[PluginConfig] = Field(
        default_factory=list,
        description="Configured plugins for the platform"
    )
    api_config: APIConfig = Field(
        default_factory=APIConfig,
        description="FastAPI application configuration"
    )
    discovery_config: DiscoveryConfig = Field(
        default_factory=DiscoveryConfig,
        description="Service discovery configuration"
    )
    server_management_config: ServerManagementConfig = Field(
        default_factory=ServerManagementConfig,
        description="Server management configuration"
    )
    
    @field_validator("plugins")
    @classmethod
    def validate_plugins_unique(cls, v: List[PluginConfig]) -> List[PluginConfig]:
        """Ensure plugin names are unique.
        
        Args:
            v: List of plugin configurations
            
        Returns:
            Validated plugin list
            
        Raises:
            ValueError: If duplicate plugin names found
        """
        names = [plugin.name for plugin in v]
        if len(names) != len(set(names)):
            duplicate_names = [name for name in set(names) if names.count(name) > 1]
            raise ValueError(f"Duplicate plugin names found: {', '.join(duplicate_names)}")
        return v
    
    def add_plugin(self, plugin_config: PluginConfig) -> None:
        """Add a plugin to the platform.
        
        Args:
            plugin_config: Plugin configuration to add
            
        Raises:
            ValueError: If plugin name already exists
        """
        existing_names = [p.name for p in self.plugins]
        if plugin_config.name in existing_names:
            raise ValueError(f"Plugin '{plugin_config.name}' already exists")
        
        self.plugins.append(plugin_config)
        self.updated_at = datetime.utcnow()
        self.add_metadata("last_plugin_added", plugin_config.name)
    
    def remove_plugin(self, plugin_name: str) -> bool:
        """Remove a plugin from the platform.
        
        Args:
            plugin_name: Name of plugin to remove
            
        Returns:
            True if plugin was removed, False if not found
        """
        original_count = len(self.plugins)
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
        
        if len(self.plugins) < original_count:
            self.updated_at = datetime.utcnow()
            self.add_metadata("last_plugin_removed", plugin_name)
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginConfig]:
        """Get plugin configuration by name.
        
        Args:
            plugin_name: Name of plugin to find
            
        Returns:
            Plugin configuration if found, None otherwise
        """
        return next((p for p in self.plugins if p.name == plugin_name), None)
    
    def get_enabled_plugins(self) -> List[PluginConfig]:
        """Get list of enabled plugins.
        
        Returns:
            List of enabled plugin configurations
        """
        return [p for p in self.plugins if p.enabled]
    
    def get_mcp_capability_summary(self) -> Dict[str, bool]:
        """Get summary of MCP-specific capabilities.
        
        Returns:
            Dictionary mapping MCP capability names to their status
        """
        base_capabilities = self.get_capability_summary()
        mcp_capabilities = {
            "server_management": self.supports_server_management,
            "tool_execution": self.supports_tool_execution,
            "bulk_operations": self.supports_bulk_operations,
        }
        return {**base_capabilities, **mcp_capabilities}