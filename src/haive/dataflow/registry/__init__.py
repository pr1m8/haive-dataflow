"""Haive Registry System.

This package provides a comprehensive registry system for Haive components,
enabling discovery, registration, and management of various components like
agents, tools, engines, and games.

The registry system acts as a central repository for component metadata,
configurations, and dependency information, making it easier to discover
and use components in the Haive ecosystem.

Key Modules:
    core: Core registry system implementation and API
    models: Data models for registry entries, configurations, and dependencies
    discovery: Component discovery mechanisms
    serialization: Utilities for serializing and deserializing complex objects
    providers: Entity type-specific provider implementations
    importers: Data importers for external component sources

Typical usage example:

    >>> from haive.dataflow.registry import registry_system, EntityType, discover_agents
    >>>
    >>> # Discover and register all agents
    >>> discovered_agents = discover_agents()
    >>> print(f"Discovered {len(discovered_agents)} agents")
    >>>
    >>> # Get all registered tools
    >>> tools = registry_system.get_entities_by_type(EntityType.TOOL)
    >>> for tool in tools:
    >>>     print(f"Tool: {tool.name} - {tool.description}")
"""

from haive.dataflow.registry.core import registry_system

# Import discovery functions
from haive.dataflow.registry.discovery import (
    discover_agents,
    discover_all,
    discover_engines,
    discover_games,
    discover_toolkits,
    discover_tools,
)
from haive.dataflow.registry.models import (
    ConfigType,
    Configuration,
    Dependency,
    DependencyType,
    EntityType,
    EnvironmentVar,
    GraphDefinition,
    ImportLogItem,
    ImportStatus,
    RegistryItem,
)

# Import serialization utilities
from haive.dataflow.registry.serialization import (
    SerializationRegistry,
    deserialize_object,
    serialize_object,
)

# Export for convenient imports
__all__ = [
    # Core registry system
    "registry_system",
    # Models
    "EntityType",
    "ConfigType",
    "DependencyType",
    "ImportStatus",
    "RegistryItem",
    "Configuration",
    "GraphDefinition",
    "Dependency",
    "EnvironmentVar",
    "ImportLogItem",
    # Discovery
    "discover_all",
    "discover_agents",
    "discover_tools",
    "discover_toolkits",
    "discover_engines",
    "discover_games",
    # Serialization
    "serialize_object",
    "deserialize_object",
    "SerializationRegistry",
]
