
:py:mod:`dataflow.api.general_games_api`
========================================

.. py:module:: dataflow.api.general_games_api

General API system for all haive games.

This module provides a general-purpose API that automatically discovers
all available games and creates endpoints for each one, with OpenAPI
documentation and game selection capabilities.


.. autolink-examples:: dataflow.api.general_games_api
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.general_games_api.GameInfo
   dataflow.api.general_games_api.GameSelectionRequest
   dataflow.api.general_games_api.GeneralGameAPI


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for GameInfo:

   .. graphviz::
      :align: center

      digraph inheritance_GameInfo {
        node [shape=record];
        "GameInfo" [label="GameInfo"];
        "pydantic.BaseModel" -> "GameInfo";
      }

.. autopydantic_model:: dataflow.api.general_games_api.GameInfo
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

   Inheritance diagram for GameSelectionRequest:

   .. graphviz::
      :align: center

      digraph inheritance_GameSelectionRequest {
        node [shape=record];
        "GameSelectionRequest" [label="GameSelectionRequest"];
        "pydantic.BaseModel" -> "GameSelectionRequest";
      }

.. autopydantic_model:: dataflow.api.general_games_api.GameSelectionRequest
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

   Inheritance diagram for GeneralGameAPI:

   .. graphviz::
      :align: center

      digraph inheritance_GeneralGameAPI {
        node [shape=record];
        "GeneralGameAPI" [label="GeneralGameAPI"];
      }

.. autoclass:: dataflow.api.general_games_api.GeneralGameAPI
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.api.general_games_api.create_general_game_api

.. py:function:: create_general_game_api(app: fastapi.FastAPI | None = None, **kwargs) -> tuple[fastapi.FastAPI, GeneralGameAPI]

   Create a general game API that discovers all games.

   :param app: Optional FastAPI app (creates one if not provided)
   :param \*\*kwargs: Additional arguments for GeneralGameAPI

   :returns: Tuple of (FastAPI app, GeneralGameAPI instance)

   .. rubric:: Example

   >>> app, game_api = create_general_game_api()
   >>> # Now you have endpoints for all games!


   .. autolink-examples:: create_general_game_api
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.general_games_api
   :collapse:
   
.. autolink-skip:: next
