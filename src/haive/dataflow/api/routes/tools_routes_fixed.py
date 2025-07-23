"""Tools API routes using the unified discovery system.

This module provides FastAPI routes for discovering and listing all available
tools in the Haive ecosystem using the haive-core discovery system.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import discovery system
from .utils.haive_discovery import (
    ComponentInfo,
    HaiveComponentDiscovery,
    create_tool_from_component,
    discover_tools,
    discover_tools_with_schemas,
    get_all_tools,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tools", tags=["tools"])


class ToolInfo(BaseModel):
    """Information about a tool."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    module: str = Field(..., description="Module path")
    type: str = Field(..., description="Tool type (tool or toolkit)")
    category: str = Field(default="general", description="Tool category")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ToolsListResponse(BaseModel):
    """Response for tools list endpoint."""

    tools: List[ToolInfo] = Field(..., description="List of available tools")
    count: int = Field(..., description="Total number of tools")
    tool_count: int = Field(..., description="Number of individual tools")
    toolkit_count: int = Field(..., description="Number of toolkits")
    discovery_method: str = Field(
        default="haive-core unified discovery", description="Discovery method used"
    )


class ToolSchema(BaseModel):
    """Tool input/output schema information."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(
        None, description="Output schema if available"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ToolInvokeRequest(BaseModel):
    """Request to invoke a tool."""

    tool_name: str = Field(..., description="Name of the tool to invoke")
    arguments: Dict[str, Any] = Field(..., description="Arguments to pass to the tool")


class ToolInvokeResponse(BaseModel):
    """Response from tool invocation."""

    success: bool = Field(..., description="Whether invocation was successful")
    result: Any = Field(None, description="Result from the tool")
    error: Optional[str] = Field(None, description="Error message if failed")


# Cache for discovered tools
_cached_tools: Optional[List[ComponentInfo]] = None
_discovery_instance: Optional[HaiveComponentDiscovery] = None


def get_discovery_instance() -> HaiveComponentDiscovery:
    """Get or create the discovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        # Get haive root from current location
        current_file = Path(__file__)
        haive_root = current_file.parents[6]  # Navigate up to haive root
        _discovery_instance = HaiveComponentDiscovery(str(haive_root))
    return _discovery_instance


def discover_all_tools(force_refresh: bool = False) -> List[ComponentInfo]:
    """Discover all tools using the unified discovery system."""
    global _cached_tools

    if _cached_tools is not None and not force_refresh:
        return _cached_tools

    try:
        logger.info("🔍 Starting tool discovery using haive-core discovery system...")

        # Use the discovery system's tool discovery with schemas
        tool_components = discover_tools_with_schemas()

        logger.info(f"📊 Total tools discovered: {len(tool_components)}")

        # Log each discovered tool
        for component in tool_components:
            logger.info(f"✅ Found tool: {component.name} in {component.module_path}")

        _cached_tools = tool_components
        return tool_components

    except Exception as e:
        logger.error(f"❌ Error discovering tools: {e}", exc_info=True)
        # Fallback to manual discovery
        return discover_tools_fallback()


def discover_tools_fallback() -> List[ComponentInfo]:
    """Fallback tool discovery if the main discovery fails."""
    try:
        logger.info("Using fallback tool discovery...")
        discovery = get_discovery_instance()

        all_tools = []

        # Discover individual tools
        individual_tools = discovery.discover_individual_tools(create_tools=False)
        all_tools.extend(individual_tools)
        logger.info(f"Found {len(individual_tools)} individual tools")

        # Discover toolkits
        toolkits = discovery.discover_toolkits(create_tools=False)
        all_tools.extend(toolkits)
        logger.info(f"Found {len(toolkits)} toolkits")

        return all_tools

    except Exception as e:
        logger.error(f"Fallback discovery also failed: {e}")
        return []


def component_to_tool_info(component: ComponentInfo) -> ToolInfo:
    """Convert a ComponentInfo to ToolInfo."""
    # Determine tool type
    if "toolkit" in component.module_path.lower() or component.name.endswith("Toolkit"):
        tool_type = "toolkit"
    else:
        tool_type = "tool"

    # Extract category from metadata or module path
    category = component.metadata.get("category", "general")
    if category == "general":
        # Try to infer from module path
        if "search" in component.module_path.lower():
            category = "search"
        elif (
            "database" in component.module_path.lower()
            or "sql" in component.module_path.lower()
        ):
            category = "database"
        elif (
            "github" in component.module_path.lower()
            or "git" in component.module_path.lower()
        ):
            category = "development"
        elif (
            "arxiv" in component.module_path.lower()
            or "research" in component.module_path.lower()
        ):
            category = "research"
        elif (
            "compute" in component.module_path.lower()
            or "calc" in component.module_path.lower()
        ):
            category = "computation"

    return ToolInfo(
        name=component.name,
        description=component.description or "No description available",
        module=component.module_path,
        type=tool_type,
        category=category,
        metadata=component.metadata,
    )


