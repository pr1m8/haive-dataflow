
:py:mod:`dataflow.api.routes.agent_discovery_routes_enhanced`
=============================================================

.. py:module:: dataflow.api.routes.agent_discovery_routes_enhanced

Fixed Agent Discovery Routes using Haive Core's unified discovery system.

This module provides FastAPI routes for discovering and managing agents using the
unified discovery system from haive-core. It replaces the previous implementation
that had duplicated discovery logic.

Key Features:
    - Uses HaiveComponentDiscovery for consistent agent discovery
    - Supports both v1 (config-based) and v2 (class-based) agents
    - Provides caching for improved performance
    - Rich metadata extraction including schemas and documentation
    - Categorization and filtering capabilities

.. rubric:: Example

```python
from fastapi import FastAPI
from haive.dataflow.api.routes.agent_discovery_routes_fixed import router

app = FastAPI()
app.include_router(router, prefix="/api/v1")

# Endpoints available:
# GET /api/v1/agents - List all agents
# GET /api/v1/agents/search - Search agents
# GET /api/v1/agents/{agent_name} - Get specific agent
# GET /api/v1/agents/stats - Get agent statistics
```

.. note::

   This implementation fixes the circular import issue between component_registry
   and haive_discovery by using the lazy import pattern implemented in haive-core.


.. autolink-examples:: dataflow.api.routes.agent_discovery_routes_enhanced
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.agent_discovery_routes_enhanced.AgentDetailResponse
   dataflow.api.routes.agent_discovery_routes_enhanced.AgentInfo
   dataflow.api.routes.agent_discovery_routes_enhanced.AgentListResponse


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentDetailResponse:

   .. graphviz::
      :align: center

      digraph inheritance_AgentDetailResponse {
        node [shape=record];
        "AgentDetailResponse" [label="AgentDetailResponse"];
        "pydantic.BaseModel" -> "AgentDetailResponse";
      }

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_enhanced.AgentDetailResponse
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_enhanced.AgentInfo
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

.. autopydantic_model:: dataflow.api.routes.agent_discovery_routes_enhanced.AgentListResponse
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

   dataflow.api.routes.agent_discovery_routes_enhanced.categorize_agents
   dataflow.api.routes.agent_discovery_routes_enhanced.component_to_agent_info
   dataflow.api.routes.agent_discovery_routes_enhanced.discover_all_agents
   dataflow.api.routes.agent_discovery_routes_enhanced.extract_agent_metadata
   dataflow.api.routes.agent_discovery_routes_enhanced.get_agent_details
   dataflow.api.routes.agent_discovery_routes_enhanced.get_agent_stats
   dataflow.api.routes.agent_discovery_routes_enhanced.get_discovery_instance
   dataflow.api.routes.agent_discovery_routes_enhanced.list_agents
   dataflow.api.routes.agent_discovery_routes_enhanced.search_agents

.. py:function:: categorize_agents(agents: list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]) -> dict[str, list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]]

   Categorize agents by their type/category.

   :param agents: List of agent components to categorize.

   :returns: Dictionary mapping category names
             to lists of agents in that category.
   :rtype: Dict[str, List[ComponentInfo]]

   .. note::

      Categories are inferred from:
      - Metadata 'category' field
      - Module path components
      - Agent type (v1 vs v2)


   .. autolink-examples:: categorize_agents
      :collapse:

