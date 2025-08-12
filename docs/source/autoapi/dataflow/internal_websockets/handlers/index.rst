
:py:mod:`dataflow.internal_websockets.handlers`
===============================================

.. py:module:: dataflow.internal_websockets.handlers


Classes
-------

.. autoapisummary::

   dataflow.internal_websockets.handlers.AgentRegistry


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentRegistry:

   .. graphviz::
      :align: center

      digraph inheritance_AgentRegistry {
        node [shape=record];
        "AgentRegistry" [label="AgentRegistry"];
      }

.. autoclass:: dataflow.internal_websockets.handlers.AgentRegistry
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.internal_websockets.handlers.format_chunk_for_client
   dataflow.internal_websockets.handlers.stream_agent_response

.. py:function:: format_chunk_for_client(chunk: Any) -> dict[str, Any]

   Format a streaming chunk for client consumption.


   .. autolink-examples:: format_chunk_for_client
      :collapse:

.. py:function:: stream_agent_response(websocket: fastapi.WebSocket, thread_id: str)
   :async:


   Stream agent responses via WebSocket.


   .. autolink-examples:: stream_agent_response
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.internal_websockets.handlers
   :collapse:
   
.. autolink-skip:: next
