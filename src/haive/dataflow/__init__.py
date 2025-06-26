"""Haive Dataflow - Registry and Discovery System.

The haive-dataflow package provides a comprehensive system for component
discovery, registration, and management in the Haive ecosystem.

It enables automatic discovery of components like agents, tools, engines, and games,
handling their registration, dependency management, configuration, and persistence.

Typical usage example:

    ```python
    from haive.dataflow import registry_system, EntityType, discover_agents

    # Discover and register agents
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
    ```

This package consists of several modules:

    registry: Core registry functionality for component management
    discovery: Component discovery mechanisms
    serialization: Tools for serializing/deserializing complex objects
    db: Database integration for persistence
    api: API endpoints for accessing registry data
    providers: Provider implementations for various services
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
