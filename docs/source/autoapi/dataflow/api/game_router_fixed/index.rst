
:py:mod:`dataflow.api.game_router_fixed`
========================================

.. py:module:: dataflow.api.game_router_fixed

Game API router for Haive games using the discovery system.

This module discovers and loads game agents from haive-games package
using the centralized discovery system, creating routes for each
available game. It provides WebSocket endpoints for streaming game state
and interacting with game agents.


.. autolink-examples:: dataflow.api.game_router_fixed
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.game_router_fixed.create_game_instance
   dataflow.api.game_router_fixed.create_game_router
   dataflow.api.game_router_fixed.create_game_router_app
   dataflow.api.game_router_fixed.discover_game_agents
   dataflow.api.game_router_fixed.get_game_client_html
   dataflow.api.game_router_fixed.get_game_instance
   dataflow.api.game_router_fixed.get_index_html
   dataflow.api.game_router_fixed.get_router
   dataflow.api.game_router_fixed.main

.. py:function:: create_game_instance(game_type: str, game_id: str) -> dict[str, Any]

   Create or get a game instance.


   .. autolink-examples:: create_game_instance
      :collapse:

.. py:function:: create_game_router(game_type: str) -> fastapi.APIRouter

   Create a router for a specific game type.


   .. autolink-examples:: create_game_router
      :collapse:

.. py:function:: create_game_router_app()

   Create a standalone FastAPI app for game routes.


   .. autolink-examples:: create_game_router_app
      :collapse:

.. py:function:: discover_game_agents()

   Discover game agents using the unified discovery system.


   .. autolink-examples:: discover_game_agents
      :collapse:

.. py:function:: get_game_client_html(game_type: str)

   Generate HTML for a specific game client.


   .. autolink-examples:: get_game_client_html
      :collapse:

.. py:function:: get_game_instance(game_type: str, game_id: str) -> dict[str, Any]

   Get an existing game instance.


   .. autolink-examples:: get_game_instance
      :collapse:

.. py:function:: get_index_html()

   Generate HTML for the index page with links to all games.


   .. autolink-examples:: get_index_html
      :collapse:

.. py:function:: get_router()

   Get a router with all game routes configured.


   .. autolink-examples:: get_router
      :collapse:

.. py:function:: main()

   Run the API server as standalone.


   .. autolink-examples:: main
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.game_router_fixed
   :collapse:
   
.. autolink-skip:: next
