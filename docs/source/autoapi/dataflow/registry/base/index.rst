
:py:mod:`dataflow.registry.base`
================================

.. py:module:: dataflow.registry.base

Base registry system for Haive components.

This module provides the fundamental registry system that all specific
registries inherit from. It handles registration, discovery, database
persistence, and retrieval of components.


.. autolink-examples:: dataflow.registry.base
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.base.Registry
   dataflow.registry.base.RegistryItem


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Registry:

   .. graphviz::
      :align: center

      digraph inheritance_Registry {
        node [shape=record];
        "Registry" [label="Registry"];
        "Generic[T]" -> "Registry";
      }

.. autoclass:: dataflow.registry.base.Registry
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for RegistryItem:

   .. graphviz::
      :align: center

      digraph inheritance_RegistryItem {
        node [shape=record];
        "RegistryItem" [label="RegistryItem"];
        "pydantic.BaseModel" -> "RegistryItem";
      }

.. autopydantic_model:: dataflow.registry.base.RegistryItem
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

   dataflow.registry.base.create
   dataflow.registry.base.get
   dataflow.registry.base.register

.. py:function:: create(registry: Registry, name: str, *args, **kwargs)

   Create a component instance from a registry.


   .. autolink-examples:: create
      :collapse:

.. py:function:: get(registry: Registry, name: str)

   Get a component from a registry.


   .. autolink-examples:: get
      :collapse:

.. py:function:: register(registry: Registry, name: str | None = None, **kwargs)

   Register a component in a registry.


   .. autolink-examples:: register
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.base
   :collapse:
   
.. autolink-skip:: next
