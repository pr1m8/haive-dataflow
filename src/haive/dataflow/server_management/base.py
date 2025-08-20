"""Generic base server manager with full type safety.

This module provides the abstract base class for all server managers in Haive.
It uses Python generics to ensure type safety while providing common functionality.
"""

from typing import TypeVar, Generic, Type, Dict, List, Optional, Any, Protocol, Union, runtime_checkable
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, ValidationInfo
import logging
import asyncio
from datetime import datetime

from .models import BaseServerConfig, BaseServerInfo, ServerStatus

logger = logging.getLogger(__name__)

# Type variables for generic server management
ConfigT = TypeVar('ConfigT', bound=BaseServerConfig)
InfoT = TypeVar('InfoT', bound=BaseServerInfo)


@runtime_checkable
class ServerLifecycle(Protocol):
    """Protocol for server lifecycle operations."""
    
    async def start_server(self, name: str, config: Optional[Any] = None) -> Any:
        """Start a server with given configuration."""
        ...
    
    async def stop_server(self, name: str, force: bool = False) -> bool:
        """Stop a running server."""
        ...
    
    async def restart_server(self, name: str) -> Any:
        """Restart a server."""
        ...
    
    async def health_check(self, name: str) -> bool:
        """Check if server is healthy."""
        ...