@router.get("/", response_model=ToolsListResponse)
async def list_tools(force_refresh: bool = False) -> ToolsListResponse:
    """List all available tools.

    Args:
        force_refresh: Force refresh the tool cache

    Returns:
        ToolsListResponse containing list of available tools and total count
    """
    try:
        components = discover_all_tools(force_refresh=force_refresh)
        tools = [component_to_tool_info(c) for c in components]

        tool_count = len([t for t in tools if t.type == "tool"])
        toolkit_count = len([t for t in tools if t.type == "toolkit"])

        logger.info(f"Returning {len(tools)} tools: {[t.name for t in tools]}")

        return ToolsListResponse(
            tools=tools,
            count=len(tools),
            tool_count=tool_count,
            toolkit_count=toolkit_count,
            discovery_method="haive-core unified discovery",
        )
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=ToolsListResponse)
async def search_tools(
    query: str = None, category: str = None, tool_type: str = None
) -> ToolsListResponse:
    """Search for tools by query, category, or type.

    Args:
        query: Search query to match against tool names and descriptions
        category: Filter by category (e.g., 'search', 'development', 'database')
        tool_type: Filter by type ('tool' or 'toolkit')

    Returns:
        ToolsListResponse containing filtered list of tools
    """
    try:
        components = discover_all_tools()
        tools = [component_to_tool_info(c) for c in components]

        # Filter by query
        if query:
            query_lower = query.lower()
            tools = [
                tool
                for tool in tools
                if query_lower in tool.name.lower()
                or query_lower in tool.description.lower()
            ]

        # Filter by category
        if category:
            tools = [tool for tool in tools if tool.category == category]

        # Filter by type
        if tool_type:
            tools = [tool for tool in tools if tool.type == tool_type]

        tool_count = len([t for t in tools if t.type == "tool"])
        toolkit_count = len([t for t in tools if t.type == "toolkit"])

        return ToolsListResponse(
            tools=tools,
            count=len(tools),
            tool_count=tool_count,
            toolkit_count=toolkit_count,
            discovery_method="haive-core unified discovery",
        )
    except Exception as e:
        logger.error(f"Failed to search tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_name}/schema", response_model=ToolSchema)
