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

import lazy_loader as lazy

# Define submodules to lazy load
submodules = [
    "registry",  # Core registry system
    "mcp",  # MCP integration
    "models",  # Data models
    "api",  # API endpoints
    "auth",  # Authentication
    "db",  # Database layer
    "persistence",  # Persistence layer
    "providers",  # Provider implementations
    "core",  # Core functionality
    "utils",  # Utilities
]

# Define specific attributes from submodules to expose
submod_attrs = {
    "registry": [
        "get_registry_system",
        "discover_agents",
        "discover_all",
        "discover_engines",
        "discover_games",
        "discover_toolkits",
        "discover_tools",
        "EntityType",
        "RegistryItem",
        "serialize_object",
        "deserialize_object",
        # MCP models are defined in registry.models
        "MCPServerConfig",
        "MCPToolDefinition",
        "MCPPromptDefinition",
        "MCPResourceDefinition",
        "MCPTransport",
        "MCPServerHealth",
    ],
    "mcp": [],  # MCP client functionality loaded on demand
    "models": [
        "ConfigType",
        "Configuration",
        "Dependency",
        "DependencyType",
        "EnvironmentVar",
        "GraphDefinition",
        "ImportLogItem",
        "ImportStatus",
    ],
    # Heavy modules are fully lazy loaded
    "api": [],  # API endpoints loaded on demand
    "db": [],  # Database connections loaded on demand
    "auth": [],  # Auth system loaded on demand
    "persistence": [],  # Persistence layer loaded on demand
    "providers": [],  # Provider implementations loaded on demand
    "core": [],  # Core functionality loaded on demand
    "utils": [],  # Utility functions loaded on demand
}

# Attach lazy loading - this creates __getattr__, __dir__, and __all__
__getattr__, __dir__, __all__ = lazy.attach(
    __name__, submodules=submodules, submod_attrs=submod_attrs
)


# Backwards compatibility - lazy registry access
class LazyRegistryAccess:
    def __getattr__(self, name):
        """  Getattr  .

Args:
    name: [TODO: Add description]
"""
        from .registry import get_registry_system

        registry = get_registry_system()
        return getattr(registry, name)


registry_system = LazyRegistryAccess()

# Add eager imports to __all__
__all__ += ["registry_system"]

# Note: Heavy database, API, and persistence modules are lazy loaded for performance
