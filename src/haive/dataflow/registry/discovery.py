"""Discovery mechanisms for the Haive Registry System.

This module provides functionality for automatically discovering and registering
various components in the Haive ecosystem, such as agents, tools, engines, and games.
It implements introspection mechanisms to find components based on naming conventions,
class inheritance, and module structure.

The discovery process works by:
1. Searching for modules in specified paths
2. Inspecting classes in those modules
3. Determining if they match criteria for specific component types
4. Registering matching components in the registry system

Functions:
    discover_modules: Find all Python modules under a base path
    discover_all: Discover all component types (agents, tools, engines, games)
    discover_agents: Discover and register agent components
    discover_tools: Discover and register tool components
    discover_toolkits: Discover and register toolkit components
    discover_engines: Discover and register engine components
    discover_games: Discover and register game components

Example:
    Discovering components:

    >>> from haive.dataflow.registry.discovery import discover_agents, discover_tools
    >>>
    >>> # Discover all agents in the system
    >>> discovered_agents = discover_agents()
    >>> print(f"Discovered {len(discovered_agents)} agents")
    >>>
    >>> # Discover tools and toolkits
    >>> discovered_tools = discover_tools()
    >>> discovered_toolkits = discover_toolkits()
    >>> print(f"Discovered {len(discovered_tools)} tools and {len(discovered_toolkits)} toolkits")
"""

import asyncio
import importlib
import inspect
import logging
import os
import pkgutil
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from haive.dataflow.mcp.discovery import discover_mcp_servers as mcp_discover

from .registry.core import registry_system  # Import the singleton instance
from .registry.models import ConfigType, EntityType, ImportStatus

# Import registry models and utilities