class BaseServerManager(BaseModel, ABC, Generic[ConfigT, InfoT]):
    """Generic base class for all server managers.
    
    This class provides a type-safe foundation for managing servers of any type.
    Subclasses should specify the concrete ConfigT and InfoT types.
    
    Type Parameters:
        ConfigT: Server configuration type (must extend BaseServerConfig)
        InfoT: Server runtime info type (must extend BaseServerInfo)
        
    Attributes:
        servers: Currently running servers mapped by name
        available_configs: Available server configurations
        config_class: Configuration class for type validation
        info_class: Info class for runtime information
        auto_restart: Whether to automatically restart failed servers
        max_restart_attempts: Maximum restart attempts before giving up
        health_check_interval: Seconds between health checks
        restart_tracking: Tracks restart attempts per server
        
    Example:
        Creating a concrete server manager::
        
            class MyServerManager(BaseServerManager[MyConfig, MyInfo]):
                config_class = Field(default=MyConfig, exclude=True)
                info_class = Field(default=MyInfo, exclude=True)
                
                async def start_server(self, name: str, config: Optional[MyConfig] = None) -> MyInfo:
                    # Implementation
                    pass
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        json_schema_extra={
            "description": "Generic server manager with type-safe configuration"
        }
    )
    
    # Core fields
    servers: Dict[str, InfoT] = Field(
        default_factory=dict,
        description="Currently running servers"
    )
    available_configs: Dict[str, ConfigT] = Field(
        default_factory=dict,
        description="Available server configurations"
    )
    
    # Type information (required by subclasses)
    config_class: Type[ConfigT] = Field(
        ...,
        exclude=True,
        description="Configuration class for validation"
    )
    info_class: Type[InfoT] = Field(
        ...,
        exclude=True,
        description="Info class for runtime data"
    )
    
    # Management settings
    auto_restart: bool = Field(
        default=False,
        description="Automatically restart failed servers"
    )
    max_restart_attempts: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum restart attempts (0-10)"
    )
    health_check_interval: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Health check interval in seconds (10-3600)"
    )
    
    # Internal state
    restart_tracking: Dict[str, int] = Field(
        default_factory=dict,
        exclude=True,
        description="Tracks restart attempts per server"
    )
    health_check_tasks: Dict[str, asyncio.Task] = Field(
        default_factory=dict,
        exclude=True,
        description="Active health check tasks",
        alias="_health_check_tasks"
    )
    
    @field_validator("available_configs", mode="after")
    @classmethod
    def validate_config_types(cls, v: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        """Ensure all configs are the correct type."""
        config_class = info.data.get("config_class")
        if not config_class:
            return v
        
        validated = {}
        for name, config in v.items():
            if not isinstance(config, config_class):
                # Try to coerce to correct type
                try:
                    validated[name] = config_class.model_validate(config)
                    logger.debug(f"Coerced config '{name}' to {config_class.__name__}")
                except Exception as e:
                    raise ValueError(
                        f"Config '{name}' is not valid {config_class.__name__}: {e}"
                    )
            else:
                validated[name] = config
        
        return validated
    
    @field_validator("servers", mode="after")
    @classmethod
    def validate_info_types(cls, v: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        """Ensure all server info objects are the correct type."""
        info_class = info.data.get("info_class")
        if not info_class:
            return v
        
        for name, server_info in v.items():
            if not isinstance(server_info, info_class):
                raise ValueError(
                    f"Server info '{name}' must be instance of {info_class.__name__}"
                )
        
        return v
    
    @model_validator(mode="after")
    def validate_restart_policy(self) -> "BaseServerManager":
        """Validate restart configuration consistency."""
        if self.auto_restart and self.max_restart_attempts == 0:
            raise ValueError("auto_restart=True requires max_restart_attempts > 0")
        
        # Initialize restart tracking for configured servers
        for config_name in self.available_configs:
            if config_name not in self.restart_tracking:
                self.restart_tracking[config_name] = 0
        
        return self
    
    @model_validator(mode="after")
    def validate_server_consistency(self) -> "BaseServerManager":
        """Ensure running servers have configurations."""
        orphaned_servers = set(self.servers.keys()) - set(self.available_configs.keys())
        
        if orphaned_servers:
            logger.warning(
                f"Running servers without configs: {orphaned_servers}. "
                "Creating minimal configs from runtime info."
            )
            
            # Auto-create minimal configs for orphaned servers
            for server_name in orphaned_servers:
                server_info = self.servers[server_name]
                if hasattr(server_info, 'config_snapshot'):
                    # Try to recreate config from snapshot
                    try:
                        config = self.config_class.model_validate(
                            server_info.config_snapshot
                        )
                        self.available_configs[server_name] = config
                    except Exception as e:
                        logger.error(
                            f"Failed to recreate config for '{server_name}': {e}"
                        )
        
        return self
    
    def model_post_init(self, __context: Any) -> None:
        """Additional initialization after validation."""
        super().model_post_init(__context)
        
        # Log initialization
        logger.info(
            f"Initialized {self.__class__.__name__} with "
            f"{len(self.available_configs)} configs and "
            f"{len(self.servers)} running servers"
        )
    
    # Configuration management
    
    def add_config(self, name: str, config: Union[ConfigT, Dict[str, Any]]) -> ConfigT:
        """Add or update a server configuration.
        
        Args:
            name: Server name
            config: Configuration object or dict
            
        Returns:
            Validated configuration object
            
        Raises:
            ValidationError: If configuration is invalid
        """
        # Validate and convert if needed
        if isinstance(config, dict):
            # Add name to dict before validation
            config['name'] = name
            config = self.config_class.model_validate(config)
        elif isinstance(config, BaseServerConfig):
            # Check if it's the correct subclass
            if not isinstance(config, self.config_class):
                raise TypeError(
                    f"Config must be {self.config_class.__name__} or dict, "
                    f"got {type(config).__name__}"
                )
            # Ensure name matches for existing config object
            config.name = name
        else:
            raise TypeError(
                f"Config must be {self.config_class.__name__} or dict, "
                f"got {type(config).__name__}"
            )
        self.available_configs[name] = config
        
        logger.info(f"Added configuration for server '{name}'")
        return config
    
    def remove_config(self, name: str) -> bool:
        """Remove a server configuration.
        
        Args:
            name: Server name
            
        Returns:
            True if removed, False if not found
            
        Raises:
            RuntimeError: If server is currently running
        """
        if name in self.servers:
            raise RuntimeError(
                f"Cannot remove config for running server '{name}'. "
                "Stop the server first."
            )
        
        if name in self.available_configs:
            del self.available_configs[name]
            # Clean up restart tracking
            self.restart_tracking.pop(name, None)
            logger.info(f"Removed configuration for server '{name}'")
            return True
        
        return False
    
    def get_config(self, name: str) -> Optional[ConfigT]:
        """Get server configuration by name.
        
        Args:
            name: Server name
            
        Returns:
            Configuration object or None if not found
        """
        return self.available_configs.get(name)
    
    # Server lifecycle (abstract methods)
    
    @abstractmethod
    async def start_server(self, name: str, config: Optional[ConfigT] = None) -> InfoT:
        """Start a server with given configuration.
        
        Args:
            name: Server name
            config: Optional configuration override
            
        Returns:
            Server runtime information
            
        Raises:
            ValueError: If no configuration found
            RuntimeError: If server already running
        """
        raise NotImplementedError
    
    @abstractmethod
    async def stop_server(self, name: str, force: bool = False) -> bool:
        """Stop a running server.
        
        Args:
            name: Server name
            force: Force stop if true
            
        Returns:
            True if stopped successfully
        """
        raise NotImplementedError
    
    @abstractmethod
    async def restart_server(self, name: str) -> InfoT:
        """Restart a server.
        
        Args:
            name: Server name
            
        Returns:
            New server runtime information
        """
        raise NotImplementedError
    
    @abstractmethod
    async def health_check(self, name: str) -> bool:
        """Check if server is healthy.
        
        Args:
            name: Server name
            
        Returns:
            True if healthy, False otherwise
        """
        raise NotImplementedError
    
    # Helper methods
    
    def get_server_info(self, name: str) -> Optional[InfoT]:
        """Get runtime information for a server.
        
        Args:
            name: Server name
            
        Returns:
            Server info or None if not running
        """
        return self.servers.get(name)
    
    def is_running(self, name: str) -> bool:
        """Check if server is running.
        
        Args:
            name: Server name
            
        Returns:
            True if server is running
        """
        info = self.get_server_info(name)
        return info is not None and info.is_running
    
    def list_servers(self, status: Optional[ServerStatus] = None) -> List[str]:
        """List servers by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of server names
        """
        if status is None:
            return list(self.servers.keys())
        
        return [
            name for name, info in self.servers.items()
            if info.status == status
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server manager statistics.
        
        Returns:
            Dictionary with stats including:
            - total_configured: Number of configured servers
            - total_running: Number of running servers
            - servers_by_status: Count by status
            - restart_counts: Restart attempts per server
        """
        status_counts = {}
        for info in self.servers.values():
            status_counts[info.status.value] = status_counts.get(info.status.value, 0) + 1
        
        return {
            "total_configured": len(self.available_configs),
            "total_running": len(self.servers),
            "servers_by_status": status_counts,
            "restart_counts": dict(self.restart_tracking),
            "health_check_active": len(self.health_check_tasks)
        }
    
    async def start_health_monitoring(self, name: str) -> None:
        """Start health monitoring for a server.
        
        Args:
            name: Server name
        """
        if name in self.health_check_tasks:
            # Cancel existing task
            self.health_check_tasks[name].cancel()
        
        async def monitor_health():
            """Health check loop."""
            while name in self.servers:
                try:
                    await asyncio.sleep(self.health_check_interval)
                    
                    if not await self.health_check(name):
                        logger.warning(f"Health check failed for '{name}'")
                        
                        if self.auto_restart:
                            await self._handle_server_failure(name)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in health check for '{name}': {e}")
        
        # Start monitoring task
        self.health_check_tasks[name] = asyncio.create_task(monitor_health())
        logger.debug(f"Started health monitoring for '{name}'")
    
    async def stop_health_monitoring(self, name: str) -> None:
        """Stop health monitoring for a server.
        
        Args:
            name: Server name
        """
        if name in self.health_check_tasks:
            self.health_check_tasks[name].cancel()
            del self.health_check_tasks[name]
            logger.debug(f"Stopped health monitoring for '{name}'")
    
    async def _handle_server_failure(self, name: str) -> None:
        """Handle server failure with restart logic.
        
        Args:
            name: Server name
        """
        restart_count = self.restart_tracking.get(name, 0)
        
        if restart_count >= self.max_restart_attempts:
            logger.error(
                f"Server '{name}' exceeded max restart attempts ({self.max_restart_attempts})"
            )
            # Update server status to error
            if name in self.servers:
                self.servers[name].update_status(
                    ServerStatus.ERROR,
                    f"Exceeded max restart attempts ({self.max_restart_attempts})"
                )
            return
        
        # Attempt restart
        logger.info(f"Attempting restart {restart_count + 1}/{self.max_restart_attempts} for '{name}'")
        self.restart_tracking[name] = restart_count + 1
        
        try:
            await self.restart_server(name)
            # Reset counter on successful restart
            self.restart_tracking[name] = 0
            logger.info(f"Successfully restarted server '{name}'")
        except Exception as e:
            logger.error(f"Failed to restart server '{name}': {e}")
            if name in self.servers:
                self.servers[name].update_status(ServerStatus.ERROR, str(e))
    
    async def cleanup(self) -> None:
        """Clean up resources and stop all servers."""
        logger.info(f"Cleaning up {self.__class__.__name__}")
        
        # Cancel all health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        self.health_check_tasks.clear()
        
        # Stop all running servers
        server_names = list(self.servers.keys())
        for name in server_names:
            try:
                await self.stop_server(name, force=True)
            except Exception as e:
                logger.error(f"Error stopping server '{name}' during cleanup: {e}")
        
        logger.info("Cleanup completed")