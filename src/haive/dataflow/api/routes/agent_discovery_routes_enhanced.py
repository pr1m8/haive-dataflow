"""Fixed Agent Discovery Routes using Haive Core's unified discovery system.

This module provides FastAPI routes for discovering and managing agents using the
unified discovery system from haive-core. It replaces the previous implementation
that had duplicated discovery logic.

Key Features:
    - Uses HaiveComponentDiscovery for consistent agent discovery
    - Supports both v1 (config-based) and v2 (class-based) agents
    - Provides caching for improved performance
    - Rich metadata extraction including schemas and documentation
    - Categorization and filtering capabilities

Example:
    ```python
    from fastapi import FastAPI
    from haive.dataflow.api.routes.agent_discovery_routes_fixed import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    # Endpoints available:
    # GET /api/v1/agents - List all agents
    # GET /api/v1/agents/search - Search agents
    # GET /api/v1/agents/{agent_name} - Get specific agent
    # GET /api/v1/agents/stats - Get agent statistics
    ```

Note:
    This implementation fixes the circular import issue between component_registry
    and haive_discovery by using the lazy import pattern implemented in haive-core.
"""

import contextlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from haive.dataflow.api.routes.utils.haive_discovery import (
    ComponentInfo,
    HaiveComponentDiscovery,
)

# Import discovery system


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["agents"])

# Module-level cache
_discovery_cache: dict[str, Any] = {}
_discovery_instance: HaiveComponentDiscovery | None = None

# Get haive root path
haive_root = Path(__file__).parents[6]


class AgentInfo(BaseModel):
    """Information about a discovered agent.

    Attributes:
        name: Agent identifier name (lowercase, without suffix).
        description: Human-readable description of the agent.
        module: Full module path to the agent.
        agent_type: Type of agent ('v1' for config-based, 'v2' for class-based).
        version: Agent version string.
        config_class: Name of config class for v1 agents.
        category: Agent category for grouping.
        metadata: Additional metadata from discovery.
    """

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


class AgentDetailResponse(BaseModel):
    """Detailed response for a specific agent.

    Includes all AgentInfo fields plus additional details about the
    component discovery and file location.
    """

    name: str
    description: str
    module: str
    agent_type: str
    version: str
    config_class: str | None
    category: str
    metadata: dict[str, Any]
    component_info: dict[str, Any]
    discovery_info: dict[str, Any]


class AgentListResponse(BaseModel):
    """Response for agent list endpoints.

    Attributes:
        agents: List of discovered agents.
        count: Total number of agents.
        v1_count: Number of v1 (config-based) agents.
        v2_count: Number of v2 (class-based) agents.
        discovery_method: Method used for discovery.
    """

    agents: list[AgentInfo] = Field(..., description="List of available agents")
    count: int = Field(..., description="Total number of agents")
    v1_count: int = Field(..., description="Number of v1 agents")
    v2_count: int = Field(..., description="Number of v2 agents")
    discovery_method: str = Field(
        default="haive-core unified discovery", description="Discovery method used"
    )


def get_discovery_instance() -> HaiveComponentDiscovery:
    """Get or create a cached discovery instance.

    Returns:
        HaiveComponentDiscovery: Cached discovery instance for the haive root.

    Note:
        Uses a global singleton pattern to avoid repeated initialization
        of the discovery system which can be expensive.
    """
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = HaiveComponentDiscovery(str(haive_root))
    return _discovery_instance


def discover_all_agents(force_refresh: bool = False) -> list[ComponentInfo]:
    """Discover all agents using the unified discovery system.

    Args:
        force_refresh: If True, bypasses cache and rediscovers all agents.

    Returns:
        List[ComponentInfo]: List of discovered agent components from both
        haive-agents and haive-core engine directories.

    Note:
        This function discovers agents from multiple locations:
        - haive-agents package (v2 agents)
        - haive-core engine configs (v1 agents)
    """
    if force_refresh:
        global _discovery_cache
        _discovery_cache = {}

    cache_key = "all_agents"
    if cache_key in _discovery_cache:
        return _discovery_cache[cache_key]

    try:
        logger.info(
            "Starting agent discovery using haive-core unified discovery system"
        )

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

            # Check if it's a config class (v1 agents)
            elif (
                component.name.endswith("Config")
                and "agent" in component.module_path.lower()
            ) and component.name not in ["BaseConfig", "AgentConfig"]:
                agent_components.append(component)

        logger.info(f"Total agents discovered: {len(agent_components)}")
        _discovery_cache[cache_key] = agent_components
        return agent_components

    except Exception as e:
        logger.error(f"Error discovering agents: {e}", exc_info=True)
        return []


