
:py:mod:`dataflow.api.game_api`
===============================

.. py:module:: dataflow.api.game_api

Generic game API with WebSocket support and Supabase integration.

This module provides a FastAPI implementation for any agent-based game
in the Haive framework, with support for:
    - REST endpoints for game state management
    - WebSocket connections for real-time updates
    - Supabase persistence for cloud storage
    - Row-Level Security (RLS) for data isolation
    - Multi-game support through factory patterns

The API supports any game that follows the standard Haive agent pattern,
allowing for easy integration of new games.


.. autolink-examples:: dataflow.api.game_api
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.game_api.GameAPI
   dataflow.api.game_api.GameAPIFactory
   dataflow.api.game_api.GameRequest
   dataflow.api.game_api.GameResponseBase


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameAPI:

   .. graphviz::
      :align: center

      digraph inheritance_GameAPI {
        node [shape=record];
        "GameAPI" [label="GameAPI"];
      }

.. autoclass:: dataflow.api.game_api.GameAPI
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameAPIFactory:

   .. graphviz::
      :align: center

      digraph inheritance_GameAPIFactory {
        node [shape=record];
        "GameAPIFactory" [label="GameAPIFactory"];
      }

.. autoclass:: dataflow.api.game_api.GameAPIFactory
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameRequest:

   .. graphviz::
      :align: center

      digraph inheritance_GameRequest {
        node [shape=record];
        "GameRequest" [label="GameRequest"];
        "pydantic.BaseModel" -> "GameRequest";
      }

.. autopydantic_model:: dataflow.api.game_api.GameRequest
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

   Inheritance diagram for GameResponseBase:

   .. graphviz::
      :align: center

      digraph inheritance_GameResponseBase {
        node [shape=record];
        "GameResponseBase" [label="GameResponseBase"];
        "pydantic.BaseModel" -> "GameResponseBase";
      }

.. autopydantic_model:: dataflow.api.game_api.GameResponseBase
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





.. rubric:: Related Links

.. autolink-examples:: dataflow.api.game_api
   :collapse:
   
.. autolink-skip:: next
