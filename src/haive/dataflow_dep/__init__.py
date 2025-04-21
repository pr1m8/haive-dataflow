"""Haive Registry System

This package provides a comprehensive registry system for Haive components,
enabling discovery, registration, and management of various components like
agents, tools, engines, and more.
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
    "SerializationRegistry"
]
