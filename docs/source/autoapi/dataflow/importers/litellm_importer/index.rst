
:py:mod:`dataflow.importers.litellm_importer`
=============================================

.. py:module:: dataflow.importers.litellm_importer

Fixed LiteLLM Importer Module.

This module imports LLM and embedding models from LiteLLM data and other
sources into Supabase, properly handling all models without limits.


.. autolink-examples:: dataflow.importers.litellm_importer
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.importers.litellm_importer.add_import_log
   dataflow.importers.litellm_importer.get_or_create_provider
   dataflow.importers.litellm_importer.get_or_create_provider_type
   dataflow.importers.litellm_importer.import_embedding_models
   dataflow.importers.litellm_importer.import_from_env
   dataflow.importers.litellm_importer.import_llm_models
   dataflow.importers.litellm_importer.main

.. py:function:: add_import_log(entity_name: str, entity_type: str, status: str, message: str) -> None

   Add an import log entry to the audit.import_logs table.


   .. autolink-examples:: add_import_log
      :collapse:

.. py:function:: get_or_create_provider(provider_name: str, provider_type: str) -> dict[str, Any] | None

   Get or create a provider and return its data.


   .. autolink-examples:: get_or_create_provider
      :collapse:

.. py:function:: get_or_create_provider_type(type_name: str, display_name: str) -> str | None

   Get or create a provider type and return its ID.


   .. autolink-examples:: get_or_create_provider_type
      :collapse:

.. py:function:: import_embedding_models() -> int

   Import embedding models.

   Returns the number of models imported.


   .. autolink-examples:: import_embedding_models
      :collapse:

.. py:function:: import_from_env() -> list[dict[str, Any]]

   Extract embedding models from environment variables.

   Look for vars like OPENAI_EMBEDDING_MODEL, AZURE_EMBEDDING_MODEL,
   etc.


   .. autolink-examples:: import_from_env
      :collapse:

.. py:function:: import_llm_models() -> int

   Import LLM models from LiteLLM.

   Returns the number of models imported.


   .. autolink-examples:: import_llm_models
      :collapse:

.. py:function:: main()

   Main function to run the import.


   .. autolink-examples:: main
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.importers.litellm_importer
   :collapse:
   
.. autolink-skip:: next
