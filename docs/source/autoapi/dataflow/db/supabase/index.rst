
:py:mod:`dataflow.db.supabase`
==============================

.. py:module:: dataflow.db.supabase

Supabase database integration for the Haive registry system.

This module provides functionality for connecting to and interacting with a
Supabase database instance for storing registry data. It handles connection
management, schema mapping, and query execution.

The module uses environment variables for configuration:
- SUPABASE_URL: The URL of your Supabase instance
- SUPABASE_SERVICE_KEY: Service role API key (preferred for admin operations)
- SUPABASE_ANON_KEY: Anonymous API key (fallback)

Typical usage example:

    >>> from haive.dataflow.db.supabase import get_supabase_client
    >>>
    >>> # Get a Supabase client
    >>> supabase = get_supabase_client()
    >>>
    >>> # Query a table
    >>> result = supabase.table('registry_items').select('*').execute()
    >>> items = result.data
    >>> print(f"Found {len(items)} registry items")


.. autolink-examples:: dataflow.db.supabase
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.db.supabase.fetch_all_schemas_and_tables
   dataflow.db.supabase.fetch_foreign_key_relations
   dataflow.db.supabase.fetch_primary_keys
   dataflow.db.supabase.fetch_table_columns
   dataflow.db.supabase.get_supabase_client
   dataflow.db.supabase.parse_table_reference
   dataflow.db.supabase.sanitize_sql
   dataflow.db.supabase.table

.. py:function:: fetch_all_schemas_and_tables(client: supabase.Client) -> list[dict]

   Return all non-system tables grouped by schema using raw SQL.


   .. autolink-examples:: fetch_all_schemas_and_tables
      :collapse:

.. py:function:: fetch_foreign_key_relations(client: supabase.Client) -> list[dict]

   Return foreign key relationships between tables using raw SQL.


   .. autolink-examples:: fetch_foreign_key_relations
      :collapse:

.. py:function:: fetch_primary_keys(client: supabase.Client) -> list[dict]

   Get all primary keys per table.


   .. autolink-examples:: fetch_primary_keys
      :collapse:

.. py:function:: fetch_table_columns(client: supabase.Client) -> list[dict]

   Get all columns, types, and constraints from
   information_schema.columns.


   .. autolink-examples:: fetch_table_columns
      :collapse:

.. py:function:: get_supabase_client(schema: str | None = None) -> supabase.Client

   Get a configured Supabase client instance.

   Creates and returns a Supabase client configured with the specified schema.
   The client uses environment variables for connection parameters.

   :param schema: Optional database schema to use. If not specified,
                  defaults to "public" schema.

   :returns: A configured Supabase client instance.
   :rtype: Client

   :raises EnvironmentError: If required environment variables are not set.

   .. rubric:: Example

   >>> # Get client with default schema
   >>> client = get_supabase_client()
   >>>
   >>> # Get client with specific schema
   >>> registry_client = get_supabase_client("registry")


   .. autolink-examples:: get_supabase_client
      :collapse:

.. py:function:: parse_table_reference(table_ref: str) -> tuple[str, str | None]

   Parse a table reference to extract table name and schema.

   This function parses table references in various formats and extracts
   the table name and schema. It handles:
   - Simple table names: "items" (uses default schema mapping)
   - Schema-qualified names: "registry.items" (explicit schema)

   :param table_ref: Table reference string in one of the supported formats.
                     Examples: "items", "registry.items", "models.providers"

   :returns:

             A tuple containing (table_name, schema_name),
                 where schema_name may be None if not specified and not in DEFAULT_SCHEMA_MAP.
   :rtype: Tuple[str, Optional[str]]

   .. rubric:: Example

   >>> parse_table_reference("items")
   ('items', 'registry')  # Uses default schema mapping
   >>> parse_table_reference("registry.items")
   ('items', 'registry')  # Explicit schema
   >>> parse_table_reference("custom_table")
   ('custom_table', None)  # No mapping found


   .. autolink-examples:: parse_table_reference
      :collapse:

.. py:function:: sanitize_sql(sql: str) -> str

   Remove trailing semicolons and whitespace for safe RPC use.


   .. autolink-examples:: sanitize_sql
      :collapse:

.. py:function:: table(client: supabase.Client, table_ref: str, schema_override: str | None = None) -> Any

   Get a table reference with appropriate schema handling.

   :param client: Supabase client
   :param table_ref: Table reference (can include schema)
   :param schema_override: Optional schema to override detected schema

   :returns: Table reference for queries


   .. autolink-examples:: table
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.db.supabase
   :collapse:
   
.. autolink-skip:: next
