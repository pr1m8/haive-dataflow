# haive-dataflow/src/haive/dataflow/platform/models/plugins.py
"""
Plugin Platform Models - Base Platform for All Plugins

This module provides the plugin platform model that serves as the foundation for all
plugin implementations across the Haive ecosystem, using intelligent inheritance patterns.

Key Features:
- Inherits from BasePlatform for core platform capabilities
- Plugin-specific extensions and lifecycle management
- Provides servers, tools, resources, and discovery capabilities
- Async initialization and cleanup methods
- Comprehensive validation for plugin configuration
"""

from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import BasePlatform, PlatformStatus


class PluginPlatform(BasePlatform):
    """Base platform for all plugins - intelligent inheritance from BasePlatform.
    
    This platform serves as the foundation for all plugin implementations in the Haive ecosystem.
    It inherits all BasePlatform capabilities and extends them with plugin-specific functionality.
    
    Inheritance Architecture:
    - Inherits: platform_id, platform_name, config, metadata, timestamps from BasePlatform
    - Extends: Plugin-specific entry points, routes, priorities, dependencies
    - Adds: Plugin capabilities (servers, tools, resources, discovery)
    - Provides: Async lifecycle methods (initialize, cleanup)
    
    Plugin Capabilities:
    - provides_servers: Plugin manages MCP servers
    - provides_tools: Plugin provides tools for agents
    - provides_resources: Plugin offers resources (files, data, etc.)
    - provides_discovery: Plugin participates in service discovery
    - provides_health_checks: Plugin provides health monitoring
    
    Lifecycle Management:
    - initialize(): Setup plugin resources (async)
    - cleanup(): Cleanup plugin resources (async)
    - entry_point: Module and class for plugin loading
    - priority: Loading order (lower numbers load first)
    
    Examples:
        Basic plugin platform::
        
            plugin = PluginPlatform(
                platform_id="my-plugin",
                platform_name="My Plugin",
                description="Sample plugin implementation",
                entry_point="mypackage.plugins:MyPlugin",
                routes_prefix="/api/my"
            )
            
        Plugin with capabilities::
        
            plugin = PluginPlatform(
                platform_id="mcp-browser-plugin",
                platform_name="MCP Browser Plugin", 
                description="Browse downloaded MCP servers",
                entry_point="haive.mcp.plugins:MCPBrowserPlugin",
                routes_prefix="/mcp",
                provides_servers=True,
                provides_discovery=True,
                provides_health_checks=True,
                priority=10  # High priority, loads early
            )
            
        Plugin with dependencies::
        
            plugin = PluginPlatform(
                platform_id="advanced-plugin",
                platform_name="Advanced Plugin",
                description="Plugin with dependencies",
                entry_point="mypackage:AdvancedPlugin", 
                routes_prefix="/advanced",
                dependencies=["base-plugin", "auth-plugin"],
                priority=200  # Lower priority, loads after dependencies
            )
    """
    
    # Plugin-specific identification and routing
    entry_point: str = Field(
        ...,
        description="Plugin entry point in format 'module:class'",
        examples=["haive.mcp.plugins:MCPBrowserPlugin", "mypackage.plugins:MyPlugin"]
    )
    routes_prefix: str = Field(
        ...,
        description="API routes prefix for plugin endpoints",
        examples=["/mcp", "/api/v1/tools", "/agents"]
    )
    priority: int = Field(
        default=100,
        description="Plugin loading priority (lower numbers = higher priority, load first)",
        ge=0,
        le=1000,
        examples=[10, 50, 100, 200]
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required plugin dependencies (must be loaded first)",
        examples=[["base-plugin"], ["auth-plugin", "database-plugin"]]
    )
    
    # Plugin capabilities - what this plugin provides to the platform
    provides_servers: bool = Field(
        default=False,
        description="Whether plugin manages/provides MCP servers"
    )
    provides_tools: bool = Field(
        default=False,
        description="Whether plugin provides tools for agent execution"
    )
    provides_resources: bool = Field(
        default=False,
        description="Whether plugin provides resources (files, data, etc.)"
    )
    provides_discovery: bool = Field(
        default=False,
        description="Whether plugin participates in service discovery"
    )
    provides_health_checks: bool = Field(
        default=False,
        description="Whether plugin provides health monitoring capabilities"
    )
    
    @field_validator("entry_point")
    @classmethod
    def validate_entry_point_format(cls, v: str) -> str:
        """Validate entry point format.
        
        Entry points must be in the format 'module:class' or 'package.module:class'.
        This follows Python's standard entry point specification.
        
        Args:
            v: Entry point string to validate
            
        Returns:
            Validated entry point string
            
        Raises:
            ValueError: If entry point format is invalid
            
        Examples:
            Valid formats:
            - "mymodule:MyClass"
            - "package.subpackage.module:MyClass"
            - "haive.mcp.plugins:MCPBrowserPlugin"
        """
        if ":" not in v:
            raise ValueError("Entry point must be in format 'module:class'")
        
        module_path, class_name = v.split(":", 1)
        if not module_path or not class_name:
            raise ValueError("Both module path and class name must be specified")
        
        return v
    
    @field_validator("routes_prefix")
    @classmethod
    def normalize_routes_prefix(cls, v: str) -> str:
        """Ensure routes prefix starts with / and is properly formatted.
        
        Args:
            v: Routes prefix to normalize
            
        Returns:
            Normalized routes prefix (always starts with /)
            
        Examples:
            - "mcp" -> "/mcp"
            - "/api/v1" -> "/api/v1" 
            - "tools/" -> "/tools"
        """
        if not v:
            return "/"
        
        # Ensure starts with /
        if not v.startswith('/'):
            v = f"/{v}"
        
        # Remove trailing slash unless it's just "/"
        if v != "/" and v.endswith('/'):
            v = v.rstrip('/')
        
        return v
    
    async def initialize(self) -> None:
        """Initialize plugin resources.
        
        This method is called during plugin loading to set up any resources,
        connections, or state that the plugin needs. Subclasses should override
        this method to perform their specific initialization.
        
        The base implementation:
        - Updates status to ACTIVE
        - Sets updated_at timestamp
        - Adds initialization metadata
        
        Raises:
            Exception: Any initialization errors should be propagated up
            
        Examples:
            Override in subclass::
            
                async def initialize(self) -> None:
                    # Plugin-specific setup
                    await self.setup_database_connections()
                    await self.load_configuration()
                    
                    # Call parent initialization
                    await super().initialize()
                    
                    # Post-initialization tasks
                    self.add_metadata("servers_loaded", len(self.get_servers()))
        """
        self.status = PlatformStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.add_metadata("initialized_at", datetime.utcnow().isoformat())
        self.add_metadata("initialization_successful", True)
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources.
        
        This method is called during plugin unloading or platform shutdown to
        clean up resources, close connections, and save state. Subclasses should
        override this method to perform their specific cleanup.
        
        The base implementation:
        - Updates status to STOPPED
        - Sets updated_at timestamp
        - Adds cleanup metadata
        
        Examples:
            Override in subclass::
            
                async def cleanup(self) -> None:
                    # Plugin-specific cleanup
                    await self.close_database_connections()
                    await self.save_state()
                    
                    # Call parent cleanup
                    await super().cleanup()
        """
        self.status = PlatformStatus.STOPPING
        self.updated_at = datetime.utcnow()
        self.add_metadata("cleanup_at", datetime.utcnow().isoformat())
        self.add_metadata("cleanup_successful", True)
        self.status = PlatformStatus.INACTIVE
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get comprehensive plugin information.
        
        Returns:
            Dictionary containing plugin metadata, capabilities, and status
            
        Examples:
            >>> plugin.get_plugin_info()
            {
                "basic_info": {
                    "platform_id": "mcp-browser-plugin",
                    "platform_name": "MCP Browser Plugin",
                    "version": "1.0.0",
                    "status": "active"
                },
                "plugin_config": {
                    "entry_point": "haive.mcp.plugins:MCPBrowserPlugin",
                    "routes_prefix": "/mcp",
                    "priority": 10
                },
                "capabilities": {
                    "provides_servers": True,
                    "provides_discovery": True,
                    "total_capabilities": 2
                },
                "lifecycle": {
                    "created_at": "2025-08-19T13:45:00Z",
                    "updated_at": "2025-08-19T13:46:30Z"
                }
            }
        """
        return {
            "basic_info": {
                "platform_id": self.platform_id,
                "platform_name": self.platform_name,
                "version": self.version,
                "description": self.description,
                "status": self.status
            },
            "plugin_config": {
                "entry_point": self.entry_point,
                "routes_prefix": self.routes_prefix,
                "priority": self.priority,
                "dependencies": self.dependencies
            },
            "capabilities": {
                "provides_servers": self.provides_servers,
                "provides_tools": self.provides_tools,
                "provides_resources": self.provides_resources,
                "provides_discovery": self.provides_discovery,
                "provides_health_checks": self.provides_health_checks,
                "total_capabilities": sum([
                    self.provides_servers,
                    self.provides_tools,
                    self.provides_resources,
                    self.provides_discovery,
                    self.provides_health_checks
                ])
            },
            "inheritance_info": {
                "base_platform_capabilities": self.get_capability_summary(),
                "platform_metadata": self.metadata
            },
            "lifecycle": {
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None
            }
        }
    
    def check_dependencies_satisfied(self, available_plugins: List[str]) -> tuple[bool, List[str]]:
        """Check if plugin dependencies are satisfied.
        
        Args:
            available_plugins: List of available plugin names
            
        Returns:
            Tuple of (satisfied, missing_dependencies)
            
        Examples:
            >>> plugin.dependencies = ["base-plugin", "auth-plugin"]
            >>> satisfied, missing = plugin.check_dependencies_satisfied(["base-plugin"])
            >>> satisfied
            False
            >>> missing
            ["auth-plugin"]
        """
        missing = [dep for dep in self.dependencies if dep not in available_plugins]
        return len(missing) == 0, missing
    
    def get_load_priority_info(self) -> Dict[str, Any]:
        """Get plugin loading priority information.
        
        Returns:
            Dictionary with priority info and loading recommendations
        """
        priority_level = "high" if self.priority < 50 else "medium" if self.priority < 150 else "low"
        
        return {
            "priority": self.priority,
            "priority_level": priority_level,
            "dependencies": self.dependencies,
            "dependency_count": len(self.dependencies),
            "loading_recommendation": (
                "Load early (core functionality)" if priority_level == "high"
                else "Load mid-phase (standard features)" if priority_level == "medium"
                else "Load late (optional features)"
            )
        }