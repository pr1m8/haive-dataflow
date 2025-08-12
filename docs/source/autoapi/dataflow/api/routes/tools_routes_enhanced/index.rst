
:py:mod:`dataflow.api.routes.tools_routes_enhanced`
===================================================

.. py:module:: dataflow.api.routes.tools_routes_enhanced

Enhanced Tools Discovery API Routes using Haive Core's unified discovery
system.

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

.. rubric:: Example

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

.. note::

   This implementation uses the fixed circular import pattern from haive-core
   to properly integrate with the discovery system.


.. autolink-examples:: dataflow.api.routes.tools_routes_enhanced
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.tools_routes_enhanced.ToolInfo
   dataflow.api.routes.tools_routes_enhanced.ToolSchema
   dataflow.api.routes.tools_routes_enhanced.ToolsListResponse


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ToolInfo:

   .. graphviz::
      :align: center

      digraph inheritance_ToolInfo {
        node [shape=record];
        "ToolInfo" [label="ToolInfo"];
        "pydantic.BaseModel" -> "ToolInfo";
      }

.. autopydantic_model:: dataflow.api.routes.tools_routes_enhanced.ToolInfo
   :members:
   :undoc-members:
   :show-inheritance:
   :model-show-field-summary:
   :model-show-config-summary:
   :model-show-validator-members:
   :model-show-validator-summary:
   :model-show-json:
   :field-list-validators:
   :field-show-constraints:





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ToolSchema:

   .. graphviz::
      :align: center

      digraph inheritance_ToolSchema {
        node [shape=record];
        "ToolSchema" [label="ToolSchema"];
        "pydantic.BaseModel" -> "ToolSchema";
      }

.. autopydantic_model:: dataflow.api.routes.tools_routes_enhanced.ToolSchema
   :members:
   :undoc-members:
   :show-inheritance:
   :model-show-field-summary:
   :model-show-config-summary:
   :model-show-validator-members:
   :model-show-validator-summary:
   :model-show-json:
   :field-list-validators:
   :field-show-constraints:





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ToolsListResponse:

   .. graphviz::
      :align: center

      digraph inheritance_ToolsListResponse {
        node [shape=record];
        "ToolsListResponse" [label="ToolsListResponse"];
        "pydantic.BaseModel" -> "ToolsListResponse";
      }

.. autopydantic_model:: dataflow.api.routes.tools_routes_enhanced.ToolsListResponse
   :members:
   :undoc-members:
   :show-inheritance:
   :model-show-field-summary:
   :model-show-config-summary:
   :model-show-validator-members:
   :model-show-validator-summary:
   :model-show-json:
   :field-list-validators:
   :field-show-constraints:



Functions
---------

.. autoapisummary::

   dataflow.api.routes.tools_routes_enhanced.component_to_tool_info
   dataflow.api.routes.tools_routes_enhanced.discover_all_tools
   dataflow.api.routes.tools_routes_enhanced.extract_tool_schema
   dataflow.api.routes.tools_routes_enhanced.get_tool_categories
   dataflow.api.routes.tools_routes_enhanced.get_tool_schema_endpoint
   dataflow.api.routes.tools_routes_enhanced.get_tool_stats
   dataflow.api.routes.tools_routes_enhanced.infer_tool_category
   dataflow.api.routes.tools_routes_enhanced.list_tools
   dataflow.api.routes.tools_routes_enhanced.search_tools

.. py:function:: component_to_tool_info(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> ToolInfo

   Convert a ComponentInfo to ToolInfo.

   :param component: ComponentInfo object from discovery.

   :returns: Structured tool information for API response.
   :rtype: ToolInfo


   .. autolink-examples:: component_to_tool_info
      :collapse:

.. py:function:: discover_all_tools(force_refresh: bool = False) -> list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]

   Discover all tools using the unified discovery system.

   :param force_refresh: If True, bypasses cache and rediscovers all tools.

   :returns: List of discovered tool components including
             both individual tools and toolkits.
   :rtype: List[ComponentInfo]

   .. note::

      Uses haive-core's discover_tools_with_schemas for comprehensive
      discovery with schema extraction.


   .. autolink-examples:: discover_all_tools
      :collapse:

