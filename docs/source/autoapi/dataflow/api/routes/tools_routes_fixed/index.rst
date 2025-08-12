
:py:mod:`dataflow.api.routes.tools_routes_fixed`
================================================

.. py:module:: dataflow.api.routes.tools_routes_fixed

Tools API routes using the unified discovery system.

This module provides FastAPI routes for discovering and listing all
available tools in the Haive ecosystem using the haive-core discovery
system.


.. autolink-examples:: dataflow.api.routes.tools_routes_fixed
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.tools_routes_fixed.ToolInfo
   dataflow.api.routes.tools_routes_fixed.ToolInvokeRequest
   dataflow.api.routes.tools_routes_fixed.ToolInvokeResponse
   dataflow.api.routes.tools_routes_fixed.ToolSchema
   dataflow.api.routes.tools_routes_fixed.ToolsListResponse


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

.. autopydantic_model:: dataflow.api.routes.tools_routes_fixed.ToolInfo
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

   Inheritance diagram for ToolInvokeRequest:

   .. graphviz::
      :align: center

      digraph inheritance_ToolInvokeRequest {
        node [shape=record];
        "ToolInvokeRequest" [label="ToolInvokeRequest"];
        "pydantic.BaseModel" -> "ToolInvokeRequest";
      }

.. autopydantic_model:: dataflow.api.routes.tools_routes_fixed.ToolInvokeRequest
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

   Inheritance diagram for ToolInvokeResponse:

   .. graphviz::
      :align: center

      digraph inheritance_ToolInvokeResponse {
        node [shape=record];
        "ToolInvokeResponse" [label="ToolInvokeResponse"];
        "pydantic.BaseModel" -> "ToolInvokeResponse";
      }

.. autopydantic_model:: dataflow.api.routes.tools_routes_fixed.ToolInvokeResponse
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

.. autopydantic_model:: dataflow.api.routes.tools_routes_fixed.ToolSchema
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

.. autopydantic_model:: dataflow.api.routes.tools_routes_fixed.ToolsListResponse
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

   dataflow.api.routes.tools_routes_fixed.component_to_tool_info
   dataflow.api.routes.tools_routes_fixed.discover_all_tools
   dataflow.api.routes.tools_routes_fixed.discover_tools_fallback
   dataflow.api.routes.tools_routes_fixed.get_discovery_instance
   dataflow.api.routes.tools_routes_fixed.get_tool_categories
   dataflow.api.routes.tools_routes_fixed.get_tool_details
   dataflow.api.routes.tools_routes_fixed.get_tool_schema_endpoint
   dataflow.api.routes.tools_routes_fixed.get_tool_stats
   dataflow.api.routes.tools_routes_fixed.invoke_tool_endpoint
   dataflow.api.routes.tools_routes_fixed.list_tools
   dataflow.api.routes.tools_routes_fixed.refresh_tool_cache
   dataflow.api.routes.tools_routes_fixed.search_tools

.. py:function:: component_to_tool_info(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> ToolInfo

   Convert a ComponentInfo to ToolInfo.


   .. autolink-examples:: component_to_tool_info
      :collapse:

.. py:function:: discover_all_tools(force_refresh: bool = False) -> list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]

   Discover all tools using the unified discovery system.


   .. autolink-examples:: discover_all_tools
      :collapse:

.. py:function:: discover_tools_fallback() -> list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]

   Fallback tool discovery if the main discovery fails.


   .. autolink-examples:: discover_tools_fallback
      :collapse:

.. py:function:: get_discovery_instance() -> haive.dataflow.api.routes.utils.haive_discovery.HaiveComponentDiscovery

   Get or create the discovery instance.


   .. autolink-examples:: get_discovery_instance
      :collapse:

.. py:function:: get_tool_categories() -> dict[str, list[str]]
   :async:


   Get all available tool categories and their tools.

   :returns: Dictionary mapping categories to tool names


   .. autolink-examples:: get_tool_categories
      :collapse:

.. py:function:: get_tool_details(tool_name: str) -> dict[str, Any]
   :async:


   Get detailed information about a specific tool.

   :param tool_name: Name of the tool to get details for

   :returns: Detailed information about the tool


   .. autolink-examples:: get_tool_details
      :collapse:

.. py:function:: get_tool_schema_endpoint(tool_name: str) -> ToolSchema
   :async:


   Get the input/output schema for a specific tool.

   :param tool_name: Name of the tool to get schema for

   :returns: ToolSchema containing input and output schemas


   .. autolink-examples:: get_tool_schema_endpoint
      :collapse:

.. py:function:: get_tool_stats() -> dict[str, Any]
   :async:


   Get summary statistics about discovered tools.

   :returns: Summary statistics


   .. autolink-examples:: get_tool_stats
      :collapse:

.. py:function:: invoke_tool_endpoint(request: ToolInvokeRequest) -> ToolInvokeResponse
   :async:


   Invoke a tool with the provided arguments.

   :param request: Tool invocation request with tool name and arguments

   :returns: ToolInvokeResponse with the result or error


   .. autolink-examples:: invoke_tool_endpoint
      :collapse:

.. py:function:: list_tools(force_refresh: bool = False) -> ToolsListResponse
   :async:


   List all available tools.

   :param force_refresh: Force refresh the tool cache

   :returns: ToolsListResponse containing list of available tools and total count


   .. autolink-examples:: list_tools
      :collapse:

.. py:function:: refresh_tool_cache() -> dict[str, Any]
   :async:


   Refresh the tool discovery cache.

   :returns: Status and count of discovered tools


   .. autolink-examples:: refresh_tool_cache
      :collapse:

.. py:function:: search_tools(query: str | None = None, category: str | None = None, tool_type: str | None = None) -> ToolsListResponse
   :async:


   Search for tools by query, category, or type.

   :param query: Search query to match against tool names and descriptions
   :param category: Filter by category (e.g., 'search', 'development', 'database')
   :param tool_type: Filter by type ('tool' or 'toolkit')

   :returns: ToolsListResponse containing filtered list of tools


   .. autolink-examples:: search_tools
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.tools_routes_fixed
   :collapse:
   
.. autolink-skip:: next
