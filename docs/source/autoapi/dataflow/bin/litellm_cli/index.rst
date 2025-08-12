
:py:mod:`dataflow.bin.litellm_cli`
==================================

.. py:module:: dataflow.bin.litellm_cli

Haive Vault CLI.

A command-line utility for managing vault secrets and model imports.

Usage:
    python haive_vault_cli.py [command] [options]

Commands:
    migrate     Migrate API keys and secrets to the vault
    import      Import LLM and embedding models
    verify      Verify vault secret references
    help        Show this help message


.. autolink-examples:: dataflow.bin.litellm_cli
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.bin.litellm_cli.main
   dataflow.bin.litellm_cli.run_import
   dataflow.bin.litellm_cli.run_migrate
   dataflow.bin.litellm_cli.run_verify

.. py:function:: main()

.. py:function:: run_import(model_type=None, skip_llm=False, skip_embeddings=False, no_progress=False)

   Run the model importer.


   .. autolink-examples:: run_import
      :collapse:

.. py:function:: run_migrate()

   Run the migration script.


   .. autolink-examples:: run_migrate
      :collapse:

.. py:function:: run_verify()

   Run the verification script.


   .. autolink-examples:: run_verify
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.bin.litellm_cli
   :collapse:
   
.. autolink-skip:: next
