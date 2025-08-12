
:py:mod:`dataflow.auth.middleware`
==================================

.. py:module:: dataflow.auth.middleware


Classes
-------

.. autoapisummary::

   dataflow.auth.middleware.AuthDependency
   dataflow.auth.middleware.SupabaseAuthMiddleware


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AuthDependency:

   .. graphviz::
      :align: center

      digraph inheritance_AuthDependency {
        node [shape=record];
        "AuthDependency" [label="AuthDependency"];
      }

.. autoclass:: dataflow.auth.middleware.AuthDependency
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SupabaseAuthMiddleware:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseAuthMiddleware {
        node [shape=record];
        "SupabaseAuthMiddleware" [label="SupabaseAuthMiddleware"];
        "starlette.middleware.base.BaseHTTPMiddleware" -> "SupabaseAuthMiddleware";
      }

.. autoclass:: dataflow.auth.middleware.SupabaseAuthMiddleware
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.auth.middleware
   :collapse:
   
.. autolink-skip:: next