def categorize_agents(agents: list[ComponentInfo]) -> dict[str, list[ComponentInfo]]:
    """Categorize agents by their type/category.

    Args:
        agents: List of agent components to categorize.

    Returns:
        Dict[str, List[ComponentInfo]]: Dictionary mapping category names
        to lists of agents in that category.

    Note:
        Categories are inferred from:
        - Metadata 'category' field
        - Module path components
        - Agent type (v1 vs v2)
    """
    categories = {}

    for agent in agents:
        # Try to get category from metadata
        category = agent.metadata.get("category")

        # If no category, infer from module path
        if not category:
            module_parts = agent.module_path.split(".")
            if "research" in module_parts:
                category = "research"
            elif "chat" in module_parts or "conversational" in module_parts:
                category = "chat"
            elif "task" in module_parts:
                category = "task"
            elif "engine" in module_parts:
                category = "engine"
            else:
                category = "general"

        if category not in categories:
            categories[category] = []
        categories[category].append(agent)

    return categories


def extract_agent_metadata(agent: ComponentInfo) -> dict[str, Any]:
    """Extract rich metadata from an agent component.

    Args:
        agent: ComponentInfo object representing an agent.

    Returns:
        Dict[str, Any]: Enhanced metadata including:
            - version: Agent version
            - category: Agent category
            - capabilities: List of agent capabilities
            - required_tools: Tools required by the agent
            - is_v1_agent: Whether this is a v1 (config) agent
            - is_v2_agent: Whether this is a v2 (class) agent
            - schema: Input/output schema if available

    Note:
        Attempts to extract schema information from both v1 configs
        and v2 agent classes using inspection and attribute access.
    """
    metadata = agent.metadata.copy() if agent.metadata else {}

    # Determine agent type
    is_v1 = "haive.core.engine.agent" in agent.module_path
    is_v2 = "haive.agents" in agent.module_path

    metadata["is_v1_agent"] = is_v1
    metadata["is_v2_agent"] = is_v2

    # Try to extract schema information
    if agent.class_obj:
        try:
            # For v1 agents, look for schema in config class
            if is_v1 and hasattr(agent.class_obj, "schema"):
                metadata["schema"] = agent.class_obj.schema()
            # For v2 agents, look for input/output schemas
            elif is_v2:
                if hasattr(agent.class_obj, "input_schema"):
                    metadata["input_schema"] = agent.class_obj.input_schema
                if hasattr(agent.class_obj, "output_schema"):
                    metadata["output_schema"] = agent.class_obj.output_schema
        except Exception as e:
            logger.debug(f"Could not extract schema for {agent.name}: {e}")

    # Set default version if not present
    if "version" not in metadata:
        metadata["version"] = "2.0" if is_v2 else "1.0"

    # Extract capabilities if available
    if agent.class_obj and hasattr(agent.class_obj, "capabilities"):
        with contextlib.suppress(BaseException):
            metadata["capabilities"] = agent.class_obj.capabilities

    return metadata


def component_to_agent_info(component: ComponentInfo) -> AgentInfo:
    """Convert a ComponentInfo to AgentInfo.

    Args:
        component: ComponentInfo object from discovery.

    Returns:
        AgentInfo: Structured agent information for API response.
    """
    # Extract enhanced metadata
    metadata = extract_agent_metadata(component)

    # Determine agent type
    if metadata.get("is_v1_agent"):
        agent_type = "v1"
    elif metadata.get("is_v2_agent"):
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
        version=metadata.get("version", "1.0"),
        config_class=config_class,
        category=metadata.get("category", "general"),
        metadata=metadata,
    )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    agent_type: str | None = Query(None, description="Filter by agent type (v1, v2)"),
    category: str | None = Query(None, description="Filter by category"),
    force_refresh: bool = Query(False, description="Force refresh discovery cache"),
) -> AgentListResponse:
    """List all available agents with optional filtering.

    Args:
        agent_type: Optional filter for agent type ('v1' for config-based,
                   'v2' for class-based agents).
        category: Optional category filter (e.g., 'research', 'chat').
        force_refresh: If True, forces rediscovery of all agents.

    Returns:
        AgentListResponse: Response containing:
            - List of discovered agents with metadata
            - Count statistics (total, v1, v2)
            - Discovery method information

    Example:
        ```
        GET /api/v1/agents?agent_type=v2&category=research
        ```
    """
    try:
        components = discover_all_agents(force_refresh=force_refresh)
        agents = [component_to_agent_info(c) for c in components]

        # Apply filters
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]

        if category:
            agents = [a for a in agents if a.category == category]

        # Remove duplicates based on name
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent.name not in seen:
                seen.add(agent.name)
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
    query: str = Query(..., description="Search query"),
    agent_type: str | None = Query(None, description="Filter by agent type"),
) -> AgentListResponse:
    """Search agents by name or description.

    Args:
        query: Search string to match against agent names and descriptions.
               Case-insensitive partial matching is used.
        agent_type: Optional filter for agent type ('v1' or 'v2').

    Returns:
        AgentListResponse: Filtered list of agents matching the search criteria.

    Example:
        ```
        GET /api/v1/agents/search?query=chat&agent_type=v2
        ```
    """
    try:
        components = discover_all_agents()
        agents = [component_to_agent_info(c) for c in components]

        # Search filter
        query_lower = query.lower()
        agents = [
            agent
            for agent in agents
            if query_lower in agent.name.lower()
            or query_lower in agent.description.lower()
        ]

        # Type filter
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]

        # Remove duplicates
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent.name not in seen:
                seen.add(agent.name)
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
        logger.exception(f"Failed to search agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_name}", response_model=AgentDetailResponse)
