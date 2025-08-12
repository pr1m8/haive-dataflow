
:py:mod:`dataflow.api.integrate_games`
======================================

.. py:module:: dataflow.api.integrate_games

Integration module for adding game routes to the main Haive API.

This module provides functions to add game WebSocket endpoints and routes
to an existing FastAPI application. It integrates with the game_router module
to discover and register game agents dynamically.

Usage:
    ```python
    from haive.dataflow.api.app import app
    from haive.dataflow.api.integrate_games import add_game_routes

    # Add game routes to the main app
    add_game_routes(app)
    ```


.. autolink-examples:: dataflow.api.integrate_games
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.integrate_games.add_game_routes
   dataflow.api.integrate_games.configure_import_paths

.. py:function:: add_game_routes(app: fastapi.FastAPI, prefix: str = '/games')

   Add game routes to the main API.

   This function discovers game agents and adds routes for each game type
   to the provided FastAPI application. It creates both REST endpoints and
   WebSocket endpoints for real-time game state streaming.

   :param app: The FastAPI application to add routes to
   :param prefix: The URL prefix for game routes (default: "/games")

   :returns: The updated FastAPI application


   .. autolink-examples:: add_game_routes
      :collapse:

.. py:function:: configure_import_paths()

   Configure import paths for game_router module.


   .. autolink-examples:: configure_import_paths
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.integrate_games
   :collapse:
   
.. autolink-skip:: next
