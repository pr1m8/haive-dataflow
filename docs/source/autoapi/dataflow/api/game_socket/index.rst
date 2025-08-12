
:py:mod:`dataflow.api.game_socket`
==================================

.. py:module:: dataflow.api.game_socket

WebSocket server for game state streaming with Supabase integration.

This module provides a general-purpose WebSocket server that can stream game state
for any agent-based game in the Haive framework. It supports:
    - Real-time state updates
    - Supabase persistence integration with RLS
    - Player move submissions
    - AI move requests
    - Multiple game types
    - Authentication and user management

The WebSocket server can be integrated with any game agent implementation
that follows the standard Haive agent interface.


.. autolink-examples:: dataflow.api.game_socket
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.game_socket.GameSocketFactory
   dataflow.api.game_socket.GameSocketServer


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameSocketFactory:

   .. graphviz::
      :align: center

      digraph inheritance_GameSocketFactory {
        node [shape=record];
        "GameSocketFactory" [label="GameSocketFactory"];
      }

.. autoclass:: dataflow.api.game_socket.GameSocketFactory
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameSocketServer:

   .. graphviz::
      :align: center

      digraph inheritance_GameSocketServer {
        node [shape=record];
        "GameSocketServer" [label="GameSocketServer"];
      }

.. autoclass:: dataflow.api.game_socket.GameSocketServer
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.api.game_socket
   :collapse:
   
.. autolink-skip:: next
