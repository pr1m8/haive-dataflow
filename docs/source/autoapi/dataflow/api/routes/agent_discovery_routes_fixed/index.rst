
:py:mod:`dataflow.api.routes.agent_discovery_routes_fixed`
==========================================================

.. py:module:: dataflow.api.routes.agent_discovery_routes_fixed

Agent discovery and management API routes using unified discovery system.

This module provides FastAPI routes for discovering and managing agents
using the haive-core discovery system.


.. autolink-examples:: dataflow.api.routes.agent_discovery_routes_fixed
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.agent_discovery_routes_fixed.AgentCreateRequest
   dataflow.api.routes.agent_discovery_routes_fixed.AgentCreateResponse
   dataflow.api.routes.agent_discovery_routes_fixed.AgentInfo
   dataflow.api.routes.agent_discovery_routes_fixed.AgentListResponse
   dataflow.api.routes.agent_discovery_routes_fixed.AgentSchema


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentCreateRequest:

   .. graphviz::
      :align: center

      digraph inheritance_AgentCreateRequest {
        node [shape=record];
        "AgentCreateRequest" [label="AgentCreateRequest"];
        "pydantic.BaseModel" -> "AgentCreateRequest";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_fixed.AgentCreateRequest
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

   Inheritance diagram for AgentCreateResponse:

   .. graphviz::
      :align: center

      digraph inheritance_AgentCreateResponse {
        node [shape=record];
        "AgentCreateResponse" [label="AgentCreateResponse"];
        "pydantic.BaseModel" -> "AgentCreateResponse";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_fixed.AgentCreateResponse
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

   Inheritance diagram for AgentInfo:

   .. graphviz::
      :align: center

      digraph inheritance_AgentInfo {
        node [shape=record];
        "AgentInfo" [label="AgentInfo"];
        "pydantic.BaseModel" -> "AgentInfo";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_fixed.AgentInfo
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

   Inheritance diagram for AgentListResponse:

   .. graphviz::
      :align: center

      digraph inheritance_AgentListResponse {
        node [shape=record];
        "AgentListResponse" [label="AgentListResponse"];
        "pydantic.BaseModel" -> "AgentListResponse";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_fixed.AgentListResponse
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

   Inheritance diagram for AgentSchema:

   .. graphviz::
      :align: center

      digraph inheritance_AgentSchema {
        node [shape=record];
        "AgentSchema" [label="AgentSchema"];
        "pydantic.BaseModel" -> "AgentSchema";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_fixed.AgentSchema
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

   dataflow.api.routes.agent_discovery_routes_fixed.component_to_agent_info
   dataflow.api.routes.agent_discovery_routes_fixed.discover_all_agents
   dataflow.api.routes.agent_discovery_routes_fixed.get_agent_details
   dataflow.api.routes.agent_discovery_routes_fixed.get_agent_schema
   dataflow.api.routes.agent_discovery_routes_fixed.get_agent_stats
   dataflow.api.routes.agent_discovery_routes_fixed.get_discovery_instance
   dataflow.api.routes.agent_discovery_routes_fixed.list_agents
   dataflow.api.routes.agent_discovery_routes_fixed.refresh_agent_cache
   dataflow.api.routes.agent_discovery_routes_fixed.search_agents

.. py:function:: component_to_agent_info(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> AgentInfo

   Convert a ComponentInfo to AgentInfo.


   .. autolink-examples:: component_to_agent_info
      :collapse:

.. py:function:: discover_all_agents(force_refresh: bool = False) -> list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]

   Discover all agents using the unified discovery system.


   .. autolink-examples:: discover_all_agents
      :collapse:

.. py:function:: get_agent_details(agent_name: str) -> dict[str, Any]
   :async:


   Get detailed information about a specific agent.

   :param agent_name: Name of the agent to get details for

   :returns: Detailed information about the agent


   .. autolink-examples:: get_agent_details
      :collapse:

.. py:function:: get_agent_schema(agent_name: str) -> AgentSchema
   :async:


   Get the configuration/initialization schema for a specific agent.

   :param agent_name: Name of the agent to get schema for

   :returns: AgentSchema containing configuration and method information


   .. autolink-examples:: get_agent_schema
      :collapse:

.. py:function:: get_agent_stats() -> dict[str, Any]
   :async:


   Get summary statistics about discovered agents.

   :returns: Summary statistics


   .. autolink-examples:: get_agent_stats
      :collapse:

.. py:function:: get_discovery_instance() -> haive.dataflow.api.routes.utils.haive_discovery.HaiveComponentDiscovery

   Get or create the discovery instance.


   .. autolink-examples:: get_discovery_instance
      :collapse:

.. py:function:: list_agents(force_refresh: bool = False) -> AgentListResponse
   :async:


   List all available agents.

   :param force_refresh: Force refresh the agent cache

   :returns: AgentListResponse containing list of available agents


   .. autolink-examples:: list_agents
      :collapse:

.. py:function:: refresh_agent_cache() -> dict[str, Any]
   :async:


   Refresh the agent discovery cache.

   :returns: Status and count of discovered agents


   .. autolink-examples:: refresh_agent_cache
      :collapse:

.. py:function:: search_agents(query: str | None = None, agent_type: str | None = None, category: str | None = None) -> AgentListResponse
   :async:


   Search for agents by query, type, or category.

   :param query: Search query to match against agent names and descriptions
   :param agent_type: Filter by agent type ('v1' or 'v2')
   :param category: Filter by category

   :returns: AgentListResponse containing filtered list of agents


   .. autolink-examples:: search_agents
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.agent_discovery_routes_fixed
   :collapse:
   
.. autolink-skip:: next
