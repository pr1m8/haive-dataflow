# haive-dataflow/src/haive/dataflow/platform/__init__.py
"""
Platform Package - Unified Platform Architecture for Haive Ecosystem

This package provides the unified platform architecture for the entire Haive ecosystem,
implementing the Pydantic-first design with intelligent inheritance patterns.

Package Structure:
=================

models/
├── base.py      - BasePlatform foundation model
├── mcp.py       - MCPPlatform and MCP-specific models
├── plugins.py   - PluginPlatform for all plugin implementations
└── servers.py   - Server hierarchy (Base -> MCP -> Downloaded)

Architecture Philosophy:
=======================

1. Pure Pydantic Models:
   - No __init__ methods anywhere in the platform
   - All configuration via Field definitions and validators
   - Clean inheritance patterns without method overrides

2. Intelligent Inheritance:
   - BasePlatform provides core platform functionality
   - Specialized platforms inherit and extend capabilities
   - Server hierarchy supports multiple server types
   - Consistent patterns across all platform components

3. Platform-Based Design:
   - Everything inherits from a platform base
   - Platform capabilities are inherited and extended
   - Plugin system built on platform inheritance
   - Server management through platform patterns

4. Real Integration:
   - Works with our 63 downloaded MCP servers
   - Integrates with haive-dataflow registry
   - Supports haive-agp HAP system
   - Factory methods for real data sources

Key Components:
==============

Platform Models:
- BasePlatform: Foundation for all platforms
- MCPPlatform: Specialized for MCP operations
- PluginPlatform: Base for all plugin implementations

Server Models:
- BaseServerInfo: Foundation for all servers
- MCPServerInfo: MCP-specific server information
- DownloadedServerInfo: Our 63 bulk-downloaded servers

Configuration Models:
- PluginConfig: Plugin configuration and metadata
- APIConfig: FastAPI application configuration
- DiscoveryConfig: Service discovery configuration
- ConnectionConfig: Server connection details

Usage Examples:
==============

Platform Creation:
    >>> from haive.dataflow.platform import MCPPlatform
    >>> platform = MCPPlatform()  # Intelligent defaults
    >>> platform.platform_name
    'Haive MCP Platform'
    >>> platform.supports_discovery
    True

Plugin Configuration:
    >>> from haive.dataflow.platform.models import PluginConfig
    >>> plugin = PluginConfig(
    ...     name="mcp-browser",
    ...     entry_point="haive.mcp.plugins:MCPBrowserPlugin"
    ... )
    >>> platform.add_plugin(plugin)

Server Management:
    >>> from haive.dataflow.platform.models import DownloadedServerInfo
    >>> server = DownloadedServerInfo.from_csv_and_install_report(
    ...     csv_data, install_report, "session-20250819"
    ... )
    >>> server.get_mcp_capabilities_summary()
    {'transport': 'stdio', 'source': 'downloaded', ...}

Inheritance Validation:
    >>> from haive.dataflow.platform.models import validate_platform_inheritance
    >>> result = validate_platform_inheritance(platform)
    >>> result['is_base_platform']
    True
    >>> result['platform_type']
    'MCPPlatform'
"""

from .models import (
    # Base platform models
    BasePlatform,
    PlatformStatus,
    
    # Specialized platform models
    MCPPlatform,
    PluginPlatform,
    
    # Server models
    BaseServerInfo,
    MCPServerInfo,
    DownloadedServerInfo,
    
    # Configuration models
    PluginConfig,
    APIConfig,
    DiscoveryConfig,
    ServerManagementConfig,
    ConnectionConfig,
    
    # Enumerations
    MCPTransport,
    ServerSource,
    ServerStatus,
    HealthStatus,
    
    # Support models
    ToolInfo,
    ResourceInfo,
    PromptInfo,
    PerformanceMetrics,
    
    # Utility functions
    validate_platform_inheritance,
    validate_server_inheritance,
    create_mcp_platform_with_plugins,
    create_downloaded_server_from_data,
    get_model_by_name,
    list_available_models,
    
    # Model registry
    MODEL_REGISTRY,
)

__version__ = "1.0.0"
__all__ = [
    # Platform models
    "BasePlatform",
    "PlatformStatus", 
    "MCPPlatform",
    "PluginPlatform",
    
    # Server models
    "BaseServerInfo",
    "MCPServerInfo",
    "DownloadedServerInfo",
    
    # Configuration models
    "PluginConfig",
    "APIConfig", 
    "DiscoveryConfig",
    "ServerManagementConfig",
    "ConnectionConfig",
    
    # Enumerations
    "MCPTransport",
    "ServerSource",
    "ServerStatus", 
    "HealthStatus",
    
    # Support models
    "ToolInfo",
    "ResourceInfo",
    "PromptInfo",
    "PerformanceMetrics",
    
    # Utility functions
    "validate_platform_inheritance",
    "validate_server_inheritance", 
    "create_mcp_platform_with_plugins",
    "create_downloaded_server_from_data",
    "get_model_by_name",
    "list_available_models",
    
    # Registry
    "MODEL_REGISTRY",
]

# Platform summary for debugging and introspection
def get_platform_summary() -> dict:
    """Get comprehensive platform architecture summary.
    
    Returns:
        Dictionary with platform architecture information
        
    Examples:
        >>> summary = get_platform_summary()
        >>> summary['total_models']
        15
        >>> 'BasePlatform' in summary['available_models']
        True
    """
    return {
        "version": __version__,
        "total_models": len(MODEL_REGISTRY),
        "available_models": list(MODEL_REGISTRY.keys()),
        "platform_types": ["BasePlatform", "MCPPlatform", "PluginPlatform"],
        "server_types": ["BaseServerInfo", "MCPServerInfo", "DownloadedServerInfo"],
        "architecture": "Pydantic-first with intelligent inheritance",
        "design_principles": [
            "No __init__ methods",
            "Platform-based inheritance",
            "Pure Pydantic models",
            "Real-world integration",
            "Comprehensive validation"
        ]
    }

# Quick platform factory for common use cases
def create_default_mcp_platform() -> MCPPlatform:
    """Create default MCP platform with common configuration.
    
    Returns:
        MCPPlatform with intelligent defaults
        
    Examples:
        >>> platform = create_default_mcp_platform()
        >>> platform.supports_discovery
        True
        >>> platform.api_config.port
        8080
    """
    return MCPPlatform()

def create_plugin_platform(name: str, entry_point: str, **kwargs) -> PluginPlatform:
    """Create plugin platform with specified configuration.
    
    Args:
        name: Plugin name
        entry_point: Plugin entry point
        **kwargs: Additional plugin configuration
        
    Returns:
        Configured PluginPlatform instance
        
    Examples:
        >>> plugin = create_plugin_platform(
        ...     "my-plugin",
        ...     "mypackage:MyPlugin",
        ...     routes_prefix="/api/my",
        ...     provides_servers=True
        ... )
        >>> plugin.provides_servers
        True
    """
    return PluginPlatform(
        platform_id=name,
        platform_name=name.replace('-', ' ').title(),
        description=f"Platform for {name}",
        entry_point=entry_point,
        routes_prefix=kwargs.pop('routes_prefix', f'/{name}'),
        **kwargs
    )