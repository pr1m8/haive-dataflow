
:py:mod:`dataflow.persistence.conversations`
============================================

.. py:module:: dataflow.persistence.conversations

Conversation persistence for the Haive framework.

This module provides functionality for persisting and retrieving conversations
between users and agents. It includes classes for managing conversation metadata,
messages, and the overall conversation lifecycle.

The conversation system uses Supabase as the storage backend, providing
reliable persistence with proper authentication and access control. It supports
operations like creating conversations, adding messages, retrieving history,
and deleting conversations.

Typical usage example:

    ```python
    from haive.dataflow.persistence.conversations import ConversationManager, ConversationMetadata

    # Create a conversation manager
    manager = ConversationManager()

    # Create a new conversation
    conversation_id = await manager.create_conversation(
        user_id="user-123",
        metadata=ConversationMetadata(
            agent_id="agent-456",
            title="Technical Support",
            tags=["support", "technical"]
        )
    )

    # Add messages to the conversation
    await manager.add_message(
        conversation_id=conversation_id,
        content="How do I reset my password?",
        role="user",
        user_id="user-123"
    )

    # Get conversation messages
    messages = await manager.get_messages(conversation_id)
    ```


.. autolink-examples:: dataflow.persistence.conversations
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.persistence.conversations.ConversationManager
   dataflow.persistence.conversations.ConversationMetadata


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ConversationManager:

   .. graphviz::
      :align: center

      digraph inheritance_ConversationManager {
        node [shape=record];
        "ConversationManager" [label="ConversationManager"];
      }

.. autoclass:: dataflow.persistence.conversations.ConversationManager
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ConversationMetadata:

   .. graphviz::
      :align: center

      digraph inheritance_ConversationMetadata {
        node [shape=record];
        "ConversationMetadata" [label="ConversationMetadata"];
        "pydantic.BaseModel" -> "ConversationMetadata";
      }

.. autopydantic_model:: dataflow.persistence.conversations.ConversationMetadata
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

.. autolink-examples:: dataflow.persistence.conversations
   :collapse:
   
.. autolink-skip:: next
