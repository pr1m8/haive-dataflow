
:py:mod:`dataflow.api.middleware.supabase_logging`
==================================================

.. py:module:: dataflow.api.middleware.supabase_logging


Classes
-------

.. autoapisummary::

   dataflow.api.middleware.supabase_logging.LLMLogger
   dataflow.api.middleware.supabase_logging.SupabaseLogger
   dataflow.api.middleware.supabase_logging.SupabaseLoggingMiddleware


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for LLMLogger:

   .. graphviz::
      :align: center

      digraph inheritance_LLMLogger {
        node [shape=record];
        "LLMLogger" [label="LLMLogger"];
      }

.. autoclass:: dataflow.api.middleware.supabase_logging.LLMLogger
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SupabaseLogger:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseLogger {
        node [shape=record];
        "SupabaseLogger" [label="SupabaseLogger"];
      }

.. autoclass:: dataflow.api.middleware.supabase_logging.SupabaseLogger
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SupabaseLoggingMiddleware:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseLoggingMiddleware {
        node [shape=record];
        "SupabaseLoggingMiddleware" [label="SupabaseLoggingMiddleware"];
        "starlette.middleware.base.BaseHTTPMiddleware" -> "SupabaseLoggingMiddleware";
      }

.. autoclass:: dataflow.api.middleware.supabase_logging.SupabaseLoggingMiddleware
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.api.middleware.supabase_logging
   :collapse:
   
.. autolink-skip:: next