# Set up logging
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
log_dir = Path.cwd() / "logs" / "registry" / "discovery"
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(log_dir / "discovery.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def discover_modules(base_path: str) -> list[str]:
    """Discover all Python modules under a base path.

    This function recursively explores a package to find all Python modules.
    It handles both regular modules and packages, traversing the entire module
    hierarchy to discover all available modules.

    Args:
        base_path: Base module path to start discovery from (e.g., "haive.agents")

    Returns:
        List[str]: List of fully qualified module paths discovered

    Example:
        >>> modules = discover_modules("haive.tools")
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
        for _loader, module_name, is_pkg in pkgutil.walk_packages([base_dir]):
            full_module_name = f"{base_path}.{module_name}"
            discovered_modules.append(full_module_name)

            # If it's a package, recursively discover submodules
            if is_pkg:
                sub_modules = discover_modules(full_module_name)
                discovered_modules.extend(sub_modules)

        return discovered_modules

    except ImportError as e:
        logger.exception(f"Error importing base module {base_path}: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error discovering modules in {base_path}: {e}")
        return []


def is_pydantic_model(obj: Any) -> bool:
    """Check if an object is a Pydantic model.

    Args:
        obj: Object to check

    Returns:
        True if it's a Pydantic model, False otherwise
    """
    try:
        return inspect.isclass(obj) and issubclass(obj, BaseModel)
    except (ImportError, TypeError):
        return False


def discover_agents(module_paths: list[str] | None = None) -> list[str]:
    """Discover and register agents.

    Args:
        module_paths: Optional list of module paths to search

    Returns:
        List of registered agent IDs
    """
    # Use default module paths if none provided
    if module_paths is None:
        module_paths = ["src.haive.agents"]

    registered_ids = []
    import_session = str(uuid.uuid4())
    logger.info(f"Starting agent discovery with session {import_session}")

    for base_path in module_paths:
        logger.info(f"Discovering agents in {base_path}")

        # Discover all modules
        modules = discover_modules(base_path)
        for module_name in modules:
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Look for classes that might be agent configs
                for name, obj in inspect.getmembers(module):
                    # Skip if it's not a class
                    if not inspect.isclass(obj):
                        continue

                    # Check if it's an agent config
                    is_agent_config = False

                    # Check class name and inheritance
                    if name.endswith(("Config", "AgentConfig")):
                        # Check inheritance - look for AgentConfig in mro
                        for base in obj.__mro__:
                            if base.__name__ in ["AgentConfig"]:
                                is_agent_config = True
                                break

                    # Check for specific attributes that suggest it's an agent config
                    if hasattr(obj, "build_agent") or hasattr(obj, "agent_class"):
                        is_agent_config = True

                    # Register if it's an agent config
                    if is_agent_config:
                        logger.info(f"Found agent config: {name} in {module_name}")

                        # Try to instantiate the config
                        try:
                            instance = None
                            if hasattr(obj, "default") and callable(obj.default):
                                instance = obj.default()
                            else:
                                # Try to instantiate with no args
                                instance = obj()

                            # Get a better name
                            agent_name = (
                                instance.name if hasattr(instance, "name") else name
                            )

                            # Register the agent
                            agent_id = registry_system.register_entity(
                                name=agent_name,
                                entity_type=EntityType.AGENT,
                                description=(
                                    instance.__doc__
                                    if instance.__doc__
                                    else f"{agent_name} agent configuration"
                                ),
                                module_path=module_name,
                                class_name=name,
                                metadata={
                                    "discovered_at": datetime.now().isoformat(),
                                    "type_hint": "agent_config",
                                },
                            )

                            # Register configurations if available
                            try:
                                # State schema
                                if hasattr(instance, "state_schema"):
                                    registry_system.add_configuration(
                                        registry_id=agent_id,
                                        config_type=ConfigType.STATE_SCHEMA,
                                        config_data=instance.state_schema,
                                    )

                                # Input schema
                                if hasattr(instance, "input_schema"):
                                    registry_system.add_configuration(
                                        registry_id=agent_id,
                                        config_type=ConfigType.INPUT_SCHEMA,
                                        config_data=instance.input_schema,
                                    )

                                # Output schema
                                if hasattr(instance, "output_schema"):
                                    registry_system.add_configuration(
                                        registry_id=agent_id,
                                        config_type=ConfigType.OUTPUT_SCHEMA,
                                        config_data=instance.output_schema,
                                    )

                                # Engine
                                if hasattr(instance, "engine"):
                                    registry_system.add_configuration(
                                        registry_id=agent_id,
                                        config_type=ConfigType.ENGINE,
                                        config_data=instance.engine,
                                    )
                            except Exception as e:
                                logger.exception(
                                    f"Error registering configurations for {agent_name}: {e}"
                                )

                            # Log success
                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=agent_name,
                                entity_type="agent",
                                status=ImportStatus.SUCCESS,
                                message=f"Successfully registered agent {agent_name} from {module_name}",
                            )

                            registered_ids.append(agent_id)

                        except Exception as e:
                            # Log error
                            error_tb = traceback.format_exc()
                            logger.exception(
                                f"Error registering agent {name} from {module_name}: {e}\n{error_tb}"
                            )

                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=name,
                                entity_type="agent",
                                status=ImportStatus.FAILURE,
                                message=f"Failed to register agent {name} from {module_name}: {e}",
                                traceback_str=error_tb,
                            )

            except Exception as e:
                error_tb = traceback.format_exc()
                logger.exception(
                    f"Error processing module {module_name}: {e}\n{error_tb}"
                )

    logger.info(f"Discovered {len(registered_ids)} agents")
    return registered_ids


def discover_tools(module_paths: list[str] | None = None) -> list[str]:
    """Discover and register tools.

    Args:
        module_paths: Optional list of module paths to search

    Returns:
        List of registered tool IDs
    """
    # Use default module paths if none provided
    if module_paths is None:
        module_paths = ["src.haive.tak.tools"]

    registered_ids = []
    import_session = str(uuid.uuid4())
    logger.info(f"Starting tool discovery with session {import_session}")

    for base_path in module_paths:
        logger.info(f"Discovering tools in {base_path}")

        # Discover all modules
        modules = discover_modules(base_path)
        for module_name in modules:
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Look for classes that might be tools
                for name, obj in inspect.getmembers(module):
                    # Skip if it's not a class or callable
                    if not (inspect.isclass(obj) or inspect.isfunction(obj)):
                        continue

                    # Check if it's a tool
                    is_tool = False

                    # For classes, check inheritance
                    if inspect.isclass(obj):
                        # Look for BaseTool in mro
                        for base in obj.__mro__:
                            if base.__name__ in ["BaseTool", "StructuredTool", "Tool"]:
                                is_tool = True
                                break

                    # For functions, check if decorated with @tool
                    elif (
                        inspect.isfunction(obj)
                        and hasattr(obj, "_type")
                        and obj._type == "tool"
                    ):
                        is_tool = True

                    # Register if it's a tool
                    if is_tool:
                        logger.info(f"Found tool: {name} in {module_name}")

                        # Try to instantiate or get tool info
                        try:
                            # For classes, try to instantiate
                            if inspect.isclass(obj):
                                instance = None
                                try:
                                    # Try to instantiate with no args
                                    instance = obj()
                                except Exception:
                                    # If that fails, skip - we'll register the class at
                                    # least
                                    pass

                                # Get tool info
                                tool_name = (
                                    getattr(instance, "name", name)
                                    if instance
                                    else name
                                )
                                tool_description = (
                                    getattr(instance, "description", None)
                                    or obj.__doc__
                                    or f"{tool_name} tool"
                                )

                                # Check for API key requirements
                                required_env_vars = []
                                if instance:
                                    # Look for attributes that might suggest API key
                                    # requirements
                                    for attr_name in [
                                        "api_key",
                                        "api_token",
                                        "token",
                                        "key",
                                    ]:
                                        if hasattr(instance, attr_name):
                                            env_var = f"{
                                                tool_name.upper()}_{
                                                attr_name.upper()}"
                                            required_env_vars.append(env_var)

                            # For functions, extract info
                            else:
                                tool_name = getattr(obj, "name", name)
                                tool_description = (
                                    getattr(obj, "description", None)
                                    or obj.__doc__
                                    or f"{tool_name} tool"
                                )
                                required_env_vars = []

                            # Register the tool
                            tool_id = registry_system.register_entity(
                                name=tool_name,
                                entity_type=EntityType.TOOL,
                                description=tool_description,
                                module_path=module_name,
                                class_name=name,
                                metadata={
                                    "discovered_at": datetime.now().isoformat(),
                                    "type": (
                                        "class" if inspect.isclass(obj) else "function"
                                    ),
                                },
                            )

                            # Register required env vars if any
                            for env_var in required_env_vars:
                                registry_system.add_environment_var(
                                    registry_id=tool_id,
                                    env_name=env_var,
                                    is_required=True,
                                )

                            # Log success
                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=tool_name,
                                entity_type="tool",
                                status=ImportStatus.SUCCESS,
                                message=f"Successfully registered tool {tool_name} from {module_name}",
                            )

                            registered_ids.append(tool_id)

                        except Exception as e:
                            # Log error
                            error_tb = traceback.format_exc()
                            logger.exception(
                                f"Error registering tool {name} from {module_name}: {e}\n{error_tb}"
                            )

                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=name,
                                entity_type="tool",
                                status=ImportStatus.FAILURE,
                                message=f"Failed to register tool {name} from {module_name}: {e}",
                                traceback_str=error_tb,
                            )

            except Exception as e:
                error_tb = traceback.format_exc()
                logger.exception(
                    f"Error processing module {module_name}: {e}\n{error_tb}"
                )

    logger.info(f"Discovered {len(registered_ids)} tools")
    return registered_ids


def discover_toolkits(module_paths: list[str] | None = None) -> list[str]:
    """Discover and register toolkits.

    Args:
        module_paths: Optional list of module paths to search

    Returns:
        List of registered toolkit IDs
    """
    # Use default module paths if none provided
    if module_paths is None:
        module_paths = ["src.haive.tak.toolkits"]

    registered_ids = []
    import_session = str(uuid.uuid4())
    logger.info(f"Starting toolkit discovery with session {import_session}")

    for base_path in module_paths:
        logger.info(f"Discovering toolkits in {base_path}")

        # Discover all modules
        modules = discover_modules(base_path)
        for module_name in modules:
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Look for classes that might be toolkits
                for name, obj in inspect.getmembers(module):
                    # Skip if it's not a class
                    if not inspect.isclass(obj):
                        continue

                    # Check if it's a toolkit
                    is_toolkit = False

                    # Look for specific base classes or attributes
                    if (
                        name.endswith("Toolkit")
                        or hasattr(obj, "tools")
                        or hasattr(obj, "get_tools")
                    ):
                        is_toolkit = True

                    # Register if it's a toolkit
                    if is_toolkit:
                        logger.info(f"Found toolkit: {name} in {module_name}")

                        # Try to instantiate and register
                        try:
                            # Try to instantiate
                            instance = None
                            try:
                                # Try to instantiate with no args
                                instance = obj()
                            except Exception:
                                # If that fails, skip - we'll register the class at
                                # least
                                pass

                            # Get toolkit info
                            toolkit_name = (
                                getattr(instance, "name", name) if instance else name
                            )
                            toolkit_description = (
                                getattr(instance, "description", None)
                                or obj.__doc__
                                or f"{toolkit_name} toolkit"
                            )

                            # Get tools if available
                            toolkit_tools = []
                            if instance:
                                if hasattr(instance, "tools") and isinstance(
                                    instance.tools, list
                                ):
                                    toolkit_tools = [
                                        getattr(tool, "name", str(tool))
                                        for tool in instance.tools
                                    ]
                                elif hasattr(instance, "get_tools") and callable(
                                    instance.get_tools
                                ):
                                    try:
                                        tools = instance.get_tools()
                                        toolkit_tools = [
                                            getattr(tool, "name", str(tool))
                                            for tool in tools
                                        ]
                                    except Exception:
                                        pass

                            # Register the toolkit
                            toolkit_id = registry_system.register_entity(
                                name=toolkit_name,
                                entity_type=EntityType.TOOLKIT,
                                description=toolkit_description,
                                module_path=module_name,
                                class_name=name,
                                metadata={
                                    "discovered_at": datetime.now().isoformat(),
                                    "tools": toolkit_tools,
                                },
                            )

                            # Look for required environment variables
                            if instance:
                                # Common patterns for storing API keys
                                for attr_name in [
                                    "api_key",
                                    "api_token",
                                    "token",
                                    "key",
                                ]:
                                    if hasattr(instance, attr_name):
                                        env_var = f"{
                                            toolkit_name.upper()}_{
                                            attr_name.upper()}"
                                        registry_system.add_environment_var(
                                            registry_id=toolkit_id,
                                            env_name=env_var,
                                            is_required=True,
                                        )

                            # Log success
                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=toolkit_name,
                                entity_type="toolkit",
                                status=ImportStatus.SUCCESS,
                                message=f"Successfully registered toolkit {toolkit_name} from {module_name}",
                            )

                            registered_ids.append(toolkit_id)

                        except Exception as e:
                            # Log error
                            error_tb = traceback.format_exc()
                            logger.exception(
                                f"Error registering toolkit {name} from {module_name}: {e}\n{error_tb}"
                            )

                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=name,
                                entity_type="toolkit",
                                status=ImportStatus.FAILURE,
                                message=f"Failed to register toolkit {name} from {module_name}: {e}",
                                traceback_str=error_tb,
                            )

            except Exception as e:
                error_tb = traceback.format_exc()
                logger.exception(
                    f"Error processing module {module_name}: {e}\n{error_tb}"
                )

    logger.info(f"Discovered {len(registered_ids)} toolkits")
    return registered_ids


def discover_engines(module_paths: list[str] | None = None) -> list[str]:
    """Discover and register engines.

    Args:
        module_paths: Optional list of module paths to search

    Returns:
        List of registered engine IDs
    """
    # Use default module paths if none provided
    if module_paths is None:
        module_paths = ["src.haive.core.engine"]

    registered_ids = []
    import_session = str(uuid.uuid4())
    logger.info(f"Starting engine discovery with session {import_session}")

    for base_path in module_paths:
        logger.info(f"Discovering engines in {base_path}")

        # Discover all modules
        modules = discover_modules(base_path)
        for module_name in modules:
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Look for classes that might be engines
                for name, obj in inspect.getmembers(module):
                    # Skip if it's not a class
                    if not inspect.isclass(obj):
                        continue

                    # Check if it's an engine
                    is_engine = False

                    # Check class name and inheritance
                    if name.endswith("Config") and (
                        name.endswith(("LLMConfig", "EngineConfig", "AugLLMConfig"))
                    ):
                        # Check inheritance - look for Engine or Config in mro
                        for base in obj.__mro__:
                            if base.__name__ in [
                                "LLMConfig",
                                "AugLLMConfig",
                                "EngineConfig",
                                "Engine",
                            ]:
                                is_engine = True
                                break

                    # Check for specific engine attributes
                    if hasattr(obj, "create_runnable") or hasattr(obj, "instantiate"):
                        is_engine = True

                    # Register if it's an engine
                    if is_engine:
                        logger.info(f"Found engine: {name} in {module_name}")

                        # Try to instantiate or get engine info
                        try:
                            # Try to instantiate
                            instance = None
                            try:
                                # Try to instantiate with no args
                                instance = obj()
                            except Exception:
                                # If that fails, skip - we'll register the class at
                                # least
                                pass

                            # Get engine info
                            engine_name = (
                                getattr(instance, "name", name)
                                if instance
                                else name.replace("Config", "")
                            )
                            engine_description = (
                                getattr(instance, "description", None)
                                or obj.__doc__
                                or f"{engine_name} engine configuration"
                            )

                            # Get provider info if available
                            provider = None
                            if hasattr(obj, "provider") or (
                                instance and hasattr(instance, "provider")
                            ):
                                provider = getattr(
                                    instance, "provider", None
                                ) or getattr(obj, "provider", None)
                                provider = str(provider) if provider else None

                            # Get model info if available
                            model = None
                            if hasattr(obj, "model") or (
                                instance and hasattr(instance, "model")
                            ):
                                model = getattr(instance, "model", None) or getattr(
                                    obj, "model", None
                                )

                            # Register the engine
                            engine_id = registry_system.register_entity(
                                name=engine_name,
                                entity_type=EntityType.ENGINE,
                                description=engine_description,
                                module_path=module_name,
                                class_name=name,
                                metadata={
                                    "discovered_at": datetime.now().isoformat(),
                                    "type_hint": "engine_config",
                                    "provider": provider,
                                    "model": model,
                                },
                            )

                            # Check for required environment variables
                            if instance:
                                # Look for API key pattern
                                if hasattr(instance, "api_key"):
                                    # Check if it's a reference to an environment
                                    # variable
                                    api_key = instance.api_key
                                    if not api_key or (
                                        isinstance(api_key, str) and "${" in api_key
                                    ):
                                        # Extract env var name if it's a reference
                                        env_var = api_key.strip("${}")
                                        if env_var:
                                            registry_system.add_environment_var(
                                                registry_id=engine_id,
                                                env_name=env_var,
                                                is_required=True,
                                            )
                                    elif provider:
                                        # Add standard pattern based on provider
                                        env_var = f"{provider.upper()}_API_KEY"
                                        registry_system.add_environment_var(
                                            registry_id=engine_id,
                                            env_name=env_var,
                                            is_required=True,
                                        )

                            # Log success
                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=engine_name,
                                entity_type="engine",
                                status=ImportStatus.SUCCESS,
                                message=f"Successfully registered engine {engine_name} from {module_name}",
                            )

                            registered_ids.append(engine_id)

                        except Exception as e:
                            # Log error
                            error_tb = traceback.format_exc()
                            logger.exception(
                                f"Error registering engine {name} from {module_name}: {e}\n{error_tb}"
                            )

                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=name,
                                entity_type="engine",
                                status=ImportStatus.FAILURE,
                                message=f"Failed to register engine {name} from {module_name}: {e}",
                                traceback_str=error_tb,
                            )

            except Exception as e:
                error_tb = traceback.format_exc()
                logger.exception(
                    f"Error processing module {module_name}: {e}\n{error_tb}"
                )

    logger.info(f"Discovered {len(registered_ids)} engines")
    return registered_ids


def discover_games(module_paths: list[str] | None = None) -> list[str]:
    """Discover and register games.

    Args:
        module_paths: Optional list of module paths to search

    Returns:
        List of registered game IDs
    """
    # Use default module paths if none provided
    if module_paths is None:
        module_paths = ["src.haive.games"]

    registered_ids = []
    import_session = str(uuid.uuid4())
    logger.info(f"Starting game discovery with session {import_session}")

    for base_path in module_paths:
        logger.info(f"Discovering games in {base_path}")

        # Discover all modules
        modules = discover_modules(base_path)
        for module_name in modules:
            try:
                # Import the module
                module = importlib.import_module(module_name)

                # Look for classes that might be games
                for name, obj in inspect.getmembers(module):
                    # Skip if it's not a class
                    if not inspect.isclass(obj):
                        continue

                    # Check if it's a game
                    is_game = False

                    # Check class name and specific attributes
                    if (
                        name.endswith("Game")
                        or hasattr(obj, "play")
                        or hasattr(obj, "start_game")
                    ):
                        is_game = True

                    # Register if it's a game
                    if is_game:
                        logger.info(f"Found game: {name} in {module_name}")

                        # Try to instantiate or get game info
                        try:
                            # Get game info
                            game_name = name.replace("Game", "")
                            game_description = obj.__doc__ or f"{game_name} game"

                            # Register the game
                            game_id = registry_system.register_entity(
                                name=game_name,
                                entity_type=EntityType.GAME,
                                description=game_description,
                                module_path=module_name,
                                class_name=name,
                                metadata={"discovered_at": datetime.now().isoformat()},
                            )

                            # Log success
                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=game_name,
                                entity_type="game",
                                status=ImportStatus.SUCCESS,
                                message=f"Successfully registered game {game_name} from {module_name}",
                            )

                            registered_ids.append(game_id)

                        except Exception as e:
                            # Log error
                            error_tb = traceback.format_exc()
                            logger.exception(
                                f"Error registering game {name} from {module_name}: {e}\n{error_tb}"
                            )

                            registry_system.add_import_log(
                                import_session=import_session,
                                entity_name=name,
                                entity_type="game",
                                status=ImportStatus.FAILURE,
                                message=f"Failed to register game {name} from {module_name}: {e}",
                                traceback_str=error_tb,
                            )

            except Exception as e:
                error_tb = traceback.format_exc()
                logger.exception(
                    f"Error processing module {module_name}: {e}\n{error_tb}"
                )

    logger.info(f"Discovered {len(registered_ids)} games")
    return registered_ids


def discover_all() -> dict[EntityType, list[str]]:
    """Discover and register all entity types.

    Returns:
        Dictionary mapping entity types to lists of registered IDs
    """
    results = {}

    # Discover agents
    results[EntityType.AGENT] = discover_agents()

    # Discover tools
    results[EntityType.TOOL] = discover_tools()

    # Discover toolkits
    results[EntityType.TOOLKIT] = discover_toolkits()

    # Discover engines
    results[EntityType.ENGINE] = discover_engines()

    # Discover games
    results[EntityType.GAME] = discover_games()

    # Discover MCP servers
    results[EntityType.MCP_SERVER] = discover_mcp_servers()

    return results


def discover_mcp_servers() -> list[str]:
    """Discover and register MCP (Model Context Protocol) servers.

    This function discovers MCP servers from various sources including:
    - npm packages (@modelcontextprotocol/*)
    - PyPI packages (mcp-*)
    - Local configurations
    - Existing haive-mcp downloaded servers

    Returns:
        List of registry IDs for registered MCP servers

    Example:
        >>> mcp_servers = discover_mcp_servers()
        >>> print(f"Discovered {len(mcp_servers)} MCP servers")
    """
    logger.info("Starting MCP server discovery")

    try:
        # Import MCP discovery (lazy import to avoid circular dependencies)
        # Discover MCP servers and register them

        async def async_discover():
            registry_items = await mcp_discover(registry_system)
            registered_ids = []

            for item in registry_items:
                try:
                    # Register the item
                    entity_id = registry_system.register_entity(
                        name=item.name,
                        type=item.type,
                        description=item.description,
                        module_path=item.module_path,
                        class_name=item.class_name,
                        config=item.config,
                        tags=item.tags,
                    )
                    registered_ids.append(entity_id)
                    logger.info(f"Registered MCP server: {item.name} -> {entity_id}")

                except Exception as e:
                    logger.exception(f"Failed to register MCP server {item.name}: {e}")

            return registered_ids

        # Run async discovery
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(async_discover())
                # For now, return empty list and let it run in background
                logger.info("MCP discovery running in background")
                return []
            # If no loop running, run directly
            return asyncio.run(async_discover())
        except RuntimeError:
            # No event loop, run directly
            return asyncio.run(async_discover())

    except ImportError as e:
        logger.warning(f"MCP discovery not available: {e}")
        return []
    except Exception as e:
        logger.exception(f"Failed to discover MCP servers: {e}")
        return []
