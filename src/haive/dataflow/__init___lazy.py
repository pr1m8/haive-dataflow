"""Haive Dataflow - Registry and Discovery System (Lazy Loading).

This is a lazy-loading version of the haive-dataflow package that prevents
heavy initialization at import time. The registry system and database
connections are only initialized when actually needed.

The haive-dataflow package provides a comprehensive system for component
discovery, registration, and management in the Haive ecosystem.

It enables automatic discovery of components like agents, tools, engines, and games,
handling their registration, dependency management, configuration, and persistence.

Typical usage example:

            from haive.dataflow import registry_system, EntityType, discover_agents

            # Discover and register agents (lazy initialization happens here)
            discovered_agents = discover_agents()
            print(f"Discovered {len(discovered_agents)} agents")

            # Register a custom component
            registry_system.register_entity(
                name="CustomAgent",
                type=EntityType.AGENT,
                description="A custom agent implementation",
                module_path="my_module.agents",
                class_name="CustomAgent"
            )

            # Query components
            agents = registry_system.get_entities_by_type(EntityType.AGENT)

This package consists of several modules:

    registry: Core registry functionality for component management
    discovery: Component discovery mechanisms
    serialization: Tools for serializing/deserializing complex objects
    db: Database integration for persistence
    api: API endpoints for accessing registry data
    providers: Provider implementations for various services
"""

# Import discovery functions (these should also be lazy)

from haive.dataflow.registry.discovery import (
    discover_agents,
    discover_all,
    discover_engines,
    discover_games,
    discover_toolkits,
    discover_tools,
)
from haive.dataflow.registry.lazy_core import registry_system
from haive.dataflow.registry.models import (  # MCP Models
    ConfigType,
    Configuration,
    Dependency,
    DependencyType,
    EntityType,
    EnvironmentVar,
    GraphDefinition,
    ImportLogItem,
    ImportStatus,
    MCPPromptDefinition,
    MCPResourceDefinition,
    MCPServerConfig,
    MCPServerHealth,
    MCPToolDefinition,
    MCPTransport,
    RegistryItem,
)
from haive.dataflow.registry.serialization import (
    SerializationRegistry,
    deserialize_object,
    serialize_object,
)

# Use lazy loading for the registry system

# Import serialization utilities


# Export for convenient imports
__all__ = [
    "ConfigType",
    "Configuration",
    "Dependency",
    "DependencyType",
    # Models
    "EntityType",
    "EnvironmentVar",
    "GraphDefinition",
    "ImportLogItem",
    "ImportStatus",
    "MCPPromptDefinition",
    "MCPResourceDefinition",
    "MCPServerConfig",
    "MCPServerHealth",
    "MCPToolDefinition",
    # MCP Models
    "MCPTransport",
    "RegistryItem",
    "SerializationRegistry",
    "deserialize_object",
    "discover_agents",
    # Discovery
    "discover_all",
    "discover_engines",
    "discover_games",
    "discover_toolkits",
    "discover_tools",
    # Core registry system
    "registry_system",
    # Serialization
    "serialize_object",
]
