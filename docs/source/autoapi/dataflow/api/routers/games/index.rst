
:py:mod:`dataflow.api.routers.games`
====================================

.. py:module:: dataflow.api.routers.games

Games router for the Haive API.

This module provides API routes for the general games system,
integrating with the haive-games package.


.. autolink-examples:: dataflow.api.routers.games
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.routers.games.create_games_router
   dataflow.api.routers.games.create_games_websocket_router
   dataflow.api.routers.games.get_game_api

.. py:function:: create_games_router(prefix: str = '/games', tags: list[str] | None = None, exclude_games: list[str] | None = None) -> fastapi.APIRouter

   Create a router for the games API.

   :param prefix: URL prefix for the router
   :param tags: OpenAPI tags for the routes
   :param exclude_games: List of games to exclude

   :returns: APIRouter with games endpoints


   .. autolink-examples:: create_games_router
      :collapse:

.. py:function:: create_games_websocket_router(prefix: str = '/ws/games') -> fastapi.APIRouter

   Create WebSocket routes for games.

   :param prefix: URL prefix for WebSocket routes

   :returns: APIRouter with WebSocket endpoints


   .. autolink-examples:: create_games_websocket_router
      :collapse:

.. py:function:: get_game_api()

   Get the game API instance (singleton).


   .. autolink-examples:: get_game_api
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routers.games
   :collapse:
   
.. autolink-skip:: next
