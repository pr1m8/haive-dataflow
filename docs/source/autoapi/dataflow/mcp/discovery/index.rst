
:py:mod:`dataflow.mcp.discovery`
================================

.. py:module:: dataflow.mcp.discovery

MCP Server Discovery for haive-dataflow.

This module provides discovery capabilities for MCP (Model Context Protocol) servers
from various sources and integrates them with the haive-dataflow registry system.

The discovery system can find MCP servers from:
- npm packages (@modelcontextprotocol/*)
- PyPI packages (mcp-*)
- GitHub repositories
- Local configurations
- Existing haive-mcp downloaded servers

Classes:
    MCPDiscovery: Main discovery engine for MCP servers

Functions:
    discover_mcp_servers: Discover and register MCP servers in dataflow registry


.. autolink-examples:: dataflow.mcp.discovery
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.mcp.discovery.MCPDiscovery


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPDiscovery:

   .. graphviz::
      :align: center

      digraph inheritance_MCPDiscovery {
        node [shape=record];
        "MCPDiscovery" [label="MCPDiscovery"];
      }

.. autoclass:: dataflow.mcp.discovery.MCPDiscovery
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.mcp.discovery.discover_mcp_servers

.. py:function:: discover_mcp_servers(registry_system=None) -> list[haive.dataflow.registry.models.RegistryItem]
   :async:


   Discover MCP servers and create registry items.

   This function provides a simple interface for discovering MCP servers
   and creating appropriate registry items for the dataflow system.

   :param registry_system: Optional registry system for registration

   :returns: List of RegistryItem objects for discovered MCP servers

   .. rubric:: Example

   ```python
   from haive.dataflow.mcp.discovery import discover_mcp_servers
   from haive.dataflow import registry_system

   # Discover and register MCP servers
   registry_items = await discover_mcp_servers(registry_system)
   print(f"Discovered {len(registry_items)} MCP servers")
   ```


   .. autolink-examples:: discover_mcp_servers
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.mcp.discovery
   :collapse:
   
.. autolink-skip:: next
