"""MCP Server Discovery for haive-dataflow.

This module provides discovery capabilities for MCP (Model Context Protocol) servers
from various sources and integrates them with the haive-dataflow registry system.

The discovery system can find MCP servers from:
- npm packages (@modelcontextprotocol/*)
- PyPI packages (mcp-*)
- GitHub repositories
- Local configurations
- Existing haive-mcp downloaded servers

Classes:
    MCPDiscovery: Main discovery engine for MCP servers

Functions:
    discover_mcp_servers: Discover and register MCP servers in dataflow registry
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .registry.models import (
    EntityType,
    MCPPromptDefinition,
    MCPResourceDefinition,
    MCPServerConfig,
    MCPToolDefinition,
    MCPTransport,
    RegistryItem,
)

logger = logging.getLogger(__name__)


class MCPDiscovery:
    """Discovery engine for MCP servers.

    This class provides comprehensive discovery of MCP servers from various sources
    and creates appropriate registry entries for integration with haive-dataflow.

    Attributes:
        registry_system: Reference to the dataflow registry system
        discovered_servers: Cache of discovered server configurations

    Example:
        Basic usage:

        ```python
        discovery = MCPDiscovery()
        servers = await discovery.discover_all()

        # Register with dataflow registry
        await discovery.register_with_dataflow()
        ```
    """

    def __init__(self, registry_system=None):
        """Initialize MCP discovery.

        Args:
            registry_system: Optional registry system instance
        """
        self.registry_system = registry_system
        self.discovered_servers: List[MCPServerConfig] = []
        self.discovered_tools: List[MCPToolDefinition] = []
        self.discovered_resources: List[MCPResourceDefinition] = []
        self.discovered_prompts: List[MCPPromptDefinition] = []

    async def discover_all(self) -> List[MCPServerConfig]:
        """Discover MCP servers from all available sources.

        Returns:
            List of discovered MCP server configurations
        """
        logger.info("Starting comprehensive MCP server discovery")

        all_servers = []

        # Discover from different sources
        npm_servers = await self.discover_npm_servers()
        all_servers.extend(npm_servers)
        logger.info(f"Discovered {len(npm_servers)} npm MCP servers")

        pip_servers = await self.discover_pip_servers()
        all_servers.extend(pip_servers)
        logger.info(f"Discovered {len(pip_servers)} pip MCP servers")

        local_servers = await self.discover_local_servers()
        all_servers.extend(local_servers)
        logger.info(f"Discovered {len(local_servers)} local MCP servers")

        haive_mcp_servers = await self.discover_from_haive_mcp()
        all_servers.extend(haive_mcp_servers)
        logger.info(f"Discovered {len(haive_mcp_servers)} haive-mcp servers")

        # Remove duplicates based on name
        unique_servers = {}
        for server in all_servers:
            if server.name not in unique_servers:
                unique_servers[server.name] = server

        self.discovered_servers = list(unique_servers.values())
        logger.info(
            f"Total unique MCP servers discovered: {len(self.discovered_servers)}"
        )

        return self.discovered_servers

    async def discover_npm_servers(self) -> List[MCPServerConfig]:
        """Discover MCP servers from npm packages.

        Returns:
            List of npm-based MCP server configurations
        """
        logger.info("Discovering npm MCP servers")
        servers = []

        # Well-known official MCP servers
        official_servers = [
            {
                "name": "filesystem",
                "package": "@modelcontextprotocol/server-filesystem",
                "capabilities": ["file_read", "file_write", "directory_list"],
                "description": "Local filesystem operations",
            },
            {
                "name": "github",
                "package": "@modelcontextprotocol/server-github",
                "capabilities": ["repo_access", "issue_management", "pr_operations"],
                "description": "GitHub repository operations",
            },
            {
                "name": "sqlite",
                "package": "@modelcontextprotocol/server-sqlite",
                "capabilities": ["database_query", "sql_execution"],
                "description": "SQLite database operations",
            },
            {
                "name": "postgres",
                "package": "@modelcontextprotocol/server-postgres",
                "capabilities": ["database_query", "sql_execution"],
                "description": "PostgreSQL database operations",
            },
            {
                "name": "fetch",
                "package": "@modelcontextprotocol/server-fetch",
                "capabilities": ["http_request", "web_scraping"],
                "description": "HTTP fetch and web scraping",
            },
            {
                "name": "time",
                "package": "@modelcontextprotocol/server-time",
                "capabilities": ["time_queries", "date_operations"],
                "description": "Time and date utilities",
            },
        ]

        for server_info in official_servers:
            # Check if package is available
            if await self._check_npm_package_available(server_info["package"]):
                config = MCPServerConfig(
                    name=server_info["name"],
                    transport=MCPTransport.STDIO,
                    command="npx",
                    args=["-y", server_info["package"]],
                    capabilities=server_info["capabilities"],
                )
                servers.append(config)

        return servers

    async def discover_pip_servers(self) -> List[MCPServerConfig]:
        """Discover MCP servers from pip packages.

        Returns:
            List of pip-based MCP server configurations
        """
        logger.info("Discovering pip MCP servers")
        servers = []

        # Search for MCP-related packages
        try:
            result = await asyncio.create_subprocess_exec(
                "pip",
                "search",
                "mcp",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                # Parse pip search results (this would need more sophisticated parsing)
                # For now, we'll add known pip MCP packages
                known_pip_servers = [
                    {
                        "name": "fastmcp-demo",
                        "package": "fastmcp",
                        "capabilities": ["demo_tools"],
                        "description": "FastMCP demonstration server",
                    }
                ]

                for server_info in known_pip_servers:
                    if await self._check_pip_package_available(server_info["package"]):
                        config = MCPServerConfig(
                            name=server_info["name"],
                            transport=MCPTransport.STDIO,
                            command="python",
                            args=["-m", server_info["package"]],
                            capabilities=server_info["capabilities"],
                        )
                        servers.append(config)

        except Exception as e:
            logger.warning(f"Failed to search pip packages: {e}")

        return servers

    async def discover_local_servers(self) -> List[MCPServerConfig]:
        """Discover locally configured MCP servers.

        Returns:
            List of locally configured MCP server configurations
        """
        logger.info("Discovering local MCP servers")
        servers = []

        # Common local configuration paths
        config_paths = [
            Path.home() / ".mcp" / "servers.json",
            Path.cwd() / "mcp_servers.json",
            Path.cwd() / "configs" / "mcp_servers.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)

                    # Parse different configuration formats
                    servers.extend(await self._parse_mcp_config(config_data))
                    logger.info(f"Loaded local configuration from {config_path}")

                except Exception as e:
                    logger.warning(f"Failed to load local config {config_path}: {e}")

        return servers

    async def discover_from_haive_mcp(self) -> List[MCPServerConfig]:
        """Discover servers from the haive-mcp package data.

        This integrates with the existing haive-mcp package to load the 941
        downloaded servers into the dataflow registry.

        Returns:
            List of MCP server configurations from haive-mcp
        """
        logger.info("Discovering servers from haive-mcp package")
        servers = []

        # Look for haive-mcp downloaded servers
        mcp_config_paths = [
            # Relative path from haive-dataflow to haive-mcp
            Path(__file__).parent.parent.parent.parent
            / "haive-mcp"
            / "downloads"
            / "mcp_servers_config.json",
            # Absolute path patterns
            Path.cwd()
            / "packages"
            / "haive-mcp"
            / "downloads"
            / "mcp_servers_config.json",
        ]

        for config_path in mcp_config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)

                    mcp_servers = config_data.get("mcpServers", {})
                    logger.info(f"Found {len(mcp_servers)} servers in haive-mcp config")

                    for server_name, server_config in mcp_servers.items():
                        # Convert haive-mcp format to dataflow format
                        config = MCPServerConfig(
                            name=server_name,
                            transport=MCPTransport.STDIO,
                            command=server_config.get("command", "npx").split()[0],
                            args=(
                                server_config.get("command", "npx").split()[1:]
                                if len(server_config.get("command", "npx").split()) > 1
                                else []
                            ),
                            env=server_config.get("env", {}),
                            capabilities=server_config.get("capabilities", []),
                        )
                        servers.append(config)

                    logger.info(
                        f"Successfully imported {len(servers)} servers from haive-mcp"
                    )
                    break  # Use first found config

                except Exception as e:
                    logger.warning(
                        f"Failed to load haive-mcp config {config_path}: {e}"
                    )

        return servers

    async def register_with_dataflow(self) -> List[str]:
        """Register discovered MCP servers with the dataflow registry.

        Returns:
            List of registry IDs for registered servers
        """
        if not self.registry_system:
            logger.error("No registry system available for registration")
            return []

        registered_ids = []

        for server in self.discovered_servers:
            try:
                # Register the MCP server
                server_id = self.registry_system.register_entity(
                    name=server.name,
                    type=EntityType.MCP_SERVER,
                    description=f"MCP server: {server.name}",
                    module_path="haive.dataflow.mcp.client",
                    class_name="MCPServerAdapter",
                    config=server.dict(),
                    tags=["mcp", "server"] + server.capabilities,
                )
                registered_ids.append(server_id)
                logger.info(f"Registered MCP server: {server.name} -> {server_id}")

            except Exception as e:
                logger.error(f"Failed to register MCP server {server.name}: {e}")

        logger.info(
            f"Registered {len(registered_ids)} MCP servers with dataflow registry"
        )
        return registered_ids

    async def _check_npm_package_available(self, package: str) -> bool:
        """Check if an npm package is available.

        Args:
            package: Package name to check

        Returns:
            True if package is available, False otherwise
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "npm",
                "view",
                package,
                "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0
        except Exception:
            return False

    async def _check_pip_package_available(self, package: str) -> bool:
        """Check if a pip package is available.

        Args:
            package: Package name to check

        Returns:
            True if package is available, False otherwise
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "pip",
                "show",
                package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0
        except Exception:
            return False

    async def _parse_mcp_config(self, config_data: Dict) -> List[MCPServerConfig]:
        """Parse MCP configuration data into server configs.

        Args:
            config_data: Raw configuration data

        Returns:
            List of parsed MCP server configurations
        """
        servers = []

        # Handle different configuration formats
        if "mcpServers" in config_data:
            # Standard MCP configuration format
            for name, config in config_data["mcpServers"].items():
                try:
                    server_config = MCPServerConfig(
                        name=name,
                        transport=MCPTransport(config.get("transport", "stdio")),
                        command=config.get("command"),
                        args=config.get("args", []),
                        env=config.get("env", {}),
                        url=config.get("url"),
                        capabilities=config.get("capabilities", []),
                    )
                    servers.append(server_config)
                except Exception as e:
                    logger.warning(f"Failed to parse server config for {name}: {e}")

        elif "servers" in config_data:
            # Alternative configuration format
            for server_data in config_data["servers"]:
                try:
                    server_config = MCPServerConfig(**server_data)
                    servers.append(server_config)
                except Exception as e:
                    logger.warning(f"Failed to parse server config: {e}")

        return servers


async def discover_mcp_servers(registry_system=None) -> List[RegistryItem]:
    """Discover MCP servers and create registry items.

    This function provides a simple interface for discovering MCP servers
    and creating appropriate registry items for the dataflow system.

    Args:
        registry_system: Optional registry system for registration

    Returns:
        List of RegistryItem objects for discovered MCP servers

    Example:
        ```python
        from haive.dataflow.mcp.discovery import discover_mcp_servers
        from haive.dataflow import registry_system

        # Discover and register MCP servers
        registry_items = await discover_mcp_servers(registry_system)
        print(f"Discovered {len(registry_items)} MCP servers")
        ```
    """
    discovery = MCPDiscovery(registry_system)
    servers = await discovery.discover_all()

    registry_items = []
    for server in servers:
        item = RegistryItem(
            name=server.name,
            type=EntityType.MCP_SERVER,
            description=f"MCP server providing {', '.join(server.capabilities) if server.capabilities else 'various capabilities'}",
            module_path="haive.dataflow.mcp.client",
            class_name="MCPServerAdapter",
            config=server.dict(),
            tags=["mcp", "server"] + server.capabilities,
        )
        registry_items.append(item)

    return registry_items
