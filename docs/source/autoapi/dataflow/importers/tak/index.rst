
:py:mod:`dataflow.importers.tak`
================================

.. py:module:: dataflow.importers.tak

Hybrid Tools and Toolkits Importer.

This script first identifies tools using your working approach, then
imports them to the database.


.. autolink-examples:: dataflow.importers.tak
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.importers.tak.determine_category_from_module_path
   dataflow.importers.tak.get_or_create_category
   dataflow.importers.tak.get_or_create_tool
   dataflow.importers.tak.get_or_create_toolkit
   dataflow.importers.tak.import_tools_to_database
   dataflow.importers.tak.link_tool_to_toolkit
   dataflow.importers.tak.load_tools_from_directory
   dataflow.importers.tak.load_tools_from_module
   dataflow.importers.tak.main
   dataflow.importers.tak.print_tool_stats

.. py:function:: determine_category_from_module_path(module_path: str) -> str

   Determine a category name from a module path.


   .. autolink-examples:: determine_category_from_module_path
      :collapse:

.. py:function:: get_or_create_category(name: str, display_name: str | None = None) -> str

   Get or create a tool category.


   .. autolink-examples:: get_or_create_category
      :collapse:

.. py:function:: get_or_create_tool(name: str, category_id: str, display_name: str | None = None, description: str | None = None) -> str

   Get or create a tool.


   .. autolink-examples:: get_or_create_tool
      :collapse:

.. py:function:: get_or_create_toolkit(name: str, display_name: str | None = None, description: str | None = None) -> str

   Get or create a toolkit.


   .. autolink-examples:: get_or_create_toolkit
      :collapse:

.. py:function:: import_tools_to_database()

   Import the discovered tools into the database.


   .. autolink-examples:: import_tools_to_database
      :collapse:

.. py:function:: link_tool_to_toolkit(tool_id: str, toolkit_id: str) -> bool

   Link a tool to a toolkit.


   .. autolink-examples:: link_tool_to_toolkit
      :collapse:

.. py:function:: load_tools_from_directory(directory: str, module_prefix: str, tool_type: str) -> list[langchain_core.tools.BaseTool]

   Load tools from a directory using your working approach.


   .. autolink-examples:: load_tools_from_directory
      :collapse:

.. py:function:: load_tools_from_module(module_path: str, tool_type: str) -> list[langchain_core.tools.BaseTool]

   Load tools from a module using your working approach.


   .. autolink-examples:: load_tools_from_module
      :collapse:

.. py:function:: main()

   Main function to run the tool importer.


   .. autolink-examples:: main
      :collapse:

.. py:function:: print_tool_stats()

   Print statistics about discovered tools.


   .. autolink-examples:: print_tool_stats
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.importers.tak
   :collapse:
   
.. autolink-skip:: next
