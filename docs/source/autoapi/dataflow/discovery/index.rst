
:py:mod:`dataflow.discovery`
============================

.. py:module:: dataflow.discovery

Discovery mechanisms for the Haive Registry System.

This module provides functionality for discovering and registering
various components in the Haive ecosystem, such as agents, tools,
engines, etc.


.. autolink-examples:: dataflow.discovery
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.discovery.discover_agents
   dataflow.discovery.discover_all
   dataflow.discovery.discover_engines
   dataflow.discovery.discover_games
   dataflow.discovery.discover_modules
   dataflow.discovery.discover_toolkits
   dataflow.discovery.discover_tools
   dataflow.discovery.is_pydantic_model

.. py:function:: discover_agents(module_paths: list[str] | None = None) -> list[str]

   Discover and register agents.

   :param module_paths: Optional list of module paths to search

   :returns: List of registered agent IDs


   .. autolink-examples:: discover_agents
      :collapse:

.. py:function:: discover_all() -> dict[haive.dataflow.models.EntityType, list[str]]

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

.. py:function:: discover_modules(base_path: str) -> list[str]

   Discover all modules under a base path.

   :param base_path: Base module path

   :returns: List of discovered module paths


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

.. autolink-examples:: dataflow.discovery
   :collapse:
   
.. autolink-skip:: next
