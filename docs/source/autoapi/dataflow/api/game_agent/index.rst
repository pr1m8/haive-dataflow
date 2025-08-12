
:py:mod:`dataflow.api.game_agent`
=================================

.. py:module:: dataflow.api.game_agent


Classes
-------

.. autoapisummary::

   dataflow.api.game_agent.AgentManager
   dataflow.api.game_agent.AgentRequest
   dataflow.api.game_agent.AgentResponseBase
   dataflow.api.game_agent.CheckpointDB
   dataflow.api.game_agent.CheckpointInfo
   dataflow.api.game_agent.GenericAgentAPI


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentManager:

   .. graphviz::
      :align: center

      digraph inheritance_AgentManager {
        node [shape=record];
        "AgentManager" [label="AgentManager"];
      }

.. autoclass:: dataflow.api.game_agent.AgentManager
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentRequest:

   .. graphviz::
      :align: center

      digraph inheritance_AgentRequest {
        node [shape=record];
        "AgentRequest" [label="AgentRequest"];
        "pydantic.BaseModel" -> "AgentRequest";
      }

.. autopydantic_model:: dataflow.api.game_agent.AgentRequest
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

   Inheritance diagram for AgentResponseBase:

   .. graphviz::
      :align: center

      digraph inheritance_AgentResponseBase {
        node [shape=record];
        "AgentResponseBase" [label="AgentResponseBase"];
        "pydantic.BaseModel" -> "AgentResponseBase";
      }

.. autopydantic_model:: dataflow.api.game_agent.AgentResponseBase
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

   Inheritance diagram for CheckpointDB:

   .. graphviz::
      :align: center

      digraph inheritance_CheckpointDB {
        node [shape=record];
        "CheckpointDB" [label="CheckpointDB"];
      }

.. autoclass:: dataflow.api.game_agent.CheckpointDB
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for CheckpointInfo:

   .. graphviz::
      :align: center

      digraph inheritance_CheckpointInfo {
        node [shape=record];
        "CheckpointInfo" [label="CheckpointInfo"];
        "pydantic.BaseModel" -> "CheckpointInfo";
      }

.. autopydantic_model:: dataflow.api.game_agent.CheckpointInfo
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

   Inheritance diagram for GenericAgentAPI:

   .. graphviz::
      :align: center

      digraph inheritance_GenericAgentAPI {
        node [shape=record];
        "GenericAgentAPI" [label="GenericAgentAPI"];
        "Generic[T, S]" -> "GenericAgentAPI";
      }

.. autoclass:: dataflow.api.game_agent.GenericAgentAPI
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.api.game_agent
   :collapse:
   
.. autolink-skip:: next
