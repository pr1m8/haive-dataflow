
:py:mod:`dataflow.importers.embeddings_importer`
================================================

.. py:module:: dataflow.importers.embeddings_importer

Embedding Models Importer for the Haive Registry System.

This module provides functionality for importing embedding models from
various providers and registering them in the system.


.. autolink-examples:: dataflow.importers.embeddings_importer
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.importers.embeddings_importer.import_embedding_models

.. py:function:: import_embedding_models() -> bool

   Import embedding models from various providers into the registry.

   This function registers embedding providers and their corresponding models
   into the Haive registry system. It handles both in-memory and Supabase
   database storage based on availability.

   :returns: True if import was successful, False otherwise.
   :rtype: bool

   .. rubric:: Example

   >>> success = import_embedding_models()
   >>> if success:
   ...     print("Embedding models imported successfully")


   .. autolink-examples:: import_embedding_models
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.importers.embeddings_importer
   :collapse:
   
.. autolink-skip:: next
