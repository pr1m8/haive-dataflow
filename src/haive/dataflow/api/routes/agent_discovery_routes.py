"""Agent discovery and management API routes.

This module provides FastAPI routes for discovering and managing both v1 and v2 agents:
- v1 agents: haive.engine.agent.config/agent (config-based agents)
- v2 agents: haive.agents.base.agent (direct agent classes)
"""

import importlib
import inspect
import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from haive.core.engine.agent import config as agent_config_module
from haive.core.utils.haive_discovery import HaiveComponentDiscovery
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["agents"])


class AgentInfo(BaseModel):
    """Information about an agent."""

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    module: str = Field(..., description="Module path")
    agent_type: str = Field(..., description="Agent type (v1 or v2)")
    version: str = Field(..., description="Agent version")
    config_class: str | None = Field(None, description="Config class for v1 agents")
    category: str = Field(default="general", description="Agent category")


class AgentSchema(BaseModel):
    """Agent configuration/input schema information."""

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: str = Field(..., description="Agent type (v1 or v2)")
    config_schema: dict[str, Any] | None = Field(
        None, description="Configuration schema for v1 agents"
    )
    init_schema: dict[str, Any] | None = Field(
        None, description="Initialization schema for v2 agents"
    )
    methods: list[str] = Field(
        default_factory=list, description="Available agent methods"
    )


class AgentListResponse(BaseModel):
    """Response for agent list endpoint."""

    agents: list[AgentInfo] = Field(..., description="List of available agents")
    count: int = Field(..., description="Total number of agents")
    v1_count: int = Field(..., description="Number of v1 agents")
    v2_count: int = Field(..., description="Number of v2 agents")


class AgentCreateRequest(BaseModel):
    """Request to create/instantiate an agent."""

    agent_name: str = Field(..., description="Name of the agent to create")
    config: dict[str, Any] | None = Field(
        None, description="Configuration for v1 agents"
    )
    init_args: dict[str, Any] | None = Field(
        None, description="Initialization arguments for v2 agents"
    )


class AgentCreateResponse(BaseModel):
    """Response from agent creation."""

    success: bool = Field(..., description="Whether creation was successful")
    agent_id: str | None = Field(None, description="Created agent ID")
    agent_type: str | None = Field(None, description="Type of created agent")
    error: str | None = Field(None, description="Error message if failed")


def discover_v1_agents() -> list[AgentInfo]:
    """Discover v1 agents from haive.engine.agent."""
    agents = []

    try:
        # Try to import haive.engine.agent modules

        # Look for config classes that end with 'Config'
        for name, obj in inspect.getmembers(agent_config_module):
            if (
                inspect.isclass(obj)
                and name.endswith("Config")
                and name != "BaseConfig"
                and hasattr(obj, "__module__")
            ):
                # Extract agent name from config name
                agent_name = name.replace("Config", "").replace("Agent", "")

                agents.append(
                    AgentInfo(
                        name=agent_name.lower(),
                        description=(
                            getattr(obj, "__doc__", "V1 config-based agent").split(
                                "\n"
                            )[0]
                            if obj.__doc__
                            else "V1 config-based agent"
                        ),
                        module="haive.core.engine.agent.config",
                        agent_type="v1",
                        version="1.0",
                        config_class=name,
                        category="v1_agent",
                    )
                )

        # Also check for generic agent with various configs
        try:
            # Look for any config classes that could be used with the generic agent
            config_classes = []
            for name, obj in inspect.getmembers(agent_config_module):
                if (
                    inspect.isclass(obj)
                    and name.endswith("Config")
                    and name not in ["BaseConfig", "AgentConfig"]
                ):
                    config_classes.append(name)

            if config_classes:
                agents.append(
                    AgentInfo(
                        name="generic_v1_agent",
                        description="Generic v1 agent that can use any config",
                        module="haive.core.engine.agent.agent",
                        agent_type="v1",
                        version="1.0",
                        config_class="GenericAgentConfig",
                        category="v1_agent",
                    )
                )

        except ImportError:
            logger.debug("Could not import v1 Agent class")

    except ImportError as e:
        logger.warning(f"Could not discover v1 agents: {e}")

    return agents


