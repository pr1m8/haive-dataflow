
:py:mod:`dataflow.registry.lazy_core`
=====================================

.. py:module:: dataflow.registry.lazy_core

Lazy-loading Registry System for Haive.

This module provides a lazy-loading version of the registry system that
only initializes the Supabase connection when actually needed,
preventing heavy initialization at import time.

The lazy registry system maintains the same interface as the original
but defers expensive operations until they're actually used.


.. autolink-examples:: dataflow.registry.lazy_core
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.lazy_core.LazyRegistrySystem


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for LazyRegistrySystem:

   .. graphviz::
      :align: center

      digraph inheritance_LazyRegistrySystem {
        node [shape=record];
        "LazyRegistrySystem" [label="LazyRegistrySystem"];
      }

.. autoclass:: dataflow.registry.lazy_core.LazyRegistrySystem
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.registry.lazy_core.get_registry_system

.. py:function:: get_registry_system() -> LazyRegistrySystem

   Get the singleton registry system instance.


   .. autolink-examples:: get_registry_system
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.lazy_core
   :collapse:
   
.. autolink-skip:: next
