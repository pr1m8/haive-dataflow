
:py:mod:`dataflow.registry.importers.litellm_importer`
======================================================

.. py:module:: dataflow.registry.importers.litellm_importer

LiteLLM model importer for the Haive registry system.

This module provides functionality to import LLM and embedding models from
LiteLLM's model data repository into the Haive registry system. It fetches
model information including pricing, context windows, and capabilities,
then registers them in the registry database.

The importer handles various model providers including OpenAI, Anthropic,
Google, Mistral, and others. It extracts model metadata, capabilities, and
pricing information, ensuring comprehensive model registration.

Key functions:
- Fetching model data from LiteLLM's GitHub repository
- Creating provider types and model entries in the registry
- Extracting model capabilities and specifications
- Tracking import operations and results

Typical usage example:

    ```python
    from haive.dataflow.registry.importers.litellm_importer import import_litellm_models

    # Import all models from LiteLLM
    session_id, import_count = import_litellm_models()
    print(f"Imported {import_count} models in session {session_id}")

    # Import models from a specific provider
    session_id, import_count = import_litellm_models(provider_filter="openai")
    print(f"Imported {import_count} OpenAI models")
    ```


.. autolink-examples:: dataflow.registry.importers.litellm_importer
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.registry.importers.litellm_importer.add_import_log
   dataflow.registry.importers.litellm_importer.get_or_create_provider
   dataflow.registry.importers.litellm_importer.get_or_create_provider_type
   dataflow.registry.importers.litellm_importer.import_embedding_models
   dataflow.registry.importers.litellm_importer.import_from_env
   dataflow.registry.importers.litellm_importer.import_llm_models
   dataflow.registry.importers.litellm_importer.main

.. py:function:: add_import_log(entity_name: str, entity_type: str, status: str, message: str) -> None

   Add an import log entry to the audit.import_logs table.


   .. autolink-examples:: add_import_log
      :collapse:

.. py:function:: get_or_create_provider(provider_name: str, provider_type: str) -> dict[str, Any] | None

   Get or create a provider and return its data.


   .. autolink-examples:: get_or_create_provider
      :collapse:

.. py:function:: get_or_create_provider_type(type_name: str, display_name: str) -> str | None

   Get or create a provider type in the registry.

   This function checks if a provider type exists in the registry database,
   and creates it if it doesn't exist. It's used to ensure that all required
   provider types are available before importing models.

   :param type_name: The internal name/ID of the provider type
   :param display_name: The human-readable name of the provider

   :returns: The ID of the provider type, or None if creation failed
   :rtype: Optional[str]

   .. rubric:: Example

   >>> provider_id = get_or_create_provider_type("openai", "OpenAI")
   >>> if provider_id:
   ...     print(f"Provider type ID: {provider_id}")


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

.. autolink-examples:: dataflow.registry.importers.litellm_importer
   :collapse:
   
.. autolink-skip:: next
