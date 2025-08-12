
:py:mod:`dataflow.conversations.manager`
========================================

.. py:module:: dataflow.conversations.manager


Classes
-------

.. autoapisummary::

   dataflow.conversations.manager.ConversationManager
   dataflow.conversations.manager.ConversationMetadata


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

.. autoclass:: dataflow.conversations.manager.ConversationManager
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

.. autopydantic_model:: dataflow.conversations.manager.ConversationMetadata
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

.. autolink-examples:: dataflow.conversations.manager
   :collapse:
   
.. autolink-skip:: next
