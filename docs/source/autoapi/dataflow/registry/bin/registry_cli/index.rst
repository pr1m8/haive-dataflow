
:py:mod:`dataflow.registry.bin.registry_cli`
============================================

.. py:module:: dataflow.registry.bin.registry_cli

Haive Registry CLI.

This script provides a command-line interface for the Haive registry system.
It allows users to:
- Discover and register components (agents, tools, engines, games, etc.)
- View registry statistics
- Import LLM models
- Search for components
- View detailed information about components

Usage:
    python registry_cli.py discover all
    python registry_cli.py discover agents
    python registry_cli.py import llm-models
    python registry_cli.py stats
    python registry_cli.py search [type] [term]
    python registry_cli.py show [id]


.. autolink-examples:: dataflow.registry.bin.registry_cli
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.registry.bin.registry_cli.format_json
   dataflow.registry.bin.registry_cli.handle_clear
   dataflow.registry.bin.registry_cli.handle_discover
   dataflow.registry.bin.registry_cli.handle_import
   dataflow.registry.bin.registry_cli.handle_list
   dataflow.registry.bin.registry_cli.handle_search
   dataflow.registry.bin.registry_cli.handle_show
   dataflow.registry.bin.registry_cli.handle_stats
   dataflow.registry.bin.registry_cli.main
   dataflow.registry.bin.registry_cli.print_header
   dataflow.registry.bin.registry_cli.print_rich
   dataflow.registry.bin.registry_cli.print_subheader
   dataflow.registry.bin.registry_cli.print_table
   dataflow.registry.bin.registry_cli.setup_parser

.. py:function:: format_json(data)

   Format JSON data for display.


   .. autolink-examples:: format_json
      :collapse:

.. py:function:: handle_clear(args)

   Handle the clear command.


   .. autolink-examples:: handle_clear
      :collapse:

.. py:function:: handle_discover(args)

   Handle the discover command.


   .. autolink-examples:: handle_discover
      :collapse:

.. py:function:: handle_import(args)

   Handle the import command.


   .. autolink-examples:: handle_import
      :collapse:

.. py:function:: handle_list(args)

   Handle the list command.


   .. autolink-examples:: handle_list
      :collapse:

.. py:function:: handle_search(args)

   Handle the search command.


   .. autolink-examples:: handle_search
      :collapse:

.. py:function:: handle_show(args)

   Handle the show command.


   .. autolink-examples:: handle_show
      :collapse:

.. py:function:: handle_stats(args)

   Handle the stats command.


   .. autolink-examples:: handle_stats
      :collapse:

.. py:function:: main()

   Main function.


   .. autolink-examples:: main
      :collapse:

.. py:function:: print_header(title, style='bold blue')

   Print a header with rich formatting if available.


   .. autolink-examples:: print_header
      :collapse:

.. py:function:: print_rich(message, style='', highlight=False, markup=True)

   Print with rich formatting if available, otherwise use regular print.


   .. autolink-examples:: print_rich
      :collapse:

.. py:function:: print_subheader(title, style='bold cyan')

   Print a subheader with rich formatting if available.


   .. autolink-examples:: print_subheader
      :collapse:

.. py:function:: print_table(headers, rows, title=None)

   Print a table with rich formatting if available.


   .. autolink-examples:: print_table
      :collapse:

.. py:function:: setup_parser() -> argparse.ArgumentParser

   Set up command-line argument parser.


   .. autolink-examples:: setup_parser
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.registry.bin.registry_cli
   :collapse:
   
.. autolink-skip:: next
