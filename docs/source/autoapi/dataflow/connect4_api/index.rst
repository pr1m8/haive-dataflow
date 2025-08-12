
:py:mod:`dataflow.connect4_api`
===============================

.. py:module:: dataflow.connect4_api


Classes
-------

.. autoapisummary::

   dataflow.connect4_api.Connect4API
   dataflow.connect4_api.Connect4MoveRequest
   dataflow.connect4_api.Connect4Request
   dataflow.connect4_api.Connect4Response


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Connect4API:

   .. graphviz::
      :align: center

      digraph inheritance_Connect4API {
        node [shape=record];
        "Connect4API" [label="Connect4API"];
        "haive.dataflow.api.game_agent.GenericAgentAPI[haive_games.connect4.agent.Connect4Agent, haive_games.connect4.config.Connect4AgentConfig]" -> "Connect4API";
      }

.. autoclass:: dataflow.connect4_api.Connect4API
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Connect4MoveRequest:

   .. graphviz::
      :align: center

      digraph inheritance_Connect4MoveRequest {
        node [shape=record];
        "Connect4MoveRequest" [label="Connect4MoveRequest"];
        "pydantic.BaseModel" -> "Connect4MoveRequest";
      }

.. autopydantic_model:: dataflow.connect4_api.Connect4MoveRequest
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

   Inheritance diagram for Connect4Request:

   .. graphviz::
      :align: center

      digraph inheritance_Connect4Request {
        node [shape=record];
        "Connect4Request" [label="Connect4Request"];
        "pydantic.BaseModel" -> "Connect4Request";
      }

.. autopydantic_model:: dataflow.connect4_api.Connect4Request
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

   Inheritance diagram for Connect4Response:

   .. graphviz::
      :align: center

      digraph inheritance_Connect4Response {
        node [shape=record];
        "Connect4Response" [label="Connect4Response"];
        "haive.dataflow.api.game_agent.AgentResponseBase" -> "Connect4Response";
      }

.. autoclass:: dataflow.connect4_api.Connect4Response
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.connect4_api.run

.. py:function:: run()

   Run the Connect4 API server.


   .. autolink-examples:: run
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.connect4_api
   :collapse:
   
.. autolink-skip:: next
