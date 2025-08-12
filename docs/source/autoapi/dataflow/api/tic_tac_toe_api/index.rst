
:py:mod:`dataflow.api.tic_tac_toe_api`
======================================

.. py:module:: dataflow.api.tic_tac_toe_api


Classes
-------

.. autoapisummary::

   dataflow.api.tic_tac_toe_api.TicTacToeAPI
   dataflow.api.tic_tac_toe_api.TicTacToeMoveRequest
   dataflow.api.tic_tac_toe_api.TicTacToeRequest
   dataflow.api.tic_tac_toe_api.TicTacToeResponse


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for TicTacToeAPI:

   .. graphviz::
      :align: center

      digraph inheritance_TicTacToeAPI {
        node [shape=record];
        "TicTacToeAPI" [label="TicTacToeAPI"];
        "haive.dataflow.api.api.game_agent.GenericAgentAPI[haive_games.tic_tac_toe.agent.TicTacToeAgent, haive_games.tic_tac_toe.config.TicTacToeConfig]" -> "TicTacToeAPI";
      }

.. autoclass:: dataflow.api.tic_tac_toe_api.TicTacToeAPI
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for TicTacToeMoveRequest:

   .. graphviz::
      :align: center

      digraph inheritance_TicTacToeMoveRequest {
        node [shape=record];
        "TicTacToeMoveRequest" [label="TicTacToeMoveRequest"];
        "pydantic.BaseModel" -> "TicTacToeMoveRequest";
      }

.. autopydantic_model:: dataflow.api.tic_tac_toe_api.TicTacToeMoveRequest
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

   Inheritance diagram for TicTacToeRequest:

   .. graphviz::
      :align: center

      digraph inheritance_TicTacToeRequest {
        node [shape=record];
        "TicTacToeRequest" [label="TicTacToeRequest"];
        "pydantic.BaseModel" -> "TicTacToeRequest";
      }

.. autopydantic_model:: dataflow.api.tic_tac_toe_api.TicTacToeRequest
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

   Inheritance diagram for TicTacToeResponse:

   .. graphviz::
      :align: center

      digraph inheritance_TicTacToeResponse {
        node [shape=record];
        "TicTacToeResponse" [label="TicTacToeResponse"];
        "haive.dataflow.api.api.game_agent.AgentResponseBase" -> "TicTacToeResponse";
      }

.. autoclass:: dataflow.api.tic_tac_toe_api.TicTacToeResponse
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.api.tic_tac_toe_api.run

.. py:function:: run()

   Run the Tic Tac Toe API server.


   .. autolink-examples:: run
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.tic_tac_toe_api
   :collapse:
   
.. autolink-skip:: next
