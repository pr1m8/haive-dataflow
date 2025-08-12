
:py:mod:`dataflow.registry.db`
==============================

.. py:module:: dataflow.registry.db

Database schema and operations for the registry system.

This module provides database integration for the registry system, focusing on:
1. Schema creation and migration
2. Supabase integration
3. Relations between registry items and state schemas
4. Agent graph storage


.. autolink-examples:: dataflow.registry.db
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.db.AgentGraph
   dataflow.registry.db.RegistryDB
   dataflow.registry.db.RegistrySchema
   dataflow.registry.db.SchemaDefinition


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentGraph:

   .. graphviz::
      :align: center

      digraph inheritance_AgentGraph {
        node [shape=record];
        "AgentGraph" [label="AgentGraph"];
        "pydantic.BaseModel" -> "AgentGraph";
      }

.. autopydantic_model:: dataflow.registry.db.AgentGraph
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


:orphan:



.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistryDB:

   .. graphviz::
      :align: center

      digraph inheritance_RegistryDB {
        node [shape=record];
        "RegistryDB" [label="RegistryDB"];
      }

.. autoclass:: dataflow.registry.db.RegistryDB
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistrySchema:

   .. graphviz::
      :align: center

      digraph inheritance_RegistrySchema {
        node [shape=record];
        "RegistrySchema" [label="RegistrySchema"];
        "pydantic.BaseModel" -> "RegistrySchema";
      }

.. autopydantic_model:: dataflow.registry.db.RegistrySchema
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

   Inheritance diagram for SchemaDefinition:

   .. graphviz::
      :align: center

      digraph inheritance_SchemaDefinition {
        node [shape=record];
        "SchemaDefinition" [label="SchemaDefinition"];
        "pydantic.BaseModel" -> "SchemaDefinition";
      }

.. autopydantic_model:: dataflow.registry.db.SchemaDefinition
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





.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.db
   :collapse:
   
.. autolink-skip:: next
