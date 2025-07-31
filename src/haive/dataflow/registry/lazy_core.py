"""Lazy-loading Registry System for Haive.

This module provides a lazy-loading version of the registry system that
only initializes the Supabase connection when actually needed,
preventing heavy initialization at import time.

The lazy registry system maintains the same interface as the original
but defers expensive operations until they're actually used.
"""

import logging
from typing import Any

from haive.dataflow.db.supabase import get_supabase_client

from .registry.models import EntityType

logger = logging.getLogger(__name__)


class LazyRegistrySystem:
    """Lazy-loading registry system that initializes components on-demand.

    This class provides the same interface as RegistrySystem but defers
    expensive initialization (like Supabase connection) until actually
    needed.
    """

    def __init__(self):
        """Initialize the lazy registry system without heavy operations."""
        self._entities = {}
        self._configurations = {}
        self._dependencies = {}
        self._environment_vars = {}
        self._import_logs = []
        self._supabase = None
        self._initialized = False

        # Skip heavy initialization at import time
        logger.debug("Lazy registry system initialized (no database connection)")

    def _ensure_initialized(self):
        """Ensure the registry system is fully initialized when needed."""
        if self._initialized:
            return

        logger.debug("Initializing registry system on first use")

        # Try to initialize Supabase client only when needed
        try:
            # Import Supabase client

            self._supabase = get_supabase_client()
            logger.info("Supabase connection initialized for registry system")

            # Initialize registry schema if needed for backwards compatibility
            try:
                self._ensure_registry_schema()
            except Exception as schema_e:
                logger.warning(f"Failed to initialize registry schema: {schema_e}")

        except Exception as e:
            logger.warning(f"Failed to initialize Supabase client: {e}")
            # Continue without database support

        self._initialized = True

    def _ensure_registry_schema(self):
        """Ensure the registry schema exists in the database."""
        if not self._supabase:
            return

        # This would contain the schema initialization logic
        # For now, we'll skip it to avoid heavy operations

    def register_entity(
        self,
        name: str,
        type: EntityType,
        description: str = "",
        module_path: str = "",
        class_name: str = "",
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        """Register a new entity (lazy initialization)."""
        # Only initialize when actually registering something
        self._ensure_initialized()

        # Delegate to the actual implementation
        # For now, just store in memory
        entity_id = f"{type.value}_{name}_{hash(module_path)}"
        self._entities[entity_id] = {
            "id": entity_id,
            "name": name,
            "type": type.value,
            "description": description,
            "module_path": module_path,
            "class_name": class_name,
            "metadata": metadata or {},
            **kwargs,
        }

        logger.debug(f"Registered entity: {name} ({type.value})")
        return entity_id

    def get_entities_by_type(self, entity_type: EntityType) -> list[dict[str, Any]]:
        """Get all entities of a specific type (lazy initialization)."""
        self._ensure_initialized()

        # Return entities of the specified type
        return [
            entity
            for entity in self._entities.values()
            if entity["type"] == entity_type.value
        ]

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        """Get a specific entity by ID (lazy initialization)."""
        self._ensure_initialized()

        return self._entities.get(entity_id)

    def search_entities(
        self,
        query: str,
        entity_type: EntityType | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search entities by query (lazy initialization)."""
        self._ensure_initialized()

        # Simple in-memory search
        results = []
        for entity in self._entities.values():
            # Apply type filter if specified
            if entity_type and entity["type"] != entity_type.value:
                continue

            # Apply text search
            if (
                query.lower() in entity["name"].lower()
                or query.lower() in entity.get("description", "").lower()
            ):
                # Apply metadata filter if specified
                if metadata_filter:
                    entity_metadata = entity.get("metadata", {})
                    metadata_matches = True
                    for key, value in metadata_filter.items():
                        if key not in entity_metadata or entity_metadata[key] != value:
                            metadata_matches = False
                            break

                    if metadata_matches:
                        results.append(entity)
                else:
                    results.append(entity)

        return results

    def add_configuration(
        self, registry_id: str, config_type: str, config_data: dict[str, Any]
    ) -> str:
        """Add configuration to an entity (lazy initialization)."""
        self._ensure_initialized()

        # Store configuration
        config_id = f"{registry_id}_{config_type}_{hash(str(config_data))}"
        self._configurations[config_id] = {
            "id": config_id,
            "registry_id": registry_id,
            "config_type": config_type,
            "config_data": config_data,
        }

        return config_id

    def get_configurations(self, registry_id: str) -> list[dict[str, Any]]:
        """Get all configurations for an entity (lazy initialization)."""
        self._ensure_initialized()

        return [
            config
            for config in self._configurations.values()
            if config["registry_id"] == registry_id
        ]


# Create a singleton instance using lazy loading
def get_registry_system() -> LazyRegistrySystem:
    """Get the singleton registry system instance."""
    if not hasattr(get_registry_system, "_instance"):
        get_registry_system._instance = LazyRegistrySystem()
    return get_registry_system._instance


# Create a lazy singleton that doesn't initialize immediately
registry_system = get_registry_system()
