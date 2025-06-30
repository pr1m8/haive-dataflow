"""Enhanced Tools Discovery API Routes using Haive Core's unified discovery system.

This module provides FastAPI routes for discovering, managing, and invoking tools
using the unified discovery system from haive-core. It supports both individual
tools and toolkits with comprehensive schema extraction.

Key Features:
    - Unified tool discovery using haive-core's discovery system
    - Support for both individual tools and toolkits
    - Schema extraction and validation
    - Tool invocation capabilities
    - Category-based organization
    - Performance caching

Example:
    ```python
    from fastapi import FastAPI
    from haive.dataflow.api.routes.tools_routes_enhanced import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    # Endpoints available:
    # GET /api/v1/tools - List all tools
    # GET /api/v1/tools/search - Search tools
    # GET /api/v1/tools/{tool_name}/schema - Get tool schema
    # POST /api/v1/tools/invoke - Invoke a tool
    ```

Note:
    This implementation uses the fixed circular import pattern from haive-core
    to properly integrate with the discovery system.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

# Import discovery system
from haive.core.utils.haive_discovery import (
    ComponentInfo,
    create_tool_from_component,
    discover_tools_with_schemas,
)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tools", tags=["tools"])

# Module-level cache
_discovery_cache: Dict[str, Any] = {}


class ToolInfo(BaseModel):
    """Information about a discovered tool or toolkit.

    Attributes:
        name: Tool identifier name.
        description: Human-readable description.
        module: Full module path to the tool.
        type: Type of tool ('tool' for individual, 'toolkit' for collection).
        category: Category for grouping (e.g., 'search', 'database').
        has_schema: Whether the tool has a defined input schema.
        metadata: Additional metadata from discovery.
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    module: str = Field(..., description="Module path")
    type: str = Field(..., description="Tool type (tool or toolkit)")
    category: str = Field(default="general", description="Tool category")
    has_schema: bool = Field(default=False, description="Whether tool has input schema")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ToolsListResponse(BaseModel):
    """Response for tools list endpoints.

    Attributes:
        tools: List of discovered tools with metadata.
        count: Total number of tools and toolkits.
        tool_count: Number of individual tools.
        toolkit_count: Number of toolkits.
        discovery_method: Method used for discovery.
    """

    tools: List[ToolInfo] = Field(..., description="List of available tools")
    count: int = Field(..., description="Total number of tools")
    tool_count: int = Field(..., description="Number of individual tools")
    toolkit_count: int = Field(..., description="Number of toolkits")
    discovery_method: str = Field(
        default="haive-core unified discovery", description="Discovery method used"
    )


