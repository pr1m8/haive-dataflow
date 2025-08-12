
:py:mod:`dataflow.api.routes.agent_discovery_routes`
====================================================

.. py:module:: dataflow.api.routes.agent_discovery_routes

Agent discovery and management API routes.

This module provides FastAPI routes for discovering and managing both v1 and v2 agents:
- v1 agents: haive.engine.agent.config/agent (config-based agents)
- v2 agents: haive.agents.base.agent (direct agent classes)


.. autolink-examples:: dataflow.api.routes.agent_discovery_routes
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.agent_discovery_routes.AgentCreateRequest
   dataflow.api.routes.agent_discovery_routes.AgentCreateResponse
   dataflow.api.routes.agent_discovery_routes.AgentInfo
   dataflow.api.routes.agent_discovery_routes.AgentListResponse
   dataflow.api.routes.agent_discovery_routes.AgentSchema


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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes.AgentCreateRequest
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes.AgentCreateResponse
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes.AgentInfo
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes.AgentListResponse
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes.AgentSchema
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

   dataflow.api.routes.agent_discovery_routes.discover_all_agents
   dataflow.api.routes.agent_discovery_routes.discover_v1_agents
   dataflow.api.routes.agent_discovery_routes.discover_v2_agents
   dataflow.api.routes.agent_discovery_routes.get_agent_details
   dataflow.api.routes.agent_discovery_routes.get_agent_schema
   dataflow.api.routes.agent_discovery_routes.list_agents
   dataflow.api.routes.agent_discovery_routes.search_agents

.. py:function:: discover_all_agents() -> list[AgentInfo]

   Discover both v1 and v2 agents.


   .. autolink-examples:: discover_all_agents
      :collapse:

.. py:function:: discover_v1_agents() -> list[AgentInfo]

   Discover v1 agents from haive.engine.agent.


   .. autolink-examples:: discover_v1_agents
      :collapse:

.. py:function:: discover_v2_agents() -> list[AgentInfo]

   Discover v2 agents from haive.agents.base.agent.


   .. autolink-examples:: discover_v2_agents
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

.. py:function:: list_agents() -> AgentListResponse
   :async:


   List all available agents (both v1 and v2).

   :returns: AgentListResponse containing list of available agents


   .. autolink-examples:: list_agents
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

.. autolink-examples:: dataflow.api.routes.agent_discovery_routes
   :collapse:
   
.. autolink-skip:: next
