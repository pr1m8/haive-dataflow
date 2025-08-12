
:py:mod:`dataflow.registry.utils.vault_migration_script`
========================================================

.. py:module:: dataflow.registry.utils.vault_migration_script

Fixed Vault Reference Migration Script.

This script migrates API keys and secrets to the vault schema, using
proper schema mapping with the existing table() helper function.


.. autolink-examples:: dataflow.registry.utils.vault_migration_script
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.registry.utils.vault_migration_script.add_vault_helper_functions
   dataflow.registry.utils.vault_migration_script.create_vault_secret
   dataflow.registry.utils.vault_migration_script.ensure_vault_reference_column
   dataflow.registry.utils.vault_migration_script.execute_sql
   dataflow.registry.utils.vault_migration_script.get_existing_vault_secrets
   dataflow.registry.utils.vault_migration_script.main
   dataflow.registry.utils.vault_migration_script.migrate_component_env_mappings
   dataflow.registry.utils.vault_migration_script.migrate_engine_api_keys
   dataflow.registry.utils.vault_migration_script.migrate_environment_variables
   dataflow.registry.utils.vault_migration_script.migrate_provider_api_keys

.. py:function:: add_vault_helper_functions() -> bool

   Add helper functions to resolve vault references.

   :returns: True if successful, False if SQL should be run manually


   .. autolink-examples:: add_vault_helper_functions
      :collapse:

.. py:function:: create_vault_secret(name: str, description: str, value: str | None = None) -> str | None

   Create a new secret in the vault.


   .. autolink-examples:: create_vault_secret
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

.. py:function:: get_existing_vault_secrets() -> dict[str, str]

   Get existing vault secrets to avoid duplicates.


   .. autolink-examples:: get_existing_vault_secrets
      :collapse:

.. py:function:: main()

   Main function to run the migration.


   .. autolink-examples:: main
      :collapse:

.. py:function:: migrate_component_env_mappings() -> int

   Migrate component_env_mappings to include vault references.

   :returns: Number of mappings migrated


   .. autolink-examples:: migrate_component_env_mappings
      :collapse:

.. py:function:: migrate_engine_api_keys() -> int

   Migrate engine API keys to vault references.

   :returns: Number of engines with API keys migrated


   .. autolink-examples:: migrate_engine_api_keys
      :collapse:

.. py:function:: migrate_environment_variables() -> int

   Migrate config.environment_variables to use vault references.

   :returns: Number of environment variables migrated


   .. autolink-examples:: migrate_environment_variables
      :collapse:

.. py:function:: migrate_provider_api_keys() -> int

   Migrate provider API keys to vault references.

   :returns: Number of providers migrated


   .. autolink-examples:: migrate_provider_api_keys
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.utils.vault_migration_script
   :collapse:
   
.. autolink-skip:: next
