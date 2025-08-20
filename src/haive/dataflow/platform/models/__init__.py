# haive-dataflow/src/haive/dataflow/platform/models/__init__.py
"""
Platform Models - Pydantic-First Architecture with Intelligent Inheritance

This module provides the complete set of platform models for the unified Haive ecosystem.
All models use pure Pydantic architecture with no __init__ methods and intelligent
inheritance patterns.

Architecture Overview:
===================

Base Platform Layer:
- BasePlatform: Foundation for all platform models
- PlatformStatus: Common status enumeration

Specialized Platforms:
- MCPPlatform: MCP-specific platform (inherits BasePlatform)
- PluginPlatform: Base for all plugins (inherits BasePlatform)

Server Hierarchy:
- BaseServerInfo: Foundation for all servers
- MCPServerInfo: MCP-specific servers (inherits BaseServerInfo)
- DownloadedServerInfo: Our 63 downloaded servers (inherits MCPServerInfo)

Configuration Models:
- PluginConfig: Plugin configuration
- APIConfig: FastAPI configuration
- DiscoveryConfig: Service discovery configuration
- ConnectionConfig: Server connection configuration

Enumerations:
- ServerSource: Where servers come from
- ServerStatus: Server operational status
- MCPTransport: MCP transport protocols
- HealthStatus: Health check status

Key Features:
============

1. Pure Pydantic Models:
   - No __init__ methods anywhere
   - All configuration via Field definitions
   - Comprehensive validation through field validators
   - Clean inheritance patterns

2. Intelligent Inheritance:
   - BasePlatform provides core platform functionality
   - Specialized platforms extend with domain-specific features
   - Server hierarchy supports multiple server types
   - Consistent patterns across all models

3. Real-World Integration:
   - DownloadedServerInfo works with our 63 downloaded servers
   - Factory methods for creating from CSV and install report data
   - Connection configurations for actual server types

4. Comprehensive Validation:
   - Field validators for IDs, URLs, versions
   - Cross-field validation where needed
   - Sensible defaults and examples

Usage Examples:
==============

Basic Platform Creation:
    >>> from haive.dataflow.platform.models import MCPPlatform
    >>> platform = MCPPlatform()  # Uses intelligent defaults
    >>> print(platform.platform_name)
    "Haive MCP Platform"

Plugin Configuration:
    >>> from haive.dataflow.platform.models import PluginConfig
    >>> plugin = PluginConfig(
    ...     name="mcp-browser",
    ...     entry_point="haive.mcp.plugins:MCPBrowserPlugin"
    ... )

Server from Download Data:
    >>> from haive.dataflow.platform.models import DownloadedServerInfo
    >>> server = DownloadedServerInfo.from_csv_and_install_report(
    ...     csv_data, install_report, "session-123"
    ... )

Inheritance Validation:
    >>> isinstance(platform, BasePlatform)  # True
    >>> isinstance(server, BaseServerInfo)  # True
    >>> isinstance(server, MCPServerInfo)   # True
"""

# Base platform models
from .base import BasePlatform, PlatformStatus

# MCP platform models
from .mcp import (
    MCPPlatform,
    MCPTransport,
    ServerSource,
    ServerStatus,
    HealthStatus,
    PluginConfig,
    APIConfig,
    DiscoveryConfig,
    ServerManagementConfig,
)

# Plugin platform models
from .plugins import PluginPlatform

# Server models with inheritance hierarchy
from .servers import (
    BaseServerInfo,
    MCPServerInfo,
    DownloadedServerInfo,
    ConnectionConfig,
    ToolInfo,
    ResourceInfo,
    PromptInfo,
    PerformanceMetrics,
)

# Version and metadata
__version__ = "1.0.0"
__all__ = [
    # Base models
    "BasePlatform",
    "PlatformStatus",
    
    # MCP models
    "MCPPlatform",
    "MCPTransport",
    "ServerSource", 
    "ServerStatus",
    "HealthStatus",
    "PluginConfig",
    "APIConfig",
    "DiscoveryConfig",
    "ServerManagementConfig",
    
    # Plugin models
    "PluginPlatform",
    
    # Server models
    "BaseServerInfo",
    "MCPServerInfo", 
    "DownloadedServerInfo",
    "ConnectionConfig",
    "ToolInfo",
    "ResourceInfo",
    "PromptInfo",
    "PerformanceMetrics",
]

