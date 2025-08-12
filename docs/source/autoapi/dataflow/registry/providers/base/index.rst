
:py:mod:`dataflow.registry.providers.base`
==========================================

.. py:module:: dataflow.registry.providers.base

Base provider class for the Haive Registry System.

This module defines the base provider class that all specific entity providers
inherit from. Entity providers are responsible for discovering, registering,
and managing specific types of entities in the registry system.

Each entity type (agent, tool, engine, etc.) has its own provider that implements
the discovery and registration logic specific to that entity type. The base
provider class defines the common interface and functionality shared by all
providers.

Classes:
    EntityProvider: Abstract base class for all entity providers

.. rubric:: Example

Implementing a custom entity provider:

>>> from haive.dataflow.registry.providers.base import EntityProvider
>>> from haive.dataflow.registry.models import EntityType
>>>
>>> class CustomProvider(EntityProvider):
...     def __init__(self):
...         super().__init__(EntityType.CUSTOM)
...
...     def discover(self, module_paths=None):
...         # Custom discovery logic
...         paths = module_paths or self.get_default_search_paths()
...         # ... discovery implementation ...
...         return registered_ids
...
...     def get_default_search_paths(self):
...         return ["my_package.custom_components"]


.. autolink-examples:: dataflow.registry.providers.base
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.providers.base.EntityProvider


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for EntityProvider:

   .. graphviz::
      :align: center

      digraph inheritance_EntityProvider {
        node [shape=record];
        "EntityProvider" [label="EntityProvider"];
        "abc.ABC" -> "EntityProvider";
      }

.. autoclass:: dataflow.registry.providers.base.EntityProvider
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.providers.base
   :collapse:
   
.. autolink-skip:: next
