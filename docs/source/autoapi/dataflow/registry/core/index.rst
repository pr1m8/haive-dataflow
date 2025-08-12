
:py:mod:`dataflow.registry.core`
================================

.. py:module:: dataflow.registry.core

Core Registry System for Haive.

This module implements the central registry system for the Haive framework,
providing functionality for registering, querying, and managing various components
such as agents, tools, engines, and other entity types.

The registry system maintains both in-memory storage and database persistence
through Supabase integration, allowing components to be discovered, registered,
and retrieved across application sessions.

.. rubric:: Examples

Basic usage of the registry system:

>>> from haive.dataflow.registry.core import registry_system
>>> from haive.dataflow.registry.models import EntityType
>>>
>>> # Register a new component
>>> entity_id = registry_system.register_entity(
...     name="TextSummarizer",
...     type=EntityType.TOOL,
...     description="Summarizes text documents",
...     module_path="haive.tools.summarizers",
...     class_name="TextSummarizerTool"
... )
>>>
>>> # Query for components by type
>>> tools = registry_system.get_entities_by_type(EntityType.TOOL)
>>> print(f"Found {len(tools)} registered tools")
>>>
>>> # Get a specific component by ID
>>> entity = registry_system.get_entity(entity_id)
>>> print(f"Retrieved entity: {entity.name}")


.. autolink-examples:: dataflow.registry.core
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.core.ConfigType
   dataflow.registry.core.DependencyType
   dataflow.registry.core.EntityType
   dataflow.registry.core.ImportStatus
   dataflow.registry.core.LazyRegistrySystem
   dataflow.registry.core.RegistrySystem


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ConfigType:

   .. graphviz::
      :align: center

      digraph inheritance_ConfigType {
        node [shape=record];
        "ConfigType" [label="ConfigType"];
        "str" -> "ConfigType";
        "enum.Enum" -> "ConfigType";
      }

.. autoclass:: dataflow.registry.core.ConfigType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ConfigType** is an Enum defined in ``dataflow.registry.core``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for DependencyType:

   .. graphviz::
      :align: center

      digraph inheritance_DependencyType {
        node [shape=record];
        "DependencyType" [label="DependencyType"];
        "str" -> "DependencyType";
        "enum.Enum" -> "DependencyType";
      }

.. autoclass:: dataflow.registry.core.DependencyType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **DependencyType** is an Enum defined in ``dataflow.registry.core``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for EntityType:

   .. graphviz::
      :align: center

      digraph inheritance_EntityType {
        node [shape=record];
        "EntityType" [label="EntityType"];
        "str" -> "EntityType";
        "enum.Enum" -> "EntityType";
      }

.. autoclass:: dataflow.registry.core.EntityType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **EntityType** is an Enum defined in ``dataflow.registry.core``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ImportStatus:

   .. graphviz::
      :align: center

      digraph inheritance_ImportStatus {
        node [shape=record];
        "ImportStatus" [label="ImportStatus"];
        "str" -> "ImportStatus";
        "enum.Enum" -> "ImportStatus";
      }

.. autoclass:: dataflow.registry.core.ImportStatus
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ImportStatus** is an Enum defined in ``dataflow.registry.core``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for LazyRegistrySystem:

   .. graphviz::
      :align: center

      digraph inheritance_LazyRegistrySystem {
        node [shape=record];
        "LazyRegistrySystem" [label="LazyRegistrySystem"];
      }

.. autoclass:: dataflow.registry.core.LazyRegistrySystem
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistrySystem:

   .. graphviz::
      :align: center

      digraph inheritance_RegistrySystem {
        node [shape=record];
        "RegistrySystem" [label="RegistrySystem"];
      }

.. autoclass:: dataflow.registry.core.RegistrySystem
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.registry.core.get_registry_system

.. py:function:: get_registry_system()

   Get the registry system instance (lazy initialization).


   .. autolink-examples:: get_registry_system
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.core
   :collapse:
   
.. autolink-skip:: next
