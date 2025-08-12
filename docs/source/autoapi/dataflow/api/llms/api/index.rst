
:py:mod:`dataflow.api.llms.api`
===============================

.. py:module:: dataflow.api.llms.api

API endpoints for LLM model information and availability.

This module provides FastAPI endpoints to access and manage LLM model
data stored in Supabase. It helps bridge the client application with the
database while providing additional server-side logic.


.. autolink-examples:: dataflow.api.llms.api
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.llms.api.get_capabilities
   dataflow.api.llms.api.get_model_by_id
   dataflow.api.llms.api.get_models
   dataflow.api.llms.api.get_modes
   dataflow.api.llms.api.get_providers
   dataflow.api.llms.api.read_model
   dataflow.api.llms.api.read_models
   dataflow.api.llms.api.read_providers
   dataflow.api.llms.api.recommended_models

.. py:function:: get_capabilities()
   :async:


   Get all possible LLM capabilities.


   .. autolink-examples:: get_capabilities
      :collapse:

.. py:function:: get_model_by_id(model_id: str) -> dict[str, Any] | None

   Get a specific model by ID with all related information.

   :param model_id: The model ID to look up

   :returns: Model data with capabilities and pricing, or None if not found


   .. autolink-examples:: get_model_by_id
      :collapse:

.. py:function:: get_models(provider: str | None = None) -> list[dict[str, Any]]

   Get all models from the database.

   :param provider: Optional provider name to filter by

   :returns: List of models with their capabilities and pricing


   .. autolink-examples:: get_models
      :collapse:

.. py:function:: get_modes()
   :async:


   Get all possible LLM operation modes.


   .. autolink-examples:: get_modes
      :collapse:

.. py:function:: get_providers() -> list[haive.dataflow.api.llms.api.llms.models.Provider]

   Get all providers from the database.


   .. autolink-examples:: get_providers
      :collapse:

.. py:function:: read_model(model_id: str)
   :async:


   Get a specific model by ID.


   .. autolink-examples:: read_model
      :collapse:

.. py:function:: read_models(provider: str | None = None, capability: str | None = None)
   :async:


   Get all models with optional filtering.

   :param provider: Filter by provider name
   :param capability: Filter by capability (e.g., 'vision', 'function_calling')


   .. autolink-examples:: read_models
      :collapse:

.. py:function:: read_providers()
   :async:


   Get all LLM providers.


   .. autolink-examples:: read_providers
      :collapse:

.. py:function:: recommended_models(task: str | None = None, vision: bool | None = False, function_calling: bool | None = False, audio: bool | None = False, web_search: bool | None = False)
   :async:


   Get recommended models based on capabilities and task requirements.

   :param task: The type of task (chat, completion, embedding, etc.)
   :param vision: Whether vision capabilities are required
   :param function_calling: Whether function calling is required
   :param audio: Whether audio processing is required
   :param web_search: Whether web search is required


   .. autolink-examples:: recommended_models
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.llms.api
   :collapse:
   
.. autolink-skip:: next
