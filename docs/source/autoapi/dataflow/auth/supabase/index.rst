
:py:mod:`dataflow.auth.supabase`
================================

.. py:module:: dataflow.auth.supabase


Classes
-------

.. autoapisummary::

   dataflow.auth.supabase.SupabaseAuth


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SupabaseAuth:

   .. graphviz::
      :align: center

      digraph inheritance_SupabaseAuth {
        node [shape=record];
        "SupabaseAuth" [label="SupabaseAuth"];
      }

.. autoclass:: dataflow.auth.supabase.SupabaseAuth
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.auth.supabase.get_auth_instance
   dataflow.auth.supabase.get_current_user
   dataflow.auth.supabase.require_auth

.. py:function:: get_auth_instance()

   Get the auth instance for dependency injection.


   .. autolink-examples:: get_auth_instance
      :collapse:

.. py:function:: get_current_user(credentials: fastapi.security.HTTPAuthorizationCredentials | None = Depends(security), auth: SupabaseAuth = Depends(get_auth_instance)) -> str | None
   :async:


   Verify the token and return the user ID.

   This is for frontend API routes - can be used with FastAPI Depends.


   .. autolink-examples:: get_current_user
      :collapse:

.. py:function:: require_auth(user_id: str | None = Depends(get_current_user)) -> str
   :async:


   Require authentication for a route.

   Raises HTTPException if not authenticated.


   .. autolink-examples:: require_auth
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.auth.supabase
   :collapse:
   
.. autolink-skip:: next