.. py:function:: extract_tool_schema(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> dict[str, Any] | None

   Extract schema information from a tool component.

   :param component: ComponentInfo object representing a tool.

   :returns: Extracted schema or None if not available.
   :rtype: Optional[Dict[str, Any]]

   .. note::

      Attempts multiple strategies to extract schema:
      1. From metadata 'schema' field
      2. From LangChain tool args_schema
      3. From custom get_input_schema method
      4. From Pydantic model if available


   .. autolink-examples:: extract_tool_schema
      :collapse:

.. py:function:: get_tool_categories() -> dict[str, list[str]]
   :async:


   Get all available tool categories and their tools.

   :returns: Dictionary mapping category names to
             sorted lists of tool names in each category.
   :rtype: Dict[str, List[str]]

   .. rubric:: Example

   ```
   GET /api/v1/tools/categories

   Response:
   {
       "search": ["GoogleSearchTool", "BingSearchTool"],
       "database": ["SQLDatabaseToolkit", "MongoDBToolkit"],
       "development": ["GithubToolkit", "GitLabToolkit"]
   }
   ```


   .. autolink-examples:: get_tool_categories
      :collapse:

.. py:function:: get_tool_schema_endpoint(tool_name: str) -> ToolSchema
   :async:


   Get the input/output schema for a specific tool.

   :param tool_name: Name of the tool to get schema for.
                     Case-sensitive exact matching is used.

   :returns:

             Schema information including:
                 - Input parameter schema (JSON Schema format)
                 - Output schema if available
                 - Usage examples if available
   :rtype: ToolSchema

   :raises HTTPException: 404 if tool is not found.

   .. rubric:: Example

   ```
   GET /api/v1/tools/GoogleSearchTool/schema
   ```


   .. autolink-examples:: get_tool_schema_endpoint
      :collapse:

.. py:function:: get_tool_stats() -> dict[str, Any]
   :async:


   Get statistics about discovered tools.

   :returns:

             Statistics including:
                 - total_tools: Total number of tools and toolkits
                 - individual_tools: Number of individual tools
                 - toolkits: Number of toolkits
                 - categories: Count by category
                 - with_schema: Number of tools with schemas
                 - discovery_method: Method used
                 - last_updated: Cache timestamp
   :rtype: Dict[str, Any]

   .. rubric:: Example

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


   .. autolink-examples:: get_tool_stats
      :collapse:

.. py:function:: infer_tool_category(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> str

   Infer tool category from component information.

   :param component: ComponentInfo object representing a tool.

   :returns: Inferred category name.
   :rtype: str

   .. note::

      Categories are inferred from:
      1. Metadata 'category' field
      2. Module path keywords
      3. Tool name patterns


   .. autolink-examples:: infer_tool_category
      :collapse:

.. py:function:: list_tools(tool_type: str | None = Query(None, description='Filter by type (tool, toolkit)'), category: str | None = Query(None, description='Filter by category'), force_refresh: bool = Query(False, description='Force refresh discovery cache')) -> ToolsListResponse
   :async:


   List all available tools with optional filtering.

   :param tool_type: Optional filter for tool type ('tool' or 'toolkit').
   :param category: Optional category filter (e.g., 'search', 'database').
   :param force_refresh: If True, forces rediscovery of all tools.

   :returns:

             Response containing:
                 - List of discovered tools with metadata
                 - Count statistics
                 - Discovery method information
   :rtype: ToolsListResponse

   .. rubric:: Example

   ```
   GET /api/v1/tools?tool_type=toolkit&category=search
   ```


   .. autolink-examples:: list_tools
      :collapse:

.. py:function:: search_tools(query: str = Query(..., description='Search query'), tool_type: str | None = Query(None, description='Filter by type'), category: str | None = Query(None, description='Filter by category')) -> ToolsListResponse
   :async:


   Search tools by name, description, or module path.

   :param query: Search string to match against tool attributes.
                 Case-insensitive partial matching is used.
   :param tool_type: Optional filter for tool type.
   :param category: Optional category filter.

   :returns: Filtered list of tools matching the search criteria.
   :rtype: ToolsListResponse

   .. rubric:: Example

   ```
   GET /api/v1/tools/search?query=google&tool_type=toolkit
   ```


   .. autolink-examples:: search_tools
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.tools_routes_enhanced
   :collapse:
   
.. autolink-skip:: next
