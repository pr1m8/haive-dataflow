"""Agent discovery and management API routes using unified discovery system.

This module provides FastAPI routes for discovering and managing agents
using the haive-core discovery system.
"""

import inspect
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .utils.haive_discovery import ComponentInfo, HaiveComponentDiscovery

# Import discovery system


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
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


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
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AgentListResponse(BaseModel):
    """Response for agent list endpoint."""

    agents: list[AgentInfo] = Field(..., description="List of available agents")
    count: int = Field(..., description="Total number of agents")
    v1_count: int = Field(..., description="Number of v1 agents")
    v2_count: int = Field(..., description="Number of v2 agents")
    discovery_method: str = Field(
        default="haive-core unified discovery", description="Discovery method used"
    )


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


# Cache for discovered agents
_cached_agents: list[ComponentInfo] | None = None
_discovery_instance: HaiveComponentDiscovery | None = None


def get_discovery_instance() -> HaiveComponentDiscovery:
    """Get or create the discovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        # Get haive root from current location
        current_file = Path(__file__)
        haive_root = current_file.parents[6]  # Navigate up to haive root
        _discovery_instance = HaiveComponentDiscovery(str(haive_root))
    return _discovery_instance


def discover_all_agents(force_refresh: bool = False) -> list[ComponentInfo]:
    """Discover all agents using the unified discovery system."""
    global _cached_agents

    if _cached_agents is not None and not force_refresh:
        return _cached_agents

    try:
        logger.info("🔍 Starting agent discovery using haive-core discovery system...")

        discovery = get_discovery_instance()
        all_components = []

        # Discover from haive-agents package
        agents_path = (
            Path(discovery.haive_root)
            / "packages"
            / "haive-agents"
            / "src"
            / "haive"
            / "agents"
        )
        if agents_path.exists():
            agent_components = discovery.discover_from_directory(
                agents_path, "haive.agents", create_tools=False
            )
            all_components.extend(agent_components)
            logger.info(f"Found {len(agent_components)} components in haive-agents")

        # Discover from haive-core engine agents (v1 agents)
        engine_agents_path = (
            Path(discovery.haive_root)
            / "packages"
            / "haive-core"
            / "src"
            / "haive"
            / "core"
            / "engine"
            / "agent"
        )
        if engine_agents_path.exists():
            engine_components = discovery.discover_from_directory(
                engine_agents_path, "haive.core.engine.agent", create_tools=False
            )
            all_components.extend(engine_components)
            logger.info(
                f"Found {len(engine_components)} components in haive-core engine"
            )

        # Filter for agent classes and configs
        agent_components = []
        for component in all_components:
            # Check if it's an agent class
            if component.name.endswith("Agent") and component.class_obj is not None:
                # Skip base classes
                if component.name not in ["Agent", "BaseAgent", "GenericAgent"]:
                    agent_components.append(component)
                    logger.info(
                        f"✅ Found agent: {component.name} in {component.module_path}"
                    )

            # Check if it's a config class (v1 agents)
            elif (
                component.name.endswith("Config")
                and "agent" in component.module_path.lower()
            ) and component.name not in ["BaseConfig", "AgentConfig"]:
                agent_components.append(component)
                logger.info(
                    f"✅ Found agent config: {
                        component.name} in {
                        component.module_path}")

        logger.info(f"📊 Total agents discovered: {len(agent_components)}")
        _cached_agents = agent_components
        return agent_components

    except Exception as e:
        logger.error(f"❌ Error discovering agents: {e}", exc_info=True)
        return []


def component_to_agent_info(component: ComponentInfo) -> AgentInfo:
    """Convert a ComponentInfo to AgentInfo."""
    # Determine agent type based on module path
    if "haive.core.engine.agent" in component.module_path:
        agent_type = "v1"
    elif "haive.agents" in component.module_path:
        agent_type = "v2"
    else:
        agent_type = "unknown"

    # Extract name
    if component.name.endswith("Agent"):
        name = component.name[:-5].lower()  # Remove 'Agent' suffix
    elif component.name.endswith("Config"):
        name = component.name[:-6].lower()  # Remove 'Config' suffix
    else:
        name = component.name.lower()

    # Determine config class for v1 agents
    config_class = None
    if agent_type == "v1" and component.name.endswith("Config"):
        config_class = component.name

    return AgentInfo(
        name=name,
        description=component.description or f"{agent_type.upper()} agent",
        module=component.module_path,
        agent_type=agent_type,
        version=component.metadata.get("version", "1.0"),
        config_class=config_class,
        category=component.metadata.get("category", "general"),
        metadata=component.metadata,
    )


@router.get("/", response_model=AgentListResponse)
async def list_agents(force_refresh: bool = False) -> AgentListResponse:
    """List all available agents.

    Args:
        force_refresh: Force refresh the agent cache

    Returns:
        AgentListResponse containing list of available agents
    """
    try:
        components = discover_all_agents(force_refresh=force_refresh)
        agents = [component_to_agent_info(c) for c in components]

        # Remove duplicates based on name and type
        seen = set()
        unique_agents = []
        for agent in agents:
            key = f"{agent.name}_{agent.agent_type}"
            if key not in seen:
                seen.add(key)
                unique_agents.append(agent)

        v1_count = len([a for a in unique_agents if a.agent_type == "v1"])
        v2_count = len([a for a in unique_agents if a.agent_type == "v2"])

        return AgentListResponse(
            agents=unique_agents,
            count=len(unique_agents),
            v1_count=v1_count,
            v2_count=v2_count,
            discovery_method="haive-core unified discovery",
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
        components = discover_all_agents()
        agents = [component_to_agent_info(c) for c in components]

        # Remove duplicates
        seen = set()
        unique_agents = []
        for agent in agents:
            key = f"{agent.name}_{agent.agent_type}"
            if key not in seen:
                seen.add(key)
                unique_agents.append(agent)

        # Filter by query
        if query:
            query_lower = query.lower()
            unique_agents = [
                agent
                for agent in unique_agents
                if query_lower in agent.name.lower()
                or query_lower in agent.description.lower()
            ]

        # Filter by agent type
        if agent_type:
            unique_agents = [
                agent for agent in unique_agents if agent.agent_type == agent_type
            ]

        # Filter by category
        if category:
            unique_agents = [
                agent for agent in unique_agents if agent.category == category
            ]

        v1_count = len([a for a in unique_agents if a.agent_type == "v1"])
        v2_count = len([a for a in unique_agents if a.agent_type == "v2"])

        return AgentListResponse(
            agents=unique_agents,
            count=len(unique_agents),
            v1_count=v1_count,
            v2_count=v2_count,
            discovery_method="haive-core unified discovery",
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
        components = discover_all_agents()

        # Find matching component
        matching_component = None
        for component in components:
            agent_info = component_to_agent_info(component)
            if agent_info.name == agent_name:
                matching_component = component
                break

        if not matching_component:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        agent_info = component_to_agent_info(matching_component)

        schema_info = AgentSchema(
            name=agent_info.name,
            description=agent_info.description,
            agent_type=agent_info.agent_type,
            metadata=agent_info.metadata,
        )

        # Extract schema based on component metadata
        if "schema" in matching_component.metadata:
            if agent_info.agent_type == "v1":
                schema_info.config_schema = matching_component.metadata["schema"]
            else:
                schema_info.init_schema = matching_component.metadata["schema"]

        # Extract methods
        if "methods" in matching_component.metadata:
            schema_info.methods = matching_component.metadata["methods"]
        elif matching_component.class_obj:
            # Try to extract methods from class

            methods = []
            for name, method in inspect.getmembers(matching_component.class_obj):
                if not name.startswith("_") and (
                    inspect.ismethod(method) or inspect.isfunction(method)
                ):
                    methods.append(name)
            schema_info.methods = methods

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
        components = discover_all_agents()

        # Find matching component
        matching_component = None
        for component in components:
            agent_info = component_to_agent_info(component)
            if agent_info.name == agent_name:
                matching_component = component
                break

        if not matching_component:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        agent_info = component_to_agent_info(matching_component)
        details = agent_info.dict()

        # Add component details
        details["component_info"] = {
            "component_type": matching_component.component_type,
            "file_path": matching_component.file_path,
            "class_name": matching_component.class_name,
            "is_tool": matching_component.is_tool,
            "metadata": matching_component.metadata,
        }

        # Add discovery information
        details["discovery_info"] = {
            "discovered_at": matching_component.metadata.get(
                "discovered_at", "Unknown"
            ),
            "discovery_method": "haive-core unified discovery",
            "module_path": matching_component.module_path,
            "package": (
                matching_component.module_path.split(".")[0]
                if "." in matching_component.module_path
                else "Unknown"
            ),
        }

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_agent_cache() -> dict[str, Any]:
    """Refresh the agent discovery cache.

    Returns:
        Status and count of discovered agents
    """
    try:
        components = discover_all_agents(force_refresh=True)
        agents = [component_to_agent_info(c) for c in components]

        # Remove duplicates
        seen = set()
        unique_agents = []
        for agent in agents:
            key = f"{agent.name}_{agent.agent_type}"
            if key not in seen:
                seen.add(key)
                unique_agents.append(agent)

        return {
            "status": "success",
            "message": "Agent cache refreshed",
            "agent_count": len(unique_agents),
            "v1_count": len([a for a in unique_agents if a.agent_type == "v1"]),
            "v2_count": len([a for a in unique_agents if a.agent_type == "v2"]),
            "discovery_method": "haive-core unified discovery",
        }
    except Exception as e:
        logger.exception(f"Failed to refresh agent cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_agent_stats() -> dict[str, Any]:
    """Get summary statistics about discovered agents.

    Returns:
        Summary statistics
    """
    try:
        components = discover_all_agents()
        agents = [component_to_agent_info(c) for c in components]

        # Remove duplicates
        seen = set()
        unique_agents = []
        for agent in agents:
            key = f"{agent.name}_{agent.agent_type}"
            if key not in seen:
                seen.add(key)
                unique_agents.append(agent)

        # Calculate stats
        stats = {
            "total_agents": len(unique_agents),
            "v1_agents": len([a for a in unique_agents if a.agent_type == "v1"]),
            "v2_agents": len([a for a in unique_agents if a.agent_type == "v2"]),
            "categories": {},
            "modules": {},
            "discovery_method": "haive-core unified discovery",
        }

        # Count by category
        for agent in unique_agents:
            category = agent.category
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1

        # Count by module
        for agent in unique_agents:
            module_parts = agent.module.split(".")
            if len(module_parts) > 2:
                package = ".".join(module_parts[:3])  # e.g., haive.agents.base
                if package not in stats["modules"]:
                    stats["modules"][package] = 0
                stats["modules"][package] += 1

        return stats

    except Exception as e:
        logger.exception(f"Failed to get agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