class ToolSchema(BaseModel):
    """Tool input/output schema information.

    Attributes:
        name: Tool name.
        description: Tool description.
        input_schema: JSON Schema for tool input parameters.
        output_schema: JSON Schema for tool output (if available).
        examples: Usage examples (if available).
        metadata: Additional schema metadata.
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(
        None, description="Output schema if available"
    )
    examples: Optional[List[Dict[str, Any]]] = Field(None, description="Usage examples")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


def discover_all_tools(force_refresh: bool = False) -> List[ComponentInfo]:
    """Discover all tools using the unified discovery system.

    Args:
        force_refresh: If True, bypasses cache and rediscovers all tools.

    Returns:
        List[ComponentInfo]: List of discovered tool components including
        both individual tools and toolkits.

    Note:
        Uses haive-core's discover_tools_with_schemas for comprehensive
        discovery with schema extraction.
    """
    cache_key = "all_tools"

    if force_refresh:
        global _discovery_cache
        _discovery_cache = {}
    elif cache_key in _discovery_cache:
        return _discovery_cache[cache_key]

    try:
        logger.info("Starting tool discovery using haive-core unified discovery system")

        # Use the discovery system's tool discovery with schemas
        tool_components = discover_tools_with_schemas()

        logger.info(f"Total tools discovered: {len(tool_components)}")

        # Cache the results
        _discovery_cache[cache_key] = tool_components
        _discovery_cache["last_updated"] = datetime.now()

        return tool_components

    except Exception as e:
        logger.error(f"Error discovering tools: {e}", exc_info=True)
        return []


def infer_tool_category(component: ComponentInfo) -> str:
    """Infer tool category from component information.

    Args:
        component: ComponentInfo object representing a tool.

    Returns:
        str: Inferred category name.

    Note:
        Categories are inferred from:
        1. Metadata 'category' field
        2. Module path keywords
        3. Tool name patterns
    """
    # Check metadata first
    category = component.metadata.get("category")
    if category and category != "general":
        return category

    # Infer from module path and name
    path_lower = component.module_path.lower()
    name_lower = component.name.lower()

    # Category mapping rules
    if any(x in path_lower for x in ["search", "google", "bing", "duckduckgo"]):
        return "search"
    elif any(x in path_lower for x in ["database", "sql", "mongodb", "redis"]):
        return "database"
    elif any(x in path_lower for x in ["github", "git", "gitlab", "dev"]):
        return "development"
    elif any(x in path_lower for x in ["arxiv", "research", "pubmed", "scholar"]):
        return "research"
    elif any(x in path_lower for x in ["compute", "calc", "math", "wolfram"]):
        return "computation"
    elif any(x in path_lower for x in ["weather", "climate"]):
        return "weather"
    elif any(x in path_lower for x in ["finance", "stock", "crypto"]):
        return "finance"
    elif any(x in path_lower for x in ["translate", "language"]):
        return "language"
    elif any(x in path_lower for x in ["email", "gmail", "office"]):
        return "communication"
    elif "toolkit" in name_lower:
        return "toolkit"
    else:
        return "general"


def extract_tool_schema(component: ComponentInfo) -> Optional[Dict[str, Any]]:
    """Extract schema information from a tool component.

    Args:
        component: ComponentInfo object representing a tool.

    Returns:
        Optional[Dict[str, Any]]: Extracted schema or None if not available.

    Note:
        Attempts multiple strategies to extract schema:
        1. From metadata 'schema' field
        2. From LangChain tool args_schema
        3. From custom get_input_schema method
        4. From Pydantic model if available
    """
    # Check metadata first
    if "schema" in component.metadata:
        return component.metadata["schema"]

    # Try to extract from tool class
    if component.class_obj:
        try:
            # LangChain tools
            if hasattr(component.class_obj, "args_schema"):
                return component.class_obj.args_schema.schema()

            # Custom schema method
            if hasattr(component.class_obj, "get_input_schema"):
                return component.class_obj.get_input_schema()

            # Pydantic model
            if hasattr(component.class_obj, "__fields__"):
                return component.class_obj.schema()

        except Exception as e:
            logger.debug(f"Could not extract schema for {component.name}: {e}")

    return None


def component_to_tool_info(component: ComponentInfo) -> ToolInfo:
    """Convert a ComponentInfo to ToolInfo.

    Args:
        component: ComponentInfo object from discovery.

    Returns:
        ToolInfo: Structured tool information for API response.
    """
    # Determine tool type
    is_toolkit = "toolkit" in component.module_path.lower() or component.name.endswith(
        "Toolkit"
    )
    tool_type = "toolkit" if is_toolkit else "tool"

    # Get category
    category = infer_tool_category(component)

    # Check for schema
    schema = extract_tool_schema(component)
    has_schema = schema is not None

    # Enhanced metadata
    metadata = component.metadata.copy()
    metadata["has_class"] = component.class_obj is not None
    metadata["component_type"] = component.component_type

    return ToolInfo(
        name=component.name,
        description=component.description or "No description available",
        module=component.module_path,
        type=tool_type,
        category=category,
        has_schema=has_schema,
        metadata=metadata,
    )


@router.get("/", response_model=ToolsListResponse)
async def list_tools(
    tool_type: Optional[str] = Query(
        None, description="Filter by type (tool, toolkit)"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    force_refresh: bool = Query(False, description="Force refresh discovery cache"),
) -> ToolsListResponse:
    """List all available tools with optional filtering.

    Args:
        tool_type: Optional filter for tool type ('tool' or 'toolkit').
        category: Optional category filter (e.g., 'search', 'database').
        force_refresh: If True, forces rediscovery of all tools.

    Returns:
        ToolsListResponse: Response containing:
            - List of discovered tools with metadata
            - Count statistics
            - Discovery method information

    Example:
        ```
        GET /api/v1/tools?tool_type=toolkit&category=search
        ```
    """
    try:
        components = discover_all_tools(force_refresh=force_refresh)
        tools = [component_to_tool_info(c) for c in components]

        # Apply filters
        if tool_type:
            tools = [t for t in tools if t.type == tool_type]

        if category:
            tools = [t for t in tools if t.category == category]

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
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=ToolsListResponse)
async def search_tools(
    query: str = Query(..., description="Search query"),
    tool_type: Optional[str] = Query(None, description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
) -> ToolsListResponse:
    """Search tools by name, description, or module path.

    Args:
        query: Search string to match against tool attributes.
               Case-insensitive partial matching is used.
        tool_type: Optional filter for tool type.
        category: Optional category filter.

    Returns:
        ToolsListResponse: Filtered list of tools matching the search criteria.

    Example:
        ```
        GET /api/v1/tools/search?query=google&tool_type=toolkit
        ```
    """
    try:
        components = discover_all_tools()
        tools = [component_to_tool_info(c) for c in components]

        # Search filter
        query_lower = query.lower()
        tools = [
            tool
            for tool in tools
            if query_lower in tool.name.lower()
            or query_lower in tool.description.lower()
            or query_lower in tool.module.lower()
        ]

        # Additional filters
        if tool_type:
            tools = [t for t in tools if t.type == tool_type]

        if category:
            tools = [t for t in tools if t.category == category]

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
        tool_name: Name of the tool to get schema for.
                   Case-sensitive exact matching is used.

    Returns:
        ToolSchema: Schema information including:
            - Input parameter schema (JSON Schema format)
            - Output schema if available
            - Usage examples if available

    Raises:
        HTTPException: 404 if tool is not found.

    Example:
        ```
        GET /api/v1/tools/GoogleSearchTool/schema
        ```
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

        # Extract comprehensive schema
        input_schema = extract_tool_schema(matching_component)

        # Default schema if none found
        if not input_schema:
            input_schema = {
                "type": "object",
                "properties": {},
                "description": f"Input schema for {tool_name}",
            }

        # Extract examples if available
        examples = matching_component.metadata.get("examples", [])

        return ToolSchema(
            name=tool_info.name,
            description=tool_info.description,
            input_schema=input_schema,
            output_schema=matching_component.metadata.get("output_schema"),
            examples=examples if examples else None,
            metadata=tool_info.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=Dict[str, List[str]])
async def get_tool_categories() -> Dict[str, List[str]]:
    """Get all available tool categories and their tools.

    Returns:
        Dict[str, List[str]]: Dictionary mapping category names to
        sorted lists of tool names in each category.

    Example:
        ```
        GET /api/v1/tools/categories

        Response:
        {
            "search": ["GoogleSearchTool", "BingSearchTool"],
            "database": ["SQLDatabaseToolkit", "MongoDBToolkit"],
            "development": ["GithubToolkit", "GitLabToolkit"]
        }
        ```
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


