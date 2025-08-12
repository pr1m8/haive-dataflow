
:py:mod:`dataflow.api.run_chess_api`
====================================

.. py:module:: dataflow.api.run_chess_api

Chess API demonstration script.

This script launches a standalone API server for the chess game
with WebSocket support and Supabase integration.

Usage:
    python run_chess_api.py [--port PORT]

Environment variables:
    SUPABASE_URL: The URL of your Supabase instance
    SUPABASE_SERVICE_KEY: Service role API key
    SUPABASE_ANON_KEY: Anonymous API key


.. autolink-examples:: dataflow.api.run_chess_api
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.run_chess_api.main
   dataflow.api.run_chess_api.run_chess_api
   dataflow.api.run_chess_api.verify_environment

.. py:function:: main()

   Parse arguments and run the chess API server.


   .. autolink-examples:: main
      :collapse:

.. py:function:: run_chess_api(port: int = 8000)

   Run the chess API server.


   .. autolink-examples:: run_chess_api
      :collapse:

.. py:function:: verify_environment() -> bool

   Verify that required environment variables are set.


   .. autolink-examples:: verify_environment
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.run_chess_api
   :collapse:
   
.. autolink-skip:: next
