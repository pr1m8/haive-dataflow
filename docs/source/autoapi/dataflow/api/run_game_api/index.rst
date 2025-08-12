
:py:mod:`dataflow.api.run_game_api`
===================================

.. py:module:: dataflow.api.run_game_api

Run the Haive Game API with the dynamically discovered game agents.

This script creates a FastAPI application that includes both the main API
and the game routes for all discovered game agents. It runs the server
on port 8005 with uvicorn.

Example usage:
    python -m haive.dataflow.api.run_game_api


.. autolink-examples:: dataflow.api.run_game_api
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.run_game_api.create_app
   dataflow.api.run_game_api.main

.. py:function:: create_app()

   Create FastAPI app with game routes.


   .. autolink-examples:: create_app
      :collapse:

.. py:function:: main()

   Run the API server.


   .. autolink-examples:: main
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.run_game_api
   :collapse:
   
.. autolink-skip:: next
