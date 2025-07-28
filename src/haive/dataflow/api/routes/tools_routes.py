"""Tools API routes for discovering and listing available tools.

This module provides FastAPI routes for discovering and listing all available
tools in the Haive ecosystem. It scans the haive-tools package and returns
information about available tools and toolkits.
"""

import inspect
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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


class ToolsListResponse(BaseModel):
    """Response for tools list endpoint."""

    tools: List[ToolInfo] = Field(..., description="List of available tools")
    count: int = Field(..., description="Total number of tools")


class ToolSchema(BaseModel):
    """Tool input/output schema information."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(
        None, description="Output schema if available"
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


def discover_tools() -> List[ToolInfo]:
    """Discover all available tools from haive-tools package."""
    tools = []

    try:
        # Try using haive discovery system first
        import os

        from haive.core.utils.haive_discovery import HaiveComponentDiscovery

        # Get haive root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))

        discovery = HaiveComponentDiscovery(haive_root)

        # Discover individual tools
        tool_components = discovery.discover_individual_tools(create_tools=False)
        for component in tool_components:
            tools.append(
                ToolInfo(
                    name=component.name,
                    description=component.description or "No description available",
                    module=component.module_path,
                    type="tool",
                    category=component.metadata.get("category", "general"),
                )
            )

        # Discover toolkits
        toolkit_components = discovery.discover_toolkits(create_tools=False)
        for component in toolkit_components:
            tools.append(
                ToolInfo(
                    name=component.name,
                    description=component.description or "No description available",
                    module=component.module_path,
                    type="toolkit",
                    category=component.metadata.get("category", "toolkit"),
                )
            )

    except ImportError as e:
        logger.warning(f"Could not use haive discovery system: {e}")
        # Fall back to manual discovery
        try:
            # Import haive.tools to get available tools
            import haive.tools
            from haive.tools import toolkits as toolkits_module
            from haive.tools import tools as tools_module

            # Discover individual tools
            if hasattr(tools_module, "__all__"):
                for tool_name in tools_module.__all__:
                    try:
                        tool_module = getattr(tools_module, tool_name, None)
                        if tool_module:
                            tools.append(
                                ToolInfo(
                                    name=tool_name,
                                    description=getattr(
                                        tool_module,
                                        "__doc__",
                                        "No description available",
                                    ).split("\n")[0],
                                    module=f"haive.tools.tools.{tool_name}",
                                    type="tool",
                                    category="tool",
                                )
                            )
                    except Exception as e:
                        logger.warning(f"Failed to load tool {tool_name}: {e}")

            # Discover toolkits
            if hasattr(toolkits_module, "__all__"):
                for toolkit_name in toolkits_module.__all__:
                    try:
                        toolkit_module = getattr(toolkits_module, toolkit_name, None)
                        if toolkit_module:
                            tools.append(
                                ToolInfo(
                                    name=toolkit_name,
                                    description=getattr(
                                        toolkit_module,
                                        "__doc__",
                                        "No description available",
                                    ).split("\n")[0],
                                    module=f"haive.tools.toolkits.{toolkit_name}",
                                    type="toolkit",
                                    category="toolkit",
                                )
                            )
                    except Exception as e:
                        logger.warning(f"Failed to load toolkit {toolkit_name}: {e}")

        except ImportError as e2:
            logger.error(f"Failed to import haive.tools: {e2}")

            # Try to discover by scanning the package structure
            import importlib
            import pkgutil

            # Scan tools directory
            try:
                tools_path = haive.tools.tools.__path__
                for _importer, modname, ispkg in pkgutil.iter_modules(tools_path):
                    if not ispkg and not modname.startswith("_"):
                        try:
                            module = importlib.import_module(
                                f"haive.tools.tools.{modname}"
                            )
                            tools.append(
                                ToolInfo(
                                    name=modname,
                                    description=(
                                        getattr(
                                            module,
                                            "__doc__",
                                            "No description available",
                                        ).split("\n")[0]
                                        if getattr(module, "__doc__", None)
                                        else "No description available"
                                    ),
                                    module=f"haive.tools.tools.{modname}",
                                    type="tool",
                                    category="tool",
                                )
                            )
                        except Exception as e:
                            logger.debug(f"Failed to import tool module {modname}: {e}")
            except Exception as e:
                logger.warning(f"Failed to scan tools directory: {e}")

            # Scan toolkits directory
            try:
                toolkits_path = haive.tools.toolkits.__path__
                for _importer, modname, ispkg in pkgutil.iter_modules(toolkits_path):
                    if not modname.startswith("_"):
                        try:
                            module = importlib.import_module(
                                f"haive.tools.toolkits.{modname}"
                            )
                            tools.append(
                                ToolInfo(
                                    name=modname,
                                    description=(
                                        getattr(
                                            module,
                                            "__doc__",
                                            "No description available",
                                        ).split("\n")[0]
                                        if getattr(module, "__doc__", None)
                                        else "No description available"
                                    ),
                                    module=f"haive.tools.toolkits.{modname}",
                                    type="toolkit",
                                    category="toolkit",
                                )
                            )
                        except Exception as e:
                            logger.debug(
                                f"Failed to import toolkit module {modname}: {e}"
                            )
            except Exception as e:
                logger.warning(f"Failed to scan toolkits directory: {e}")

        except Exception as e:
            logger.error(f"Failed to scan package structure: {e}")

    except ImportError as e:
        logger.error(f"Failed to import haive.tools: {e}")
        # Return some hardcoded tools as fallback
        tools = [
            ToolInfo(
                name="calculator",
                description="Simple calculator tool",
                module="haive.dataflow.api.routes.example_tool",
                type="tool",
                category="computation",
            ),
            ToolInfo(
                name="simple_search",
                description="Simple search function",
                module="haive.dataflow.api.routes.example_tool",
                type="tool",
                category="search",
            ),
            ToolInfo(
                name="brave_search",
                description="Brave search tool for web searches",
                module="haive.tools.tools.brave_search",
                type="tool",
                category="search",
            ),
            ToolInfo(
                name="wolfram_alpha_tool",
                description="Wolfram Alpha computational tool",
                module="haive.tools.tools.wolfram_alpha_tool",
                type="tool",
                category="computation",
            ),
            ToolInfo(
                name="arxiv",
                description="ArXiv paper search tool",
                module="haive.tools.tools.arxiv",
                type="tool",
                category="research",
            ),
            ToolInfo(
                name="github_toolkit",
                description="GitHub API toolkit",
                module="haive.tools.toolkits.github_toolkit",
                type="toolkit",
                category="development",
            ),
            ToolInfo(
                name="sql_db_toolkit",
                description="SQL database toolkit",
                module="haive.tools.toolkits.sql_db_toolkit",
                type="toolkit",
                category="database",
            ),
        ]

    # Remove duplicates based on name
    seen = set()
    unique_tools = []
    for tool in tools:
        if tool.name not in seen:
            seen.add(tool.name)
            unique_tools.append(tool)

    return unique_tools


def simple_discover_tools() -> List[ToolInfo]:
    """Simple tool discovery that always works."""
    tools = [
        ToolInfo(
            name="calculator",
            description="Simple calculator tool",
            module="haive.dataflow.api.routes.example_tool",
            type="tool",
            category="computation",
        ),
        ToolInfo(
            name="simple_search",
            description="Simple search function",
            module="haive.dataflow.api.routes.example_tool",
            type="tool",
            category="search",
        ),
    ]

    # Try to add real tools
    try:
        import importlib
        import pkgutil

        import haive.tools.tools

        for _importer, modname, ispkg in pkgutil.iter_modules(
            haive.tools.tools.__path__
        ):
            if not ispkg and not modname.startswith("_") and modname != "__init__":
                try:
                    importlib.import_module(f"haive.tools.tools.{modname}")
                    tools.append(
                        ToolInfo(
                            name=modname,
                            description=f"Tool from {modname}",
                            module=f"haive.tools.tools.{modname}",
                            type="tool",
                            category="tool",
                        )
                    )
                except:
                    pass
    except:
        pass

    return tools


@router.get("/", response_model=ToolsListResponse)
async def list_tools() -> ToolsListResponse:
    """List all available tools.

    Returns:
        ToolsListResponse containing list of available tools and total count
    """
    try:
        tools = simple_discover_tools()
        logger.info(f"Returning {len(tools)} tools: {[t.name for t in tools]}")
        return ToolsListResponse(tools=tools, count=len(tools))
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
        tools = simple_discover_tools()

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

        return ToolsListResponse(tools=tools, count=len(tools))
    except Exception as e:
        logger.error(f"Failed to search tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_tool_schema(tool_module_path: str) -> Dict[str, Any]:
    """Extract input schema from a tool module."""
    try:
        import importlib

        module = importlib.import_module(tool_module_path)

        # Get the tool name from the module path
        tool_name = tool_module_path.split(".")[-1]

        # Try to find the specific tool class or function
        tool_class = None
        tool_func = None

        # First check if there's a specific class matching the tool name
        for name, obj in inspect.getmembers(module):
            if (
                name.lower() == tool_name.lower()
                or name.lower() == f"{tool_name.lower()}tool"
            ):
                if inspect.isclass(obj):
                    tool_class = obj
                    break
                elif inspect.isfunction(obj):
                    tool_func = obj
                    break

        # If not found, look for any Tool/Toolkit class
        if not tool_class and not tool_func:
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and (
                    name.endswith("Tool") or name.endswith("Toolkit")
                ):
                    tool_class = obj
                    break

        if not tool_class:
            # Look for a function-based tool
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    # Get function signature
                    sig = inspect.signature(obj)
                    params = {}
                    for param_name, param in sig.parameters.items():
                        if param_name != "self":
                            param_type = (
                                str(param.annotation)
                                if param.annotation != inspect.Parameter.empty
                                else "Any"
                            )
                            params[param_name] = {
                                "type": param_type,
                                "required": param.default == inspect.Parameter.empty,
                                "default": (
                                    param.default
                                    if param.default != inspect.Parameter.empty
                                    else None
                                ),
                            }
                    return {
                        "type": "function",
                        "parameters": params,
                        "description": obj.__doc__ or "No description",
                    }

        # For class-based tools, check for input schema
        if hasattr(tool_class, "args_schema"):
            # LangChain tool with args_schema
            schema = tool_class.args_schema.schema()
            return schema
        elif hasattr(tool_class, "__init__"):
            # Extract from __init__ parameters
            sig = inspect.signature(tool_class.__init__)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name not in ["self", "args", "kwargs"]:
                    param_type = (
                        str(param.annotation)
                        if param.annotation != inspect.Parameter.empty
                        else "Any"
                    )
                    params[param_name] = {
                        "type": param_type,
                        "required": param.default == inspect.Parameter.empty,
                        "default": (
                            param.default
                            if param.default != inspect.Parameter.empty
                            else None
                        ),
                    }
            return {"type": "class", "parameters": params}

        return {"type": "unknown", "message": "Could not extract schema"}

    except Exception as e:
        logger.error(f"Failed to get schema for {tool_module_path}: {e}")
        return {"error": str(e)}


async def invoke_tool(tool_module_path: str, arguments: Dict[str, Any]) -> Any:
    """Invoke a tool with given arguments."""
    try:
        import importlib

        module = importlib.import_module(tool_module_path)

        # Try to find and instantiate the tool
        tool_instance = None

        # First, try to find a tool class
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and (
                name.endswith("Tool") or name.endswith("Toolkit")
            ):
                # Instantiate the tool
                try:
                    tool_instance = obj(**arguments.get("init_args", {}))

                    # If it's a LangChain tool, invoke it
                    if hasattr(tool_instance, "invoke") or hasattr(
                        tool_instance, "run"
                    ):
                        method = (
                            getattr(tool_instance, "invoke", None) or tool_instance.run
                        )
                        result = (
                            await method(**arguments.get("run_args", arguments))
                            if inspect.iscoroutinefunction(method)
                            else method(**arguments.get("run_args", arguments))
                        )
                        return result
                    else:
                        return {"error": "Tool does not have invoke or run method"}
                except Exception as e:
                    logger.error(f"Failed to instantiate tool: {e}")
                    # Try next tool class
                    continue

        # If no class found, try function-based tool
        if not tool_instance:
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    # Call the function directly
                    result = (
                        await obj(**arguments)
                        if inspect.iscoroutinefunction(obj)
                        else obj(**arguments)
                    )
                    return result

        return {"error": "No callable tool found in module"}

    except Exception as e:
        logger.error(f"Failed to invoke tool {tool_module_path}: {e}")
        raise


@router.get("/{tool_name}/schema", response_model=ToolSchema)
async def get_tool_schema_endpoint(tool_name: str) -> ToolSchema:
    """Get the input/output schema for a specific tool.

    Args:
        tool_name: Name of the tool to get schema for

    Returns:
        ToolSchema containing input and output schemas
    """
    try:
        tools = simple_discover_tools()
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        # Get the schema - pass tool name to help identify the right one
        schema = get_tool_schema_for_name(tool.module, tool_name)

        return ToolSchema(
            name=tool.name,
            description=tool.description,
            input_schema=schema,
            output_schema=None,  # Could be extended to extract output schema
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_tool_schema_for_name(
    tool_module_path: str, target_tool_name: str
) -> Dict[str, Any]:
    """Extract input schema for a specific tool by name."""
    try:
        # Try using the enhanced analyzer from haive discovery
        import importlib

        from haive.core.utils.haive_discovery.enhanced_tool_discovery import (
            EnhancedToolAnalyzer,
        )

        module = importlib.import_module(tool_module_path)

        # Try to find the specific tool by name
        tool_obj = None

        # Check for exact name match (function or class)
        for name, obj in inspect.getmembers(module):
            if name.lower() == target_tool_name.lower():
                tool_obj = obj
                break
            elif name.lower() == f"{target_tool_name.lower()}tool":
                tool_obj = obj
                break

        if tool_obj:
            # Use enhanced analyzer if available
            try:
                analyzer = EnhancedToolAnalyzer()
                schema_info = analyzer.analyze_tool_schema(tool_obj)

                # Convert to our format
                if schema_info.get("parameters"):
                    properties = {}
                    required = []

                    for param in schema_info["parameters"]:
                        properties[param["name"]] = {
                            "type": param["type"],
                            "description": param.get("description", ""),
                        }
                        if param.get("default") is not None:
                            properties[param["name"]]["default"] = param["default"]
                        if param.get("required", False):
                            required.append(param["name"])

                    return {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                        "description": schema_info.get("description", ""),
                    }
                else:
                    return schema_info

            except ImportError:
                # Fall back to manual extraction
                pass

            if inspect.isfunction(tool_obj):
                # Function-based tool
                sig = inspect.signature(tool_obj)
                params = {}
                for param_name, param in sig.parameters.items():
                    if param_name != "self":
                        param_type = (
                            str(param.annotation)
                            if param.annotation != inspect.Parameter.empty
                            else "Any"
                        )
                        params[param_name] = {
                            "type": param_type,
                            "required": param.default == inspect.Parameter.empty,
                            "default": (
                                param.default
                                if param.default != inspect.Parameter.empty
                                else None
                            ),
                        }
                return {
                    "type": "function",
                    "parameters": params,
                    "description": tool_obj.__doc__ or "No description",
                }
            elif inspect.isclass(tool_obj):
                # Class-based tool
                if hasattr(tool_obj, "args_schema"):
                    schema = tool_obj.args_schema.schema()
                    return schema
                else:
                    # Extract from __init__ or run method
                    method = getattr(tool_obj, "run", None) or getattr(
                        tool_obj, "__init__", None
                    )
                    if method:
                        sig = inspect.signature(method)
                        params = {}
                        for param_name, param in sig.parameters.items():
                            if param_name not in ["self", "args", "kwargs"]:
                                param_type = (
                                    str(param.annotation)
                                    if param.annotation != inspect.Parameter.empty
                                    else "Any"
                                )
                                params[param_name] = {
                                    "type": param_type,
                                    "required": param.default
                                    == inspect.Parameter.empty,
                                    "default": (
                                        param.default
                                        if param.default != inspect.Parameter.empty
                                        else None
                                    ),
                                }
                        return {"type": "class", "parameters": params}

        # Fallback to original logic
        return get_tool_schema(tool_module_path)

    except Exception as e:
        logger.error(f"Failed to get schema for {target_tool_name}: {e}")
        return {"error": str(e)}


@router.post("/invoke", response_model=ToolInvokeResponse)
async def invoke_tool_endpoint(request: ToolInvokeRequest) -> ToolInvokeResponse:
    """Invoke a tool with the provided arguments.

    Args:
        request: Tool invocation request with tool name and arguments

    Returns:
        ToolInvokeResponse with the result or error
    """
    try:
        tools = simple_discover_tools()
        tool = next((t for t in tools if t.name == request.tool_name), None)

        if not tool:
            return ToolInvokeResponse(
                success=False, error=f"Tool '{request.tool_name}' not found"
            )

        # Invoke the tool
        result = await invoke_tool(tool.module, request.arguments)

        return ToolInvokeResponse(success=True, result=result)

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
        tools = simple_discover_tools()
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        # Try to get more details by importing the module
        details = tool.dict()

        try:
            import importlib

            module = importlib.import_module(tool.module)

            # Add additional details if available
            details["full_description"] = getattr(
                module, "__doc__", "No description available"
            )
            details["author"] = getattr(module, "__author__", "Unknown")
            details["version"] = getattr(module, "__version__", "Unknown")

            # For toolkits, try to get the list of tools
            if tool.type == "toolkit" and hasattr(module, "get_tools"):
                details["available_tools"] = [str(t) for t in module.get_tools()]

        except Exception as e:
            logger.warning(f"Failed to load additional details for {tool_name}: {e}")

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
