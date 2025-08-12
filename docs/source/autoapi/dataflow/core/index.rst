
:py:mod:`dataflow.core`
=======================

.. py:module:: dataflow.core

Core Registry System for Haive.

This module provides the central registry system for managing LLM
models, embeddings, and other entity types in the system.


.. autolink-examples:: dataflow.core
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.core.ConfigType
   dataflow.core.DependencyType
   dataflow.core.EntityType
   dataflow.core.ImportStatus
   dataflow.core.RegistrySystem


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

.. autoclass:: dataflow.core.ConfigType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ConfigType** is an Enum defined in ``dataflow.core``.





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

.. autoclass:: dataflow.core.DependencyType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **DependencyType** is an Enum defined in ``dataflow.core``.





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

.. autoclass:: dataflow.core.EntityType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **EntityType** is an Enum defined in ``dataflow.core``.





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

.. autoclass:: dataflow.core.ImportStatus
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ImportStatus** is an Enum defined in ``dataflow.core``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistrySystem:

   .. graphviz::
      :align: center

      digraph inheritance_RegistrySystem {
        node [shape=record];
        "RegistrySystem" [label="RegistrySystem"];
      }

.. autoclass:: dataflow.core.RegistrySystem
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.core
   :collapse:
   
.. autolink-skip:: next
