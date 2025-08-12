
:py:mod:`dataflow.registry.discovery`
=====================================

.. py:module:: dataflow.registry.discovery

Discovery mechanisms for the Haive Registry System.

This module provides functionality for automatically discovering and registering
various components in the Haive ecosystem, such as agents, tools, engines, and games.
It implements introspection mechanisms to find components based on naming conventions,
class inheritance, and module structure.

The discovery process works by:
1. Searching for modules in specified paths
2. Inspecting classes in those modules
3. Determining if they match criteria for specific component types
4. Registering matching components in the registry system

Functions:
    discover_modules: Find all Python modules under a base path
    discover_all: Discover all component types (agents, tools, engines, games)
    discover_agents: Discover and register agent components
    discover_tools: Discover and register tool components
    discover_toolkits: Discover and register toolkit components
    discover_engines: Discover and register engine components
    discover_games: Discover and register game components

.. rubric:: Example

Discovering components:

>>> from haive.dataflow.registry.discovery import discover_agents, discover_tools
>>>
>>> # Discover all agents in the system
>>> discovered_agents = discover_agents()
>>> print(f"Discovered {len(discovered_agents)} agents")
>>>
>>> # Discover tools and toolkits
>>> discovered_tools = discover_tools()
>>> discovered_toolkits = discover_toolkits()
>>> print(f"Discovered {len(discovered_tools)} tools and {len(discovered_toolkits)} toolkits")


.. autolink-examples:: dataflow.registry.discovery
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.registry.discovery.discover_agents
   dataflow.registry.discovery.discover_all
   dataflow.registry.discovery.discover_engines
   dataflow.registry.discovery.discover_games
   dataflow.registry.discovery.discover_mcp_servers
   dataflow.registry.discovery.discover_modules
   dataflow.registry.discovery.discover_toolkits
   dataflow.registry.discovery.discover_tools
   dataflow.registry.discovery.is_pydantic_model

.. py:function:: discover_agents(module_paths: list[str] | None = None) -> list[str]

   Discover and register agents.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered agent IDs


   .. autolink-examples:: discover_agents
      :collapse:

.. py:function:: discover_all() -> dict[haive.dataflow.registry.models.EntityType, list[str]]

   Discover and register all entity types.

   :returns: Dictionary mapping entity types to lists of registered IDs


   .. autolink-examples:: discover_all
      :collapse:

.. py:function:: discover_engines(module_paths: list[str] | None = None) -> list[str]

   Discover and register engines.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered engine IDs


   .. autolink-examples:: discover_engines
      :collapse:

.. py:function:: discover_games(module_paths: list[str] | None = None) -> list[str]

   Discover and register games.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered game IDs


   .. autolink-examples:: discover_games
      :collapse:

.. py:function:: discover_mcp_servers() -> list[str]

   Discover and register MCP (Model Context Protocol) servers.

   This function discovers MCP servers from various sources including:
   - npm packages (@modelcontextprotocol/*)
   - PyPI packages (mcp-*)
   - Local configurations
   - Existing haive-mcp downloaded servers

   :returns: List of registry IDs for registered MCP servers

   .. rubric:: Example

   >>> mcp_servers = discover_mcp_servers()
   >>> print(f"Discovered {len(mcp_servers)} MCP servers")


   .. autolink-examples:: discover_mcp_servers
      :collapse:

.. py:function:: discover_modules(base_path: str) -> list[str]

   Discover all Python modules under a base path.

   This function recursively explores a package to find all Python modules.
   It handles both regular modules and packages, traversing the entire module
   hierarchy to discover all available modules.

   :param base_path: Base module path to start discovery from (e.g., "haive.agents")

   :returns: List of fully qualified module paths discovered
   :rtype: List[str]

   .. rubric:: Example

   >>> modules = discover_modules("haive.tools")
   >>> print(f"Discovered modules: {modules}")
   Discovered modules: ['haive.tools.text', 'haive.tools.image', ...]


   .. autolink-examples:: discover_modules
      :collapse:

.. py:function:: discover_toolkits(module_paths: list[str] | None = None) -> list[str]

   Discover and register toolkits.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered toolkit IDs


   .. autolink-examples:: discover_toolkits
      :collapse:

.. py:function:: discover_tools(module_paths: list[str] | None = None) -> list[str]

   Discover and register tools.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered tool IDs


   .. autolink-examples:: discover_tools
      :collapse:

.. py:function:: is_pydantic_model(obj: Any) -> bool

   Check if an object is a Pydantic model.

   :param obj: Object to check

   :returns: True if it's a Pydantic model, False otherwise


   .. autolink-examples:: is_pydantic_model
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.discovery
   :collapse:
   
.. autolink-skip:: next
