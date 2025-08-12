
:py:mod:`dataflow.api.serve_chess_client`
=========================================

.. py:module:: dataflow.api.serve_chess_client

Simple HTTP server to serve the chess client HTML/JS interface.

This script starts a simple HTTP server to serve the chess client
interface that connects to the WebSocket API.

Usage:
    python serve_chess_client.py [--port PORT]

.. note:: This is for development/testing only and should not be used in production.


.. autolink-examples:: dataflow.api.serve_chess_client
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.serve_chess_client.ChessClientHandler


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ChessClientHandler:

   .. graphviz::
      :align: center

      digraph inheritance_ChessClientHandler {
        node [shape=record];
        "ChessClientHandler" [label="ChessClientHandler"];
        "http.server.SimpleHTTPRequestHandler" -> "ChessClientHandler";
      }

.. autoclass:: dataflow.api.serve_chess_client.ChessClientHandler
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.api.serve_chess_client.get_static_dir
   dataflow.api.serve_chess_client.main
   dataflow.api.serve_chess_client.run_server

.. py:function:: get_static_dir()

   Get the directory containing the static files.


   .. autolink-examples:: get_static_dir
      :collapse:

.. py:function:: main()

   Parse arguments and run the server.


   .. autolink-examples:: main
      :collapse:

.. py:function:: run_server(port=8080)

   Run the HTTP server.


   .. autolink-examples:: run_server
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.serve_chess_client
   :collapse:
   
.. autolink-skip:: next
