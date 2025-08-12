
:py:mod:`dataflow.persistence.supabase_adapter`
===============================================

.. py:module:: dataflow.persistence.supabase_adapter

Supabase persistence adapter for the Haive framework.

This module provides an adapter for persisting data to Supabase's PostgreSQL
database. It handles the connection management, Row-Level Security (RLS)
context, and provides methods for storing and retrieving data.

The adapter integrates with Haive's core persistence system, specifically
the PostgreSQL checkpointer, to provide a consistent interface for data
storage and retrieval while respecting Supabase's security model.

Key features:
- RLS context management for proper access control
- Connection pooling and management
- Checkpointing for LangGraph state persistence
- Thread registration for conversation tracking

Typical usage example:

    ```python
    from haive.dataflow.persistence.supabase_adapter import SupabasePersistence

    # Create the persistence adapter
    persistence = SupabasePersistence()

    # Register a thread
    thread_id = await persistence.register_thread(
        user_id="user-123",
        metadata={"agent_id": "agent-456"}
    )

    # Store a checkpoint
    await persistence.store_checkpoint(
        thread_id=thread_id,
        checkpoint_id="checkpoint-1",
        state={"key": "value"},
        user_id="user-123"
    )

    # Retrieve a checkpoint
    checkpoint = await persistence.get_checkpoint(
        thread_id=thread_id,
        checkpoint_id="checkpoint-1",
        user_id="user-123"
    )
    ```


.. autolink-examples:: dataflow.persistence.supabase_adapter
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.persistence.supabase_adapter.SupabasePersistence


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SupabasePersistence:

   .. graphviz::
      :align: center

      digraph inheritance_SupabasePersistence {
        node [shape=record];
        "SupabasePersistence" [label="SupabasePersistence"];
      }

.. autoclass:: dataflow.persistence.supabase_adapter.SupabasePersistence
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.persistence.supabase_adapter
   :collapse:
   
.. autolink-skip:: next
