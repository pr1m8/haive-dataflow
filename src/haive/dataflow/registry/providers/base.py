"""Base provider class for the Haive Registry System.

This module defines the base provider class that all specific entity providers
inherit from. Entity providers are responsible for discovering, registering,
and managing specific types of entities in the registry system.

Each entity type (agent, tool, engine, etc.) has its own provider that implements
the discovery and registration logic specific to that entity type. The base
provider class defines the common interface and functionality shared by all
providers.

Classes:
    EntityProvider: Abstract base class for all entity providers

Example:
    Implementing a custom entity provider:

    >>> from haive.dataflow.registry.providers.base import EntityProvider
    >>> from haive.dataflow.registry.models import EntityType
    >>>
    >>> class CustomProvider(EntityProvider):
    ...     def __init__(self):
    ...         super().__init__(EntityType.CUSTOM)
    ...
    ...     def discover(self, module_paths=None):
    ...         # Custom discovery logic
    ...         paths = module_paths or self.get_default_search_paths()
    ...         # ... discovery implementation ...
    ...         return registered_ids
    ...
    ...     def get_default_search_paths(self):
    ...         return ["my_package.custom_components"]
"""

import importlib
import inspect
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Any

from haive.dataflow.core import registry_system

# Import models
from haive.dataflow.models import ConfigType, DependencyType, EntityType, ImportStatus

# Set up logging
from haive.dataflow.utils.logging import setup_discovery_logger

logger = setup_discovery_logger("providers")


class EntityProvider(ABC):
    """Abstract base class for entity providers.

    Entity providers are responsible for discovering, registering, and managing
    specific types of entities in the registry system. This base class defines
    the common interface and shared functionality that all entity providers
    must implement.

    Entity providers handle:
    - Discovering components of a specific type in the codebase
    - Registering discovered components in the registry system
    - Managing component metadata, configurations, and dependencies

    Attributes:
        entity_type (EntityType): The type of entity this provider handles
    """

    def __init__(self, entity_type: EntityType):
        """Initialize the entity provider.

        Args:
            entity_type: Type of entity this provider handles (e.g., AGENT, TOOL)
        """
        self.entity_type = entity_type

    @abstractmethod
    def discover(self, module_paths: list[str] | None = None) -> list[str]:
        """Discover and register entities.

        This abstract method must be implemented by concrete provider classes.
        It should search for components of the provider's entity type in the
        specified module paths, and register them in the registry system.

        Args:
            module_paths: Optional list of module paths to search. If None,
                the provider's default search paths will be used.

        Returns:
            List[str]: List of registered entity IDs for the discovered components

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """

    @abstractmethod
    def get_default_search_paths(self) -> list[str]:
        """Get default search paths for entity discovery.

        This abstract method must be implemented by concrete provider classes.
        It should return a list of module paths where components of the provider's
        entity type are likely to be found.

        Returns:
            List[str]: List of package paths to search for components

        Raises:
            NotImplementedError: Must be implemented by subclasses

        Example:
            >>> def get_default_search_paths(self):
            ...     return [
            ...         "haive.agents",
            ...         "haive.core.agents",
            ...         "my_package.custom_agents"
            ...     ]
        """

    def discover_modules(self, base_path: str) -> list[str]:
        """Discover all Python modules under a base path.

        This helper method recursively explores a package to find all Python modules.
        It handles both regular modules and packages, traversing the entire module
        hierarchy to discover all available modules.

        Args:
            base_path: Base module path to start discovery from (e.g., "haive.agents")

        Returns:
            List[str]: List of fully qualified module paths discovered

        Example:
            >>> provider = SomeEntityProvider()
            >>> modules = provider.discover_modules("haive.tools")
            >>> print(f"Discovered modules: {modules}")
            Discovered modules: ['haive.tools.text', 'haive.tools.image', ...]
        """
        discovered_modules = []
        try:
            # Import the base module
            base_module = importlib.import_module(base_path)

            # Get the base module's file path
            if hasattr(base_module, "__path__"):
                base_dir = base_module.__path__[0]
            elif hasattr(base_module, "__file__"):
                base_dir = os.path.dirname(base_module.__file__)
            else:
                logger.warning(f"Could not determine path for {base_path}")
                return []

            # Walk through the package
            for loader, module_name, is_pkg in pkgutil.walk_packages([base_dir]):
                full_module_name = f"{base_path}.{module_name}"
                discovered_modules.append(full_module_name)

                # If it's a package, recursively discover submodules
                if is_pkg:
                    sub_modules = self.discover_modules(full_module_name)
                    discovered_modules.extend(sub_modules)

            return discovered_modules

        except ImportError as e:
            logger.error(f"Error importing base module {base_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error discovering modules in {base_path}: {e}")
            return []

    def is_pydantic_model(self, obj: Any) -> bool:
        """Check if an object is a Pydantic model.

        Args:
            obj: Object to check

        Returns:
            True if it's a Pydantic model, False otherwise
        """
        try:
            from pydantic import BaseModel

            return inspect.isclass(obj) and issubclass(obj, BaseModel)
        except (ImportError, TypeError):
            return False

    def add_environment_vars(self, registry_id: str, env_vars: dict[str, bool]) -> None:
        """Add environment variables to a registry entity.

        Args:
            registry_id: Registry entity ID
            env_vars: Dictionary mapping environment variable names to required flag
        """
        for env_name, is_required in env_vars.items():
            registry_system.add_environment_var(
                registry_id=registry_id, env_name=env_name, is_required=is_required
            )

    def add_dependency(
        self, registry_id: str, dependent_id: str, dependency_type: DependencyType
    ) -> None:
        """Add a dependency between registry entities.

        Args:
            registry_id: ID of the entity that depends on another
            dependent_id: ID of the entity being depended on
            dependency_type: Type of dependency
        """
        registry_system.add_dependency(
            registry_id=registry_id,
            dependent_id=dependent_id,
            dependency_type=dependency_type,
        )

    def add_configuration(
        self, registry_id: str, config_type: ConfigType, config_data: Any
    ) -> None:
        """Add a configuration to a registry entity.

        Args:
            registry_id: Registry entity ID
            config_type: Type of configuration
            config_data: Configuration data
        """
        registry_system.add_configuration(
            registry_id=registry_id, config_type=config_type, config_data=config_data
        )

    def add_import_log(
        self,
        import_session: str,
        entity_name: str,
        status: ImportStatus,
        message: str | None = None,
        traceback_str: str | None = None,
    ) -> None:
        """Add an import log entry.

        Args:
            import_session: Import session identifier
            entity_name: Name of the entity being imported
            status: Import status
            message: Optional message
            traceback_str: Optional traceback string
        """
        registry_system.add_import_log(
            import_session=import_session,
            entity_name=entity_name,
            entity_type=self.entity_type,
            status=status,
            message=message,
            traceback_str=traceback_str,
        )
