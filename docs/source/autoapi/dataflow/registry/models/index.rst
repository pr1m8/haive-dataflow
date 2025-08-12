
:py:mod:`dataflow.registry.models`
==================================

.. py:module:: dataflow.registry.models

Models for the Haive Registry System.

This module defines the core data models used by the registry system to represent
different types of entities, configurations, dependencies, and other components.
These models provide a structured way to store and retrieve information about
various components in the Haive ecosystem.

The models use Pydantic for validation, serialization, and deserialization,
ensuring type safety and consistent data structures throughout the system.

Classes:
    EntityType: Enumeration of entity types that can be registered
    ConfigType: Enumeration of configuration types for registry items
    DependencyType: Enumeration of dependency relationships between entities
    ImportStatus: Enumeration of import operation status values
    RegistryItem: Base model for all registry entries
    Configuration: Model for configuration data associated with registry items
    GraphDefinition: Model for graph structure definitions (nodes and edges)
    Dependency: Model for dependency relationships between registry items
    EnvironmentVar: Model for environment variable requirements
    ImportLogItem: Model for logging import operations

.. rubric:: Example

Creating registry models:

>>> from haive.dataflow.registry.models import RegistryItem, EntityType
>>> from datetime import datetime
>>>
>>> # Create a new registry item
>>> item = RegistryItem(
...     name="TextClassifier",
...     type=EntityType.AGENT,
...     description="Classifies text into categories",
...     module_path="haive.agents.classifiers",
...     class_name="TextClassifierAgent",
...     created_at=datetime.now()
... )
>>>
>>> # Access properties
>>> print(f"Registry item: {item.name} ({item.type})")
>>> print(f"Created at: {item.created_at}")


.. autolink-examples:: dataflow.registry.models
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.models.ConfigType
   dataflow.registry.models.Configuration
   dataflow.registry.models.Dependency
   dataflow.registry.models.DependencyType
   dataflow.registry.models.EntityType
   dataflow.registry.models.EnvironmentVar
   dataflow.registry.models.GraphDefinition
   dataflow.registry.models.ImportLogItem
   dataflow.registry.models.ImportStatus
   dataflow.registry.models.MCPPromptDefinition
   dataflow.registry.models.MCPResourceDefinition
   dataflow.registry.models.MCPServerConfig
   dataflow.registry.models.MCPServerHealth
   dataflow.registry.models.MCPToolDefinition
   dataflow.registry.models.MCPTransport
   dataflow.registry.models.RegistryItem


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

.. autoclass:: dataflow.registry.models.ConfigType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ConfigType** is an Enum defined in ``dataflow.registry.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Configuration:

   .. graphviz::
      :align: center

      digraph inheritance_Configuration {
        node [shape=record];
        "Configuration" [label="Configuration"];
        "pydantic.BaseModel" -> "Configuration";
      }

.. autopydantic_model:: dataflow.registry.models.Configuration
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

.. autopydantic_model:: dataflow.registry.models.Dependency
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

.. autoclass:: dataflow.registry.models.DependencyType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **DependencyType** is an Enum defined in ``dataflow.registry.models``.





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

.. autoclass:: dataflow.registry.models.EntityType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **EntityType** is an Enum defined in ``dataflow.registry.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for EnvironmentVar:

   .. graphviz::
      :align: center

      digraph inheritance_EnvironmentVar {
        node [shape=record];
        "EnvironmentVar" [label="EnvironmentVar"];
        "pydantic.BaseModel" -> "EnvironmentVar";
      }

.. autopydantic_model:: dataflow.registry.models.EnvironmentVar
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

.. autopydantic_model:: dataflow.registry.models.GraphDefinition
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

.. autopydantic_model:: dataflow.registry.models.ImportLogItem
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

.. autoclass:: dataflow.registry.models.ImportStatus
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **ImportStatus** is an Enum defined in ``dataflow.registry.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPPromptDefinition:

   .. graphviz::
      :align: center

      digraph inheritance_MCPPromptDefinition {
        node [shape=record];
        "MCPPromptDefinition" [label="MCPPromptDefinition"];
        "pydantic.BaseModel" -> "MCPPromptDefinition";
      }

.. autopydantic_model:: dataflow.registry.models.MCPPromptDefinition
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

   Inheritance diagram for MCPResourceDefinition:

   .. graphviz::
      :align: center

      digraph inheritance_MCPResourceDefinition {
        node [shape=record];
        "MCPResourceDefinition" [label="MCPResourceDefinition"];
        "pydantic.BaseModel" -> "MCPResourceDefinition";
      }

.. autopydantic_model:: dataflow.registry.models.MCPResourceDefinition
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

   Inheritance diagram for MCPServerConfig:

   .. graphviz::
      :align: center

      digraph inheritance_MCPServerConfig {
        node [shape=record];
        "MCPServerConfig" [label="MCPServerConfig"];
        "pydantic.BaseModel" -> "MCPServerConfig";
      }

.. autopydantic_model:: dataflow.registry.models.MCPServerConfig
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

   Inheritance diagram for MCPServerHealth:

   .. graphviz::
      :align: center

      digraph inheritance_MCPServerHealth {
        node [shape=record];
        "MCPServerHealth" [label="MCPServerHealth"];
        "pydantic.BaseModel" -> "MCPServerHealth";
      }

.. autopydantic_model:: dataflow.registry.models.MCPServerHealth
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

   Inheritance diagram for MCPToolDefinition:

   .. graphviz::
      :align: center

      digraph inheritance_MCPToolDefinition {
        node [shape=record];
        "MCPToolDefinition" [label="MCPToolDefinition"];
        "pydantic.BaseModel" -> "MCPToolDefinition";
      }

.. autopydantic_model:: dataflow.registry.models.MCPToolDefinition
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

   Inheritance diagram for MCPTransport:

   .. graphviz::
      :align: center

      digraph inheritance_MCPTransport {
        node [shape=record];
        "MCPTransport" [label="MCPTransport"];
        "str" -> "MCPTransport";
        "enum.Enum" -> "MCPTransport";
      }

.. autoclass:: dataflow.registry.models.MCPTransport
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **MCPTransport** is an Enum defined in ``dataflow.registry.models``.





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistryItem:

   .. graphviz::
      :align: center

      digraph inheritance_RegistryItem {
        node [shape=record];
        "RegistryItem" [label="RegistryItem"];
        "pydantic.BaseModel" -> "RegistryItem";
      }

.. autopydantic_model:: dataflow.registry.models.RegistryItem
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

.. autolink-examples:: dataflow.registry.models
   :collapse:
   
.. autolink-skip:: next
