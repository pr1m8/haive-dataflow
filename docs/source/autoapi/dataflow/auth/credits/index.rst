
:py:mod:`dataflow.auth.credits`
===============================

.. py:module:: dataflow.auth.credits


Classes
-------

.. autoapisummary::

   dataflow.auth.credits.CreditsManager
   dataflow.auth.credits.UsageRecord


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for CreditsManager:

   .. graphviz::
      :align: center

      digraph inheritance_CreditsManager {
        node [shape=record];
        "CreditsManager" [label="CreditsManager"];
      }

.. autoclass:: dataflow.auth.credits.CreditsManager
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for UsageRecord:

   .. graphviz::
      :align: center

      digraph inheritance_UsageRecord {
        node [shape=record];
        "UsageRecord" [label="UsageRecord"];
        "pydantic.BaseModel" -> "UsageRecord";
      }

.. autopydantic_model:: dataflow.auth.credits.UsageRecord
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

.. autolink-examples:: dataflow.auth.credits
   :collapse:
   
.. autolink-skip:: next
