
:py:mod:`dataflow.models`
=========================

.. py:module:: dataflow.models

Models for the Haive Registry System.

This module defines the core models used by the registry system to
represent different types of entities, configurations, dependencies,
etc.


.. autolink-examples:: dataflow.models
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.models.ConfigType
   dataflow.models.Configuration
   dataflow.models.Dependency
   dataflow.models.DependencyType
   dataflow.models.EntityType
   dataflow.models.EnvironmentVar
   dataflow.models.GraphDefinition
   dataflow.models.ImportLogItem
   dataflow.models.ImportStatus
   dataflow.models.RegistryItem


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

.. autoclass:: dataflow.models.ConfigType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ConfigType** is an Enum defined in ``dataflow.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Configuration:

   .. graphviz::
      :align: center

      digraph inheritance_Configuration {
        node [shape=record];
        "Configuration" [label="Configuration"];
        "pydantic.BaseModel" -> "Configuration";
      }

.. autopydantic_model:: dataflow.models.Configuration
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

   Inheritance diagram for Dependency:

   .. graphviz::
      :align: center

      digraph inheritance_Dependency {
        node [shape=record];
        "Dependency" [label="Dependency"];
        "pydantic.BaseModel" -> "Dependency";
      }

.. autopydantic_model:: dataflow.models.Dependency
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

   Inheritance diagram for DependencyType:

   .. graphviz::
      :align: center

      digraph inheritance_DependencyType {
        node [shape=record];
        "DependencyType" [label="DependencyType"];
        "str" -> "DependencyType";
        "enum.Enum" -> "DependencyType";
      }

.. autoclass:: dataflow.models.DependencyType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **DependencyType** is an Enum defined in ``dataflow.models``.





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

.. autoclass:: dataflow.models.EntityType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **EntityType** is an Enum defined in ``dataflow.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for EnvironmentVar:

   .. graphviz::
      :align: center

      digraph inheritance_EnvironmentVar {
        node [shape=record];
        "EnvironmentVar" [label="EnvironmentVar"];
        "pydantic.BaseModel" -> "EnvironmentVar";
      }

.. autopydantic_model:: dataflow.models.EnvironmentVar
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

   Inheritance diagram for GraphDefinition:

   .. graphviz::
      :align: center

      digraph inheritance_GraphDefinition {
        node [shape=record];
        "GraphDefinition" [label="GraphDefinition"];
        "pydantic.BaseModel" -> "GraphDefinition";
      }

.. autopydantic_model:: dataflow.models.GraphDefinition
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

   Inheritance diagram for ImportLogItem:

   .. graphviz::
      :align: center

      digraph inheritance_ImportLogItem {
        node [shape=record];
        "ImportLogItem" [label="ImportLogItem"];
        "pydantic.BaseModel" -> "ImportLogItem";
      }

.. autopydantic_model:: dataflow.models.ImportLogItem
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

   Inheritance diagram for ImportStatus:

   .. graphviz::
      :align: center

      digraph inheritance_ImportStatus {
        node [shape=record];
        "ImportStatus" [label="ImportStatus"];
        "str" -> "ImportStatus";
        "enum.Enum" -> "ImportStatus";
      }

.. autoclass:: dataflow.models.ImportStatus
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ImportStatus** is an Enum defined in ``dataflow.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistryItem:

   .. graphviz::
      :align: center

      digraph inheritance_RegistryItem {
        node [shape=record];
        "RegistryItem" [label="RegistryItem"];
        "pydantic.BaseModel" -> "RegistryItem";
      }

.. autopydantic_model:: dataflow.models.RegistryItem
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

.. autolink-examples:: dataflow.models
   :collapse:
   
.. autolink-skip:: next