async def get_tool_schema_endpoint(tool_name: str) -> ToolSchema:
    """Get the input/output schema for a specific tool.

    Args:
        tool_name: Name of the tool to get schema for

    Returns:
        ToolSchema containing input and output schemas
    """
    try:
        components = discover_all_tools()

        # Find matching component
        matching_component = None
        for component in components:
            if component.name == tool_name:
                matching_component = component
                break

        if not matching_component:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        tool_info = component_to_tool_info(matching_component)

        # Extract schema from component metadata
        input_schema = matching_component.metadata.get("schema", {})
        if not input_schema and "input_schema" in matching_component.metadata:
            input_schema = matching_component.metadata["input_schema"]

        # If no schema in metadata, try to extract from the tool itself
        if not input_schema and matching_component.class_obj:
            try:
                # For LangChain tools
                if hasattr(matching_component.class_obj, "args_schema"):
                    input_schema = matching_component.class_obj.args_schema.schema()
                # For other tools, try to get from class
                elif hasattr(matching_component.class_obj, "get_input_schema"):
                    input_schema = matching_component.class_obj.get_input_schema()
            except Exception as e:
                logger.warning(f"Could not extract schema from tool class: {e}")

        # Default schema structure
        if not input_schema:
            input_schema = {
                "type": "object",
                "properties": {},
                "description": f"Input schema for {tool_name}",
            }

        return ToolSchema(
            name=tool_info.name,
            description=tool_info.description,
            input_schema=input_schema,
            output_schema=matching_component.metadata.get("output_schema"),
            metadata=tool_info.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoke", response_model=ToolInvokeResponse)
async def invoke_tool_endpoint(request: ToolInvokeRequest) -> ToolInvokeResponse:
    """Invoke a tool with the provided arguments.

    Args:
        request: Tool invocation request with tool name and arguments

    Returns:
        ToolInvokeResponse with the result or error
    """
    try:
        components = discover_all_tools()

        # Find matching component
        matching_component = None
        for component in components:
            if component.name == request.tool_name:
                matching_component = component
                break

        if not matching_component:
            return ToolInvokeResponse(
                success=False, error=f"Tool '{request.tool_name}' not found"
            )

        # Try to create and invoke the tool
        try:
            # Create tool instance from component
            tool = create_tool_from_component(matching_component)

            # Invoke the tool
            if hasattr(tool, "invoke"):
                result = (
                    await tool.invoke(request.arguments)
                    if asyncio.iscoroutinefunction(tool.invoke)
                    else tool.invoke(request.arguments)
                )
            elif hasattr(tool, "run"):
                result = (
                    await tool.run(request.arguments)
                    if asyncio.iscoroutinefunction(tool.run)
                    else tool.run(request.arguments)
                )
            elif callable(tool):
                result = (
                    await tool(**request.arguments)
                    if asyncio.iscoroutinefunction(tool)
                    else tool(**request.arguments)
                )
            else:
                return ToolInvokeResponse(
                    success=False, error="Tool does not have a callable interface"
                )

            return ToolInvokeResponse(success=True, result=result)

        except Exception as e:
            logger.error(f"Error invoking tool: {e}")
            return ToolInvokeResponse(success=False, error=str(e))

    except Exception as e:
        logger.error(f"Failed to invoke tool: {e}")
        return ToolInvokeResponse(success=False, error=str(e))


@router.get("/{tool_name}")
async def get_tool_details(tool_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific tool.

    Args:
        tool_name: Name of the tool to get details for

    Returns:
        Detailed information about the tool
    """
    try:
        components = discover_all_tools()

        # Find matching component
        matching_component = None
        for component in components:
            if component.name == tool_name:
                matching_component = component
                break

        if not matching_component:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        tool_info = component_to_tool_info(matching_component)
        details = tool_info.dict()

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

        # For toolkits, try to get the list of tools
        if tool_info.type == "toolkit" and matching_component.class_obj:
            try:
                if hasattr(matching_component.class_obj, "get_tools"):
                    toolkit_instance = matching_component.class_obj()
                    tools = toolkit_instance.get_tools()
                    details["available_tools"] = [str(t) for t in tools]
            except Exception as e:
                logger.warning(f"Could not get toolkit tools: {e}")

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_tool_cache() -> Dict[str, Any]:
    """Refresh the tool discovery cache.

    Returns:
        Status and count of discovered tools
    """
    try:
        components = discover_all_tools(force_refresh=True)
        tools = [component_to_tool_info(c) for c in components]

        tool_count = len([t for t in tools if t.type == "tool"])
        toolkit_count = len([t for t in tools if t.type == "toolkit"])

        return {
            "status": "success",
            "message": "Tool cache refreshed",
            "total_tools": len(tools),
            "tool_count": tool_count,
            "toolkit_count": toolkit_count,
            "discovery_method": "haive-core unified discovery",
        }
    except Exception as e:
        logger.error(f"Failed to refresh tool cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_tool_stats() -> Dict[str, Any]:
    """Get summary statistics about discovered tools.

    Returns:
        Summary statistics
    """
    try:
        components = discover_all_tools()
        tools = [component_to_tool_info(c) for c in components]

        # Calculate stats
        stats = {
            "total_tools": len(tools),
            "individual_tools": len([t for t in tools if t.type == "tool"]),
            "toolkits": len([t for t in tools if t.type == "toolkit"]),
            "categories": {},
            "modules": {},
            "discovery_method": "haive-core unified discovery",
        }

        # Count by category
        for tool in tools:
            category = tool.category
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1

        # Count by module
        for tool in tools:
            module_parts = tool.module.split(".")
            if len(module_parts) > 2:
                package = ".".join(module_parts[:3])  # e.g., haive.tools.tools
                if package not in stats["modules"]:
                    stats["modules"][package] = 0
                stats["modules"][package] += 1

        return stats

    except Exception as e:
        logger.error(f"Failed to get tool stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_tool_categories() -> Dict[str, List[str]]:
    """Get all available tool categories and their tools.

    Returns:
        Dictionary mapping categories to tool names
    """
    try:
        components = discover_all_tools()
        tools = [component_to_tool_info(c) for c in components]

        categories = {}
        for tool in tools:
            if tool.category not in categories:
                categories[tool.category] = []
            categories[tool.category].append(tool.name)

        # Sort tools in each category
        for category in categories:
            categories[category].sort()

        return categories

    except Exception as e:
        logger.error(f"Failed to get tool categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
