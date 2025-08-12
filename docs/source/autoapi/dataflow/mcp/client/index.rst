
:py:mod:`dataflow.mcp.client`
=============================

.. py:module:: dataflow.mcp.client

MCP Client Integration for haive-dataflow.

This module provides integration between MCP servers and the Haive framework
through LangChain MCP adapters and the dataflow registry system.

The client handles:
- Connection management to multiple MCP servers
- Tool loading and registration from MCP servers
- Integration with LangGraph workflows
- Health monitoring and error handling

Classes:
    MCPClient: Main client for MCP server integration
    MCPToolProvider: Provider for MCP tools in the registry
    MCPServerAdapter: Adapter for individual MCP servers


.. autolink-examples:: dataflow.mcp.client
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.mcp.client.MCPClient
   dataflow.mcp.client.MCPServerAdapter
   dataflow.mcp.client.MCPToolProvider


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPClient:

   .. graphviz::
      :align: center

      digraph inheritance_MCPClient {
        node [shape=record];
        "MCPClient" [label="MCPClient"];
      }

.. autoclass:: dataflow.mcp.client.MCPClient
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPServerAdapter:

   .. graphviz::
      :align: center

      digraph inheritance_MCPServerAdapter {
        node [shape=record];
        "MCPServerAdapter" [label="MCPServerAdapter"];
      }

.. autoclass:: dataflow.mcp.client.MCPServerAdapter
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPToolProvider:

   .. graphviz::
      :align: center

      digraph inheritance_MCPToolProvider {
        node [shape=record];
        "MCPToolProvider" [label="MCPToolProvider"];
      }

.. autoclass:: dataflow.mcp.client.MCPToolProvider
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.mcp.client
   :collapse:
   
.. autolink-skip:: next
