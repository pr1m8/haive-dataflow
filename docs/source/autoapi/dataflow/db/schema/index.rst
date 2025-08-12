
:py:mod:`dataflow.db.schema`
============================

.. py:module:: dataflow.db.schema

Database schema management for the Haive Registry System.

This module provides functions for creating and managing the database
schema for the registry system. It handles schema creation, migrations,
and upgrades as needed.


.. autolink-examples:: dataflow.db.schema
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.db.schema.check_schema_exists
   dataflow.db.schema.check_table_exists
   dataflow.db.schema.create_schema_sql
   dataflow.db.schema.execute_schema_sql
   dataflow.db.schema.initialize_database
   dataflow.db.schema.setup_execute_sql_function
   dataflow.db.schema.setup_schema

.. py:function:: check_schema_exists(client=None) -> bool

   Check if the registry schema exists.

   :param client: Optional Supabase client

   :returns: True if the schema exists, False otherwise


   .. autolink-examples:: check_schema_exists
      :collapse:

.. py:function:: check_table_exists(table_name: str, schema: str = 'registry', client=None) -> bool

   Check if a specific table exists.

   :param table_name: Name of the table to check
   :param schema: Schema name
   :param client: Optional Supabase client

   :returns: True if the table exists, False otherwise


   .. autolink-examples:: check_table_exists
      :collapse:

.. py:function:: create_schema_sql() -> str

   Generate the SQL schema definition for the registry system.

   :returns: SQL schema definition as a string


   .. autolink-examples:: create_schema_sql
      :collapse:

.. py:function:: execute_schema_sql(client=None, schema_sql: str | None = None) -> bool

   Execute the schema SQL to set up the database.

   :param client: Optional Supabase client
   :param schema_sql: Optional schema SQL to execute

   :returns: True if successful, False otherwise


   .. autolink-examples:: execute_schema_sql
      :collapse:

.. py:function:: initialize_database(client=None) -> bool

   Initialize the database for the registry system.

   :param client: Optional Supabase client

   :returns: True if successful, False otherwise


   .. autolink-examples:: initialize_database
      :collapse:

.. py:function:: setup_execute_sql_function(client=None) -> bool

   Set up the execute_sql function in the database. This function is needed
   to execute arbitrary SQL statements.

   :param client: Optional Supabase client

   :returns: True if successful, False otherwise


   .. autolink-examples:: setup_execute_sql_function
      :collapse:

.. py:function:: setup_schema(client=None) -> bool

   Set up the database schema for the registry system.

   :param client: Optional Supabase client

   :returns: True if successful, False otherwise


   .. autolink-examples:: setup_schema
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.db.schema
   :collapse:
   
.. autolink-skip:: next