# Export inheritance validation helpers
def validate_platform_inheritance(instance) -> dict:
    """Validate platform inheritance chain.
    
    Args:
        instance: Platform instance to validate
        
    Returns:
        Dictionary showing inheritance validation results
        
    Examples:
        >>> platform = MCPPlatform()
        >>> result = validate_platform_inheritance(platform)
        >>> result['is_base_platform']
        True
        >>> result['platform_type']
        'MCPPlatform'
    """
    return {
        "is_base_platform": isinstance(instance, BasePlatform),
        "is_mcp_platform": isinstance(instance, MCPPlatform),
        "is_plugin_platform": isinstance(instance, PluginPlatform),
        "platform_type": instance.__class__.__name__,
        "platform_id": getattr(instance, 'platform_id', None),
        "inheritance_chain": [cls.__name__ for cls in instance.__class__.__mro__[:-1]]
    }

def validate_server_inheritance(instance) -> dict:
    """Validate server inheritance chain.
    
    Args:
        instance: Server instance to validate
        
    Returns:
        Dictionary showing server inheritance validation results
        
    Examples:
        >>> server = DownloadedServerInfo(...)
        >>> result = validate_server_inheritance(server)
        >>> result['inheritance_depth']
        3  # BaseServerInfo -> MCPServerInfo -> DownloadedServerInfo
    """
    return {
        "is_base_server": isinstance(instance, BaseServerInfo),
        "is_mcp_server": isinstance(instance, MCPServerInfo),
        "is_downloaded_server": isinstance(instance, DownloadedServerInfo),
        "server_type": instance.__class__.__name__,
        "server_id": getattr(instance, 'server_id', None),
        "inheritance_chain": [cls.__name__ for cls in instance.__class__.__mro__[:-1]],
        "inheritance_depth": len([cls for cls in instance.__class__.__mro__ if 'Server' in cls.__name__])
    }

# Convenience factory functions
def create_mcp_platform_with_plugins(plugin_configs: list) -> MCPPlatform:
    """Create MCP platform with plugin configurations.
    
    Args:
        plugin_configs: List of plugin configuration dictionaries
        
    Returns:
        Configured MCPPlatform instance
        
    Examples:
        >>> plugins = [
        ...     {"name": "mcp-browser", "entry_point": "haive.mcp:MCPBrowserPlugin"},
        ...     {"name": "hap-agents", "entry_point": "haive.agp:HAPPlugin"}
        ... ]
        >>> platform = create_mcp_platform_with_plugins(plugins)
        >>> len(platform.plugins)
        2
    """
    plugins = [PluginConfig(**config) for config in plugin_configs]
    return MCPPlatform(plugins=plugins)

def create_downloaded_server_from_data(
    csv_row: dict,
    install_report: dict,
    session_id: str
) -> DownloadedServerInfo:
    """Create downloaded server from real download data.
    
    Args:
        csv_row: CSV data row from our server database
        install_report: Install report entry
        session_id: Bulk install session ID
        
    Returns:
        DownloadedServerInfo instance
        
    Examples:
        >>> server = create_downloaded_server_from_data(
        ...     {"name": "test/server", "description": "Test server"},
        ...     {"command": "npx test-server", "status": "success"},
        ...     "session-123"
        ... )
        >>> server.source
        <ServerSource.DOWNLOADED: 'downloaded'>
    """
    return DownloadedServerInfo.from_csv_and_install_report(
        csv_row, install_report, session_id
    )

# Model registry for dynamic loading
MODEL_REGISTRY = {
    "BasePlatform": BasePlatform,
    "MCPPlatform": MCPPlatform,
    "PluginPlatform": PluginPlatform,
    "BaseServerInfo": BaseServerInfo,
    "MCPServerInfo": MCPServerInfo,
    "DownloadedServerInfo": DownloadedServerInfo,
    "PluginConfig": PluginConfig,
    "APIConfig": APIConfig,
    "DiscoveryConfig": DiscoveryConfig,
    "ConnectionConfig": ConnectionConfig,
}

def get_model_by_name(model_name: str):
    """Get model class by name.
    
    Args:
        model_name: Name of the model class
        
    Returns:
        Model class if found, None otherwise
        
    Examples:
        >>> cls = get_model_by_name("MCPPlatform")
        >>> cls.__name__
        'MCPPlatform'
    """
    return MODEL_REGISTRY.get(model_name)

def list_available_models() -> list:
    """List all available model names.
    
    Returns:
        List of available model class names
    """
    return list(MODEL_REGISTRY.keys())