async def get_agent_details(agent_name: str) -> AgentDetailResponse:
    """Get detailed information about a specific agent.

    Args:
        agent_name: Name of the agent to retrieve details for.
                   Case-insensitive matching is used.

    Returns:
        AgentDetailResponse: Detailed agent information including:
            - Full metadata and capabilities
            - Module and file paths
            - Schema information
            - Version and category details

    Raises:
        HTTPException: 404 if agent is not found.

    Example:
        ```
        GET /api/v1/agents/SimpleAgent
        ```
    """
    try:
        components = discover_all_agents()

        # Find matching component
        matching_component = None
        agent_name_lower = agent_name.lower()

        for component in components:
            agent_info = component_to_agent_info(component)
            if agent_info.name == agent_name_lower:
                matching_component = component
                break

        if not matching_component:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        agent_info = component_to_agent_info(matching_component)

        return AgentDetailResponse(
            name=agent_info.name,
            description=agent_info.description,
            module=agent_info.module,
            agent_type=agent_info.agent_type,
            version=agent_info.version,
            config_class=agent_info.config_class,
            category=agent_info.category,
            metadata=agent_info.metadata,
            component_info={
                "component_type": matching_component.component_type,
                "file_path": matching_component.file_path,
                "class_name": matching_component.class_name,
                "is_tool": matching_component.is_tool,
                "metadata": matching_component.metadata,
            },
            discovery_info={
                "discovered_at": datetime.now().isoformat(),
                "discovery_method": "haive-core unified discovery",
                "module_path": matching_component.module_path,
                "package": matching_component.module_path.split(".")[0],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=dict[str, Any])
async def get_agent_stats() -> dict[str, Any]:
    """Get statistics about discovered agents.

    Returns:
        Dict[str, Any]: Statistics including:
            - total_agents: Total number of discovered agents
            - v1_agents: Number of config-based agents
            - v2_agents: Number of class-based agents
            - categories: Dictionary of category counts
            - discovery_sources: List of discovery source paths
            - discovery_method: Method used for discovery
            - last_updated: Timestamp of last discovery

    Example:
        ```
        GET /api/v1/agents/stats

        Response:
        {
            "total_agents": 25,
            "v1_agents": 10,
            "v2_agents": 15,
            "categories": {
                "research": 5,
                "chat": 8,
                "task": 12
            }
        }
        ```
    """
    try:
        components = discover_all_agents()
        categorized = categorize_agents(components)

        # Count unique agents
        seen_names = set()
        v1_count = 0
        v2_count = 0

        for component in components:
            agent_info = component_to_agent_info(component)
            if agent_info.name not in seen_names:
                seen_names.add(agent_info.name)
                if agent_info.agent_type == "v1":
                    v1_count += 1
                elif agent_info.agent_type == "v2":
                    v2_count += 1

        # Category counts
        category_counts = {
            category: len(agents) for category, agents in categorized.items()
        }

        return {
            "total_agents": len(seen_names),
            "v1_agents": v1_count,
            "v2_agents": v2_count,
            "categories": category_counts,
            "discovery_sources": ["haive-agents", "haive-core/engine/agent"],
            "discovery_method": "haive-core unified discovery",
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to get agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