def discover_v2_agents() -> list[AgentInfo]:
    """Discover v2 agents from haive.agents.base.agent."""
    agents = []

    try:
        # Check haive.agents.base.agent

        agents.append(
            AgentInfo(
                name="base_agent_v2",
                description="Base v2 agent from haive.agents.base.agent",
                module="haive.agents.base.agent",
                agent_type="v2",
                version="2.0",
                config_class=None,
                category="v2_agent",
            )
        )

        # Try to discover other v2 agents using haive discovery
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))

            HaiveComponentDiscovery(haive_root)

            # Look for agents in haive-agents package
            agents_path = os.path.join(
                haive_root, "packages", "haive-agents", "src", "haive", "agents"
            )
            if os.path.exists(agents_path):
                # Scan for agent modules
                for root, _dirs, files in os.walk(agents_path):
                    for file in files:
                        if file.endswith(".py") and file != "__init__.py":
                            module_name = file[:-3]  # Remove .py

                            # Try to import and check for Agent classes
                            try:
                                relative_path = os.path.relpath(root, agents_path)
                                if relative_path == ".":
                                    module_path = f"haive.agents.{module_name}"
                                else:
                                    module_path = f"haive.agents.{
                                        relative_path.replace(os.sep, '.')
                                    }.{module_name}"

                                module = importlib.import_module(module_path)

                                for name, obj in inspect.getmembers(module):
                                    if (
                                        inspect.isclass(obj)
                                        and name.endswith("Agent")
                                        and name != "Agent"
                                        and obj.__module__ == module_path
                                    ):
                                        agents.append(
                                            AgentInfo(
                                                name=name.lower(),
                                                description=(
                                                    getattr(
                                                        obj, "__doc__", "V2 agent"
                                                    ).split("\n")[0]
                                                    if obj.__doc__
                                                    else "V2 agent"
                                                ),
                                                module=module_path,
                                                agent_type="v2",
                                                version="2.0",
                                                config_class=None,
                                                category="v2_agent",
                                            )
                                        )

                            except Exception as e:
                                logger.debug(f"Could not import {module_path}: {e}")
                                continue

        except Exception as e:
            logger.debug(f"Could not use discovery system for v2 agents: {e}")

    except ImportError as e:
        logger.warning(f"Could not discover v2 agents: {e}")

    return agents


def discover_all_agents() -> list[AgentInfo]:
    """Discover both v1 and v2 agents."""
    agents = []

    # Discover v1 agents
    v1_agents = discover_v1_agents()
    agents.extend(v1_agents)

    # Discover v2 agents
    v2_agents = discover_v2_agents()
    agents.extend(v2_agents)

    # Remove duplicates based on name
    seen = set()
    unique_agents = []
    for agent in agents:
        agent_key = f"{agent.name}_{agent.agent_type}"
        if agent_key not in seen:
            seen.add(agent_key)
            unique_agents.append(agent)

    return unique_agents


@router.get("/", response_model=AgentListResponse)
async def list_agents() -> AgentListResponse:
    """List all available agents (both v1 and v2).

    Returns:
        AgentListResponse containing list of available agents
    """
    try:
        agents = discover_all_agents()

        v1_count = len([a for a in agents if a.agent_type == "v1"])
        v2_count = len([a for a in agents if a.agent_type == "v2"])

        return AgentListResponse(
            agents=agents, count=len(agents), v1_count=v1_count, v2_count=v2_count
        )
    except Exception as e:
        logger.exception(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=AgentListResponse)
async def search_agents(
    query: str | None = None, agent_type: str | None = None, category: str | None = None
) -> AgentListResponse:
    """Search for agents by query, type, or category.

    Args:
        query: Search query to match against agent names and descriptions
        agent_type: Filter by agent type ('v1' or 'v2')
        category: Filter by category

    Returns:
        AgentListResponse containing filtered list of agents
    """
    try:
        agents = discover_all_agents()

        # Filter by query
        if query:
            query_lower = query.lower()
            agents = [
                agent
                for agent in agents
                if query_lower in agent.name.lower()
                or query_lower in agent.description.lower()
            ]

        # Filter by agent type
        if agent_type:
            agents = [agent for agent in agents if agent.agent_type == agent_type]

        # Filter by category
        if category:
            agents = [agent for agent in agents if agent.category == category]

        v1_count = len([a for a in agents if a.agent_type == "v1"])
        v2_count = len([a for a in agents if a.agent_type == "v2"])

        return AgentListResponse(
            agents=agents, count=len(agents), v1_count=v1_count, v2_count=v2_count
        )
    except Exception as e:
        logger.exception(f"Failed to search agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}/schema", response_model=AgentSchema)
