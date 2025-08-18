"""MCP (Model Context Protocol) integration for haive-dataflow.

This module provides comprehensive MCP server discovery, management, and integration
with the Haive framework through the dataflow registry system.

The module includes:
- MCP server discovery from various sources (npm, pip, GitHub, local)
- Integration with LangChain MCP adapters for tool loading
- Health monitoring and management of MCP servers
- API endpoints for MCP operations
- Registry integration for MCP entities

Examples:
    Basic MCP integration:

            from haive.dataflow.mcp import MCPDiscovery, MCPClient
            from haive.dataflow import registry_system

            # Discover and register MCP servers
            discovery = MCPDiscovery()
            servers = await discovery.discover_all()

            # Initialize MCP client with discovered servers
            client = MCPClient(registry_system)
            await client.initialize_from_registry()

            # Get available tools
            tools = await client.get_available_tools()
"""

from haive.dataflow.mcp.client import MCPClient, MCPToolProvider
from haive.dataflow.mcp.discovery import MCPDiscovery
from haive.dataflow.mcp.health import MCPHealthMonitor

__all__ = [
    "MCPClient",
    "MCPDiscovery",
    "MCPHealthMonitor",
    "MCPToolProvider",
]
