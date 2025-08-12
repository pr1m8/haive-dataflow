
:py:mod:`dataflow.api.routes.example_tool`
==========================================

.. py:module:: dataflow.api.routes.example_tool

Example tool for testing the tools API.


.. autolink-examples:: dataflow.api.routes.example_tool
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.example_tool.CalculatorInput
   dataflow.api.routes.example_tool.CalculatorTool
   dataflow.api.routes.example_tool.SearchToolInput


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for CalculatorInput:

   .. graphviz::
      :align: center

      digraph inheritance_CalculatorInput {
        node [shape=record];
        "CalculatorInput" [label="CalculatorInput"];
        "pydantic.BaseModel" -> "CalculatorInput";
      }

.. autopydantic_model:: dataflow.api.routes.example_tool.CalculatorInput
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





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for CalculatorTool:

   .. graphviz::
      :align: center

      digraph inheritance_CalculatorTool {
        node [shape=record];
        "CalculatorTool" [label="CalculatorTool"];
      }

.. autoclass:: dataflow.api.routes.example_tool.CalculatorTool
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SearchToolInput:

   .. graphviz::
      :align: center

      digraph inheritance_SearchToolInput {
        node [shape=record];
        "SearchToolInput" [label="SearchToolInput"];
        "pydantic.BaseModel" -> "SearchToolInput";
      }

.. autopydantic_model:: dataflow.api.routes.example_tool.SearchToolInput
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



Functions
---------

.. autoapisummary::

   dataflow.api.routes.example_tool.simple_search

.. py:function:: simple_search(query: str, max_results: int = 10) -> list[str]

   Simple search function for testing.

   :param query: Search query string
   :param max_results: Maximum number of results to return

   :returns: List of mock search results


   .. autolink-examples:: simple_search
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.example_tool
   :collapse:
   
.. autolink-skip:: next
