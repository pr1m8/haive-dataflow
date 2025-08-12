
:py:mod:`dataflow.api.routes.tools_routes`
==========================================

.. py:module:: dataflow.api.routes.tools_routes

Tools API routes for discovering and listing available tools.

This module provides FastAPI routes for discovering and listing all
available tools in the Haive ecosystem. It scans the haive-tools package
and returns information about available tools and toolkits.


.. autolink-examples:: dataflow.api.routes.tools_routes
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.tools_routes.ToolInfo
   dataflow.api.routes.tools_routes.ToolInvokeRequest
   dataflow.api.routes.tools_routes.ToolInvokeResponse
   dataflow.api.routes.tools_routes.ToolSchema
   dataflow.api.routes.tools_routes.ToolsListResponse


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

.. autopydantic_model:: dataflow.api.routes.tools_routes.ToolInfo
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

.. autopydantic_model:: dataflow.api.routes.tools_routes.ToolInvokeRequest
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

.. autopydantic_model:: dataflow.api.routes.tools_routes.ToolInvokeResponse
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

.. autopydantic_model:: dataflow.api.routes.tools_routes.ToolSchema
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

.. autopydantic_model:: dataflow.api.routes.tools_routes.ToolsListResponse
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

   dataflow.api.routes.tools_routes.discover_tools
   dataflow.api.routes.tools_routes.get_tool_details
   dataflow.api.routes.tools_routes.get_tool_schema
   dataflow.api.routes.tools_routes.get_tool_schema_endpoint
   dataflow.api.routes.tools_routes.get_tool_schema_for_name
   dataflow.api.routes.tools_routes.invoke_tool
   dataflow.api.routes.tools_routes.invoke_tool_endpoint
   dataflow.api.routes.tools_routes.list_tools
   dataflow.api.routes.tools_routes.search_tools
   dataflow.api.routes.tools_routes.simple_discover_tools

.. py:function:: discover_tools() -> list[ToolInfo]

   Discover all available tools from haive-tools package.


   .. autolink-examples:: discover_tools
      :collapse:

.. py:function:: get_tool_details(tool_name: str) -> dict[str, Any]
   :async:


   Get detailed information about a specific tool.

   :param tool_name: Name of the tool to get details for

   :returns: Detailed information about the tool


   .. autolink-examples:: get_tool_details
      :collapse:

.. py:function:: get_tool_schema(tool_module_path: str) -> dict[str, Any]

   Extract input schema from a tool module.


   .. autolink-examples:: get_tool_schema
      :collapse:

.. py:function:: get_tool_schema_endpoint(tool_name: str) -> ToolSchema
   :async:


   Get the input/output schema for a specific tool.

   :param tool_name: Name of the tool to get schema for

   :returns: ToolSchema containing input and output schemas


   .. autolink-examples:: get_tool_schema_endpoint
      :collapse:

.. py:function:: get_tool_schema_for_name(tool_module_path: str, target_tool_name: str) -> dict[str, Any]

   Extract input schema for a specific tool by name.


   .. autolink-examples:: get_tool_schema_for_name
      :collapse:

.. py:function:: invoke_tool(tool_module_path: str, arguments: dict[str, Any]) -> Any
   :async:


   Invoke a tool with given arguments.


   .. autolink-examples:: invoke_tool
      :collapse:

.. py:function:: invoke_tool_endpoint(request: ToolInvokeRequest) -> ToolInvokeResponse
   :async:


   Invoke a tool with the provided arguments.

   :param request: Tool invocation request with tool name and arguments

   :returns: ToolInvokeResponse with the result or error


   .. autolink-examples:: invoke_tool_endpoint
      :collapse:

.. py:function:: list_tools() -> ToolsListResponse
   :async:


   List all available tools.

   :returns: ToolsListResponse containing list of available tools and total count


   .. autolink-examples:: list_tools
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

.. py:function:: simple_discover_tools() -> list[ToolInfo]

   Simple tool discovery that always works.


   .. autolink-examples:: simple_discover_tools
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.tools_routes
   :collapse:
   
.. autolink-skip:: next
