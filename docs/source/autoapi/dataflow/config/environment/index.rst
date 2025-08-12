
:py:mod:`dataflow.config.environment`
=====================================

.. py:module:: dataflow.config.environment


Classes
-------

.. autoapisummary::

   dataflow.config.environment.PostgresConfig
   dataflow.config.environment.SupabaseClientConfig
   dataflow.config.environment.SupabaseServerConfig


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for PostgresConfig:

   .. graphviz::
      :align: center

      digraph inheritance_PostgresConfig {
        node [shape=record];
        "PostgresConfig" [label="PostgresConfig"];
        "pydantic.BaseModel" -> "PostgresConfig";
      }

.. autopydantic_model:: dataflow.config.environment.PostgresConfig
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

   Inheritance diagram for SupabaseClientConfig:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseClientConfig {
        node [shape=record];
        "SupabaseClientConfig" [label="SupabaseClientConfig"];
        "pydantic.BaseModel" -> "SupabaseClientConfig";
      }

.. autopydantic_model:: dataflow.config.environment.SupabaseClientConfig
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

   Inheritance diagram for SupabaseServerConfig:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseServerConfig {
        node [shape=record];
        "SupabaseServerConfig" [label="SupabaseServerConfig"];
        "pydantic.BaseModel" -> "SupabaseServerConfig";
      }

.. autopydantic_model:: dataflow.config.environment.SupabaseServerConfig
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



Functions
---------

.. autoapisummary::

   dataflow.config.environment.get_postgres_config
   dataflow.config.environment.get_supabase_client_config
   dataflow.config.environment.get_supabase_server_config

.. py:function:: get_postgres_config() -> PostgresConfig

   Get PostgreSQL configuration from environment.


   .. autolink-examples:: get_postgres_config
      :collapse:

.. py:function:: get_supabase_client_config() -> SupabaseClientConfig

   Get Supabase client configuration from environment.


   .. autolink-examples:: get_supabase_client_config
      :collapse:

.. py:function:: get_supabase_server_config() -> SupabaseServerConfig

   Get Supabase server configuration from environment.


   .. autolink-examples:: get_supabase_server_config
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.config.environment
   :collapse:
   
.. autolink-skip:: next
