
:py:mod:`dataflow.mcp.health`
=============================

.. py:module:: dataflow.mcp.health

MCP Health Monitoring for haive-dataflow.

This module provides health monitoring and management capabilities for MCP servers,
including connection status tracking, performance metrics, and automatic recovery.

Classes:
    MCPHealthMonitor: Main health monitoring service
    MCPHealthChecker: Individual server health checker


.. autolink-examples:: dataflow.mcp.health
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.mcp.health.MCPHealthChecker
   dataflow.mcp.health.MCPHealthMonitor


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPHealthChecker:

   .. graphviz::
      :align: center

      digraph inheritance_MCPHealthChecker {
        node [shape=record];
        "MCPHealthChecker" [label="MCPHealthChecker"];
      }

.. autoclass:: dataflow.mcp.health.MCPHealthChecker
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for MCPHealthMonitor:

   .. graphviz::
      :align: center

      digraph inheritance_MCPHealthMonitor {
        node [shape=record];
        "MCPHealthMonitor" [label="MCPHealthMonitor"];
      }

.. autoclass:: dataflow.mcp.health.MCPHealthMonitor
   :members:
   :undoc-members:
   :show-inheritance:




.. rubric:: Related Links

.. autolink-examples:: dataflow.mcp.health
   :collapse:
   
.. autolink-skip:: next
