"""Protocol definitions for server management interfaces.

This module defines the protocols (interfaces) that server managers should implement,
enabling type checking and ensuring consistent API across implementations.
"""

from typing import Protocol, Dict, List, Optional, Any, Union, runtime_checkable
from abc import abstractmethod

from .models import BaseServerConfig, BaseServerInfo, ServerStatus


@runtime_checkable
class ServerManagerProtocol(Protocol):
    """Protocol defining the server manager interface.
    
    This protocol ensures all server managers implement the required methods
    for managing server lifecycles, regardless of the specific server type.
    """
    
    # Required attributes
    servers: Dict[str, BaseServerInfo]
    available_configs: Dict[str, BaseServerConfig]
    
    # Configuration management
    
    def add_config(self, name: str, config: Union[BaseServerConfig, Dict[str, Any]]) -> BaseServerConfig:
        """Add or update a server configuration."""
        ...
    
    def remove_config(self, name: str) -> bool:
        """Remove a server configuration."""
        ...
    
    def get_config(self, name: str) -> Optional[BaseServerConfig]:
        """Get server configuration by name."""
        ...
    
    # Server lifecycle
    
    @abstractmethod
    async def start_server(self, name: str, config: Optional[BaseServerConfig] = None) -> BaseServerInfo:
        """Start a server with given configuration."""
        ...
    
    @abstractmethod
    async def stop_server(self, name: str, force: bool = False) -> bool:
        """Stop a running server."""
        ...
    
    @abstractmethod
    async def restart_server(self, name: str) -> BaseServerInfo:
        """Restart a server."""
        ...
    
    @abstractmethod
    async def health_check(self, name: str) -> bool:
        """Check if server is healthy."""
        ...
    
    # Query methods
    
    def get_server_info(self, name: str) -> Optional[BaseServerInfo]:
        """Get runtime information for a server."""
        ...
    
    def is_running(self, name: str) -> bool:
        """Check if server is running."""
        ...
    
    def list_servers(self, status: Optional[ServerStatus] = None) -> List[str]:
        """List servers by status."""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server manager statistics."""
        ...
    
    # Resource management
    
    async def cleanup(self) -> None:
        """Clean up resources and stop all servers."""
        ...


@runtime_checkable
class HealthMonitorProtocol(Protocol):
    """Protocol for health monitoring capabilities."""
    
    async def start_health_monitoring(self, name: str) -> None:
        """Start health monitoring for a server."""
        ...
    
    async def stop_health_monitoring(self, name: str) -> None:
        """Stop health monitoring for a server."""
        ...


@runtime_checkable
class ConfigLoaderProtocol(Protocol):
    """Protocol for configuration loading capabilities."""
    
    async def load_configs_from_file(self, path: str) -> Dict[str, BaseServerConfig]:
        """Load server configurations from a file."""
        ...
    
    async def save_configs_to_file(self, path: str) -> None:
        """Save current configurations to a file."""
        ...


@runtime_checkable
class ServerDiscoveryProtocol(Protocol):
    """Protocol for server discovery capabilities."""
    
    async def discover_servers(self) -> List[BaseServerInfo]:
        """Discover running servers not managed by this instance."""
        ...
    
    async def adopt_server(self, server_info: BaseServerInfo) -> bool:
        """Adopt an externally started server."""
        ...


@runtime_checkable
class MetricsProtocol(Protocol):
    """Protocol for metrics collection capabilities."""
    
    def get_server_metrics(self, name: str) -> Dict[str, float]:
        """Get metrics for a specific server."""
        ...
    
    def get_aggregate_metrics(self) -> Dict[str, float]:
        """Get aggregated metrics for all servers."""
        ...
    
    async def export_metrics(self, exporter: str) -> None:
        """Export metrics to external system."""
        ...