@router.get("/stats", response_model=Dict[str, Any])
async def get_tool_stats() -> Dict[str, Any]:
    """Get statistics about discovered tools.

    Returns:
        Dict[str, Any]: Statistics including:
            - total_tools: Total number of tools and toolkits
            - individual_tools: Number of individual tools
            - toolkits: Number of toolkits
            - categories: Count by category
            - with_schema: Number of tools with schemas
            - discovery_method: Method used
            - last_updated: Cache timestamp

    Example:
        ```
        GET /api/v1/tools/stats

        Response:
        {
            "total_tools": 50,
            "individual_tools": 35,
            "toolkits": 15,
            "categories": {
                "search": 8,
                "database": 10,
                "development": 12
            },
            "with_schema": 45
        }
        ```
    """
    try:
        components = discover_all_tools()
        tools = [component_to_tool_info(c) for c in components]

        # Calculate statistics
        stats = {
            "total_tools": len(tools),
            "individual_tools": len([t for t in tools if t.type == "tool"]),
            "toolkits": len([t for t in tools if t.type == "toolkit"]),
            "categories": {},
            "with_schema": len([t for t in tools if t.has_schema]),
            "discovery_method": "haive-core unified discovery",
            "last_updated": _discovery_cache.get(
                "last_updated", datetime.now()
            ).isoformat(),
        }

        # Count by category
        for tool in tools:
            category = tool.category
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1

        return stats

    except Exception as e:
        logger.error(f"Failed to get tool stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