async def get_agent_schema(agent_name: str) -> AgentSchema:
    """Get the configuration/initialization schema for a specific agent.

    Args:
        agent_name: Name of the agent to get schema for

    Returns:
        AgentSchema containing configuration and method information
    """
    try:
        agents = discover_all_agents()
        agent = next((a for a in agents if a.name == agent_name), None)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        schema_info = AgentSchema(
            name=agent.name, description=agent.description, agent_type=agent.agent_type
        )

        # Get schema based on agent type
        if agent.agent_type == "v1":
            # For v1 agents, get config schema
            try:
                module = importlib.import_module(agent.module)
                if agent.config_class:
                    config_class = getattr(module, agent.config_class, None)
                    if config_class and hasattr(config_class, "schema"):
                        schema_info.config_schema = config_class.schema()
            except Exception as e:
                logger.warning(f"Could not get config schema for {agent_name}: {e}")

        elif agent.agent_type == "v2":
            # For v2 agents, get __init__ parameters
            try:
                module = importlib.import_module(agent.module)
                # Look for the Agent class
                agent_class = None
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and (name == "Agent" or name.endswith("Agent"))
                        and obj.__module__ == agent.module
                    ):
                        agent_class = obj
                        break

                if agent_class:
                    # Get __init__ signature
                    init_sig = inspect.signature(agent_class.__init__)
                    init_params = {}

                    for param_name, param in init_sig.parameters.items():
                        if param_name != "self":
                            param_type = (
                                str(param.annotation)
                                if param.annotation != inspect.Parameter.empty
                                else "Any"
                            )
                            init_params[param_name] = {
                                "type": param_type,
                                "required": param.default == inspect.Parameter.empty,
                                "default": (
                                    param.default
                                    if param.default != inspect.Parameter.empty
                                    else None
                                ),
                            }

                    schema_info.init_schema = {
                        "type": "object",
                        "properties": init_params,
                    }

                    # Get available methods
                    methods = []
                    for name, _method in inspect.getmembers(
                        agent_class, predicate=inspect.ismethod
                    ):
                        if not name.startswith("_"):
                            methods.append(name)
                    for name, _method in inspect.getmembers(
                        agent_class, predicate=inspect.isfunction
                    ):
                        if not name.startswith("_"):
                            methods.append(name)

                    schema_info.methods = list(set(methods))

            except Exception as e:
                logger.warning(f"Could not get init schema for {agent_name}: {e}")

        return schema_info

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get agent schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}")
async def get_agent_details(agent_name: str) -> dict[str, Any]:
    """Get detailed information about a specific agent.

    Args:
        agent_name: Name of the agent to get details for

    Returns:
        Detailed information about the agent
    """
    try:
        agents = discover_all_agents()
        agent = next((a for a in agents if a.name == agent_name), None)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        details = agent.dict()

        # Add additional details
        try:
            module = importlib.import_module(agent.module)
            details["module_doc"] = getattr(
                module, "__doc__", "No module documentation"
            )
            details["module_file"] = getattr(module, "__file__", "Unknown")

            # For v1 agents, add config class info
            if agent.agent_type == "v1" and agent.config_class:
                config_class = getattr(module, agent.config_class, None)
                if config_class:
                    details["config_doc"] = getattr(
                        config_class, "__doc__", "No config documentation"
                    )

            # For v2 agents, add agent class info
            elif agent.agent_type == "v2":
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and (name == "Agent" or name.endswith("Agent"))
                        and obj.__module__ == agent.module
                    ):
                        details["agent_doc"] = getattr(
                            obj, "__doc__", "No agent documentation"
                        )
                        details["agent_class"] = name
                        break

        except Exception as e:
            logger.warning(f"Failed to load additional details for {agent_name}: {e}")

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