.. py:function:: component_to_agent_info(component: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> AgentInfo

   Convert a ComponentInfo to AgentInfo.

   :param component: ComponentInfo object from discovery.

   :returns: Structured agent information for API response.
   :rtype: AgentInfo


   .. autolink-examples:: component_to_agent_info
      :collapse:

.. py:function:: discover_all_agents(force_refresh: bool = False) -> list[haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo]

   Discover all agents using the unified discovery system.

   :param force_refresh: If True, bypasses cache and rediscovers all agents.

   :returns: List of discovered agent components from both
             haive-agents and haive-core engine directories.
   :rtype: List[ComponentInfo]

   .. note::

      This function discovers agents from multiple locations:
      - haive-agents package (v2 agents)
      - haive-core engine configs (v1 agents)


   .. autolink-examples:: discover_all_agents
      :collapse:

.. py:function:: extract_agent_metadata(agent: haive.dataflow.api.routes.utils.haive_discovery.ComponentInfo) -> dict[str, Any]

   Extract rich metadata from an agent component.

   :param agent: ComponentInfo object representing an agent.

   :returns:

             Enhanced metadata including:
                 - version: Agent version
                 - category: Agent category
                 - capabilities: List of agent capabilities
                 - required_tools: Tools required by the agent
                 - is_v1_agent: Whether this is a v1 (config) agent
                 - is_v2_agent: Whether this is a v2 (class) agent
                 - schema: Input/output schema if available
   :rtype: Dict[str, Any]

   .. note::

      Attempts to extract schema information from both v1 configs
      and v2 agent classes using inspection and attribute access.


   .. autolink-examples:: extract_agent_metadata
      :collapse:

.. py:function:: get_agent_details(agent_name: str) -> AgentDetailResponse
   :async:


   Get detailed information about a specific agent.

   :param agent_name: Name of the agent to retrieve details for.
                      Case-insensitive matching is used.

   :returns:

             Detailed agent information including:
                 - Full metadata and capabilities
                 - Module and file paths
                 - Schema information
                 - Version and category details
   :rtype: AgentDetailResponse

   :raises HTTPException: 404 if agent is not found.

   .. rubric:: Example

   ```
   GET /api/v1/agents/SimpleAgent
   ```


   .. autolink-examples:: get_agent_details
      :collapse:

.. py:function:: get_agent_stats() -> dict[str, Any]
   :async:


   Get statistics about discovered agents.

   :returns:

             Statistics including:
                 - total_agents: Total number of discovered agents
                 - v1_agents: Number of config-based agents
                 - v2_agents: Number of class-based agents
                 - categories: Dictionary of category counts
                 - discovery_sources: List of discovery source paths
                 - discovery_method: Method used for discovery
                 - last_updated: Timestamp of last discovery
   :rtype: Dict[str, Any]

   .. rubric:: Example

   ```
   GET /api/v1/agents/stats

   Response:
   {
       "total_agents": 25,
       "v1_agents": 10,
       "v2_agents": 15,
       "categories": {
           "research": 5,
           "chat": 8,
           "task": 12
       }
   }
   ```


   .. autolink-examples:: get_agent_stats
      :collapse:

.. py:function:: get_discovery_instance() -> haive.dataflow.api.routes.utils.haive_discovery.HaiveComponentDiscovery

   Get or create a cached discovery instance.

   :returns: Cached discovery instance for the haive root.
   :rtype: HaiveComponentDiscovery

   .. note::

      Uses a global singleton pattern to avoid repeated initialization
      of the discovery system which can be expensive.


   .. autolink-examples:: get_discovery_instance
      :collapse:

.. py:function:: list_agents(agent_type: str | None = Query(None, description='Filter by agent type (v1, v2)'), category: str | None = Query(None, description='Filter by category'), force_refresh: bool = Query(False, description='Force refresh discovery cache')) -> AgentListResponse
   :async:


   List all available agents with optional filtering.

   :param agent_type: Optional filter for agent type ('v1' for config-based,
                      'v2' for class-based agents).
   :param category: Optional category filter (e.g., 'research', 'chat').
   :param force_refresh: If True, forces rediscovery of all agents.

   :returns:

             Response containing:
                 - List of discovered agents with metadata
                 - Count statistics (total, v1, v2)
                 - Discovery method information
   :rtype: AgentListResponse

   .. rubric:: Example

   ```
   GET /api/v1/agents?agent_type=v2&category=research
   ```


   .. autolink-examples:: list_agents
      :collapse:

.. py:function:: search_agents(query: str = Query(..., description='Search query'), agent_type: str | None = Query(None, description='Filter by agent type')) -> AgentListResponse
   :async:


   Search agents by name or description.

   :param query: Search string to match against agent names and descriptions.
                 Case-insensitive partial matching is used.
   :param agent_type: Optional filter for agent type ('v1' or 'v2').

   :returns: Filtered list of agents matching the search criteria.
   :rtype: AgentListResponse

   .. rubric:: Example

   ```
   GET /api/v1/agents/search?query=chat&agent_type=v2
   ```


   .. autolink-examples:: search_agents
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.agent_discovery_routes_enhanced
   :collapse:
   
.. autolink-skip:: next
