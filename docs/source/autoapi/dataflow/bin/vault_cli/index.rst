
:py:mod:`dataflow.bin.vault_cli`
================================

.. py:module:: dataflow.bin.vault_cli

Fixed Vault CLI.

A command-line utility to manage vault secrets and model imports, with
proper schema mapping for Supabase.


.. autolink-examples:: dataflow.bin.vault_cli
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.bin.vault_cli.add_columns
   dataflow.bin.vault_cli.ensure_vault_reference_column
   dataflow.bin.vault_cli.execute_sql
   dataflow.bin.vault_cli.find_module_path
   dataflow.bin.vault_cli.import_module
   dataflow.bin.vault_cli.main
   dataflow.bin.vault_cli.run_export
   dataflow.bin.vault_cli.run_import
   dataflow.bin.vault_cli.run_import_secrets
   dataflow.bin.vault_cli.run_migrate
   dataflow.bin.vault_cli.run_verify

.. py:function:: add_columns(args)

   Add the vault reference columns to the database tables using table()
   helper.


   .. autolink-examples:: add_columns
      :collapse:

.. py:function:: ensure_vault_reference_column(table_name: str) -> bool

   Ensure the table has a vault_reference column for secret references.
   Uses table() helper function for proper schema resolution.

   :param table_name: Full table name including schema

   :returns: True if column exists or was created, False otherwise


   .. autolink-examples:: ensure_vault_reference_column
      :collapse:

.. py:function:: execute_sql(sql: str) -> Any

   Execute SQL safely through Supabase RPC function.


   .. autolink-examples:: execute_sql
      :collapse:

.. py:function:: find_module_path(module_name)

   Find and import a module from the given paths.


   .. autolink-examples:: find_module_path
      :collapse:

.. py:function:: import_module(module_name, module_path)

   Import a module from a file path.


   .. autolink-examples:: import_module
      :collapse:

.. py:function:: main()

   Main entry point for the CLI.


   .. autolink-examples:: main
      :collapse:

.. py:function:: run_export(args)

   Export secrets from the vault.


   .. autolink-examples:: run_export
      :collapse:

.. py:function:: run_import(args)

   Run the model import.


   .. autolink-examples:: run_import
      :collapse:

.. py:function:: run_import_secrets(args)

   Import secrets into the vault.


   .. autolink-examples:: run_import_secrets
      :collapse:

.. py:function:: run_migrate(args)

   Run the vault migration.


   .. autolink-examples:: run_migrate
      :collapse:

.. py:function:: run_verify(args)

   Run the vault verification.


   .. autolink-examples:: run_verify
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.bin.vault_cli
   :collapse:
   
.. autolink-skip:: next
