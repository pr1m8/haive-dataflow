
:py:mod:`dataflow.api.run_games_api`
====================================

.. py:module:: dataflow.api.run_games_api

Run the Haive Games API with dynamic game discovery.

This script runs a standalone API for game agents with dynamic discovery
from the haive-games package. It creates WebSocket endpoints for each
discovered game agent and provides HTML clients for testing.

Usage:
    python run_games_api.py


.. autolink-examples:: dataflow.api.run_games_api
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.run_games_api.create_app
   dataflow.api.run_games_api.main

.. py:function:: create_app()

   Create FastAPI app with game routes.


   .. autolink-examples:: create_app
      :collapse:

.. py:function:: main()

   Run the games API server.


   .. autolink-examples:: main
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.run_games_api
   :collapse:
   
.. autolink-skip:: next
