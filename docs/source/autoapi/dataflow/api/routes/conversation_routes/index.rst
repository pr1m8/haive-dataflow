
:py:mod:`dataflow.api.routes.conversation_routes`
=================================================

.. py:module:: dataflow.api.routes.conversation_routes

Conversation management API routes.

This module provides FastAPI routes for managing conversations between users
and agents. It supports operations like creating, listing, retrieving, and
deleting conversations, as well as adding messages to existing conversations.

The conversation system provides persistence for chat history, enabling
users to continue conversations across sessions. It also includes integration
with the credits system for tracking usage and enforcing limits.

Key features:
- Conversation CRUD operations
- Message management
- Usage tracking and credits
- Pagination for conversation listing
- Agent integration

Typical usage example:

    ```python
    # Client-side code to create and use a conversation
    import requests

    # Create a new conversation
    response = requests.post(
        "http://localhost:8000/api/conversations",
        json={
            "title": "My Conversation",
            "agent_id": "agent-123",
            "metadata": {"topic": "AI Ethics"}
        },
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )

    conversation_id = response.json()["id"]

    # Add a message to the conversation
    response = requests.post(
        f"http://localhost:8000/api/conversations/{conversation_id}/messages",
        json={
            "content": "Tell me about AI ethics",
            "role": "user"
        },
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    ```


.. autolink-examples:: dataflow.api.routes.conversation_routes
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.conversation_routes.AgentRegistry


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

.. autoclass:: dataflow.api.routes.conversation_routes.AgentRegistry
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.api.routes.conversation_routes.add_message
   dataflow.api.routes.conversation_routes.get_conversation
   dataflow.api.routes.conversation_routes.list_conversations

.. py:function:: add_message(thread_id: str, message: dict[str, Any], user_id: str = Depends(require_auth))
   :async:


   Add a message to a conversation and get a response.


   .. autolink-examples:: add_message
      :collapse:

.. py:function:: get_conversation(thread_id: str, user_id: str = Depends(require_auth))
   :async:


   Get conversation details and state.


   .. autolink-examples:: get_conversation
      :collapse:

.. py:function:: list_conversations(user_id: str = Depends(require_auth), offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100))
   :async:


   List conversations for the current user.

   This endpoint retrieves a paginated list of conversations belonging to
   the authenticated user. Results can be paginated using offset and limit
   parameters.

   :param user_id: The ID of the authenticated user (from auth dependency)
   :param offset: Number of conversations to skip (pagination offset)
   :param limit: Maximum number of conversations to return (pagination limit)

   :returns: Object containing conversations list and pagination metadata
   :rtype: dict

   :raises HTTPException: If there's an error retrieving the conversations

   .. rubric:: Example

   ```
   GET /api/conversations?offset=0&limit=20
   ```


   .. autolink-examples:: list_conversations
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.conversation_routes
   :collapse:
   
.. autolink-skip:: next
