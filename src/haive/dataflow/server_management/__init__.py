"""Server management framework for Haive.

This module provides a generic, type-safe server management framework using Pydantic
models and validation. It serves as the foundation for managing various types of
servers (MCP, HAP, Docker, etc.) across the Haive ecosystem.

Key Features:
- Generic base classes with full type safety
- Pydantic validation for all configurations
- Extensible architecture for different server types
- Smart defaults and auto-configuration
- Comprehensive error handling with clear messages

Example:
    Basic usage with MCP servers::
    
        from haive.dataflow.server_management import BaseServerManager
        from haive.mcp.servers import MCPServerConfig, MCPServerInfo
        
        class MCPServerManager(BaseServerManager[MCPServerConfig, MCPServerInfo]):
            config_class = Field(default=MCPServerConfig, exclude=True)
            info_class = Field(default=MCPServerInfo, exclude=True)
            
            async def start_server(self, name: str, config: Optional[MCPServerConfig] = None) -> MCPServerInfo:
                # Implementation
                pass
"""

from .models import (
    ServerStatus,
    BaseServerConfig, 
    BaseServerInfo,
)
from .base import BaseServerManager
from .protocols import (
    ServerManagerProtocol,
    HealthMonitorProtocol,
    ConfigLoaderProtocol,
    ServerDiscoveryProtocol,
    MetricsProtocol,
)

__all__ = [
    # Enums
    "ServerStatus",
    
    # Models
    "BaseServerConfig",
    "BaseServerInfo",
    
    # Base classes
    "BaseServerManager",
    
    # Protocols
    "ServerManagerProtocol",
    "HealthMonitorProtocol",
    "ConfigLoaderProtocol",
    "ServerDiscoveryProtocol",
    "MetricsProtocol",
]