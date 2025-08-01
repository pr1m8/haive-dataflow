"""MCP Client Integration for haive-dataflow.

This module provides integration between MCP servers and the Haive framework
through LangChain MCP adapters and the dataflow registry system.

The client handles:
- Connection management to multiple MCP servers
- Tool loading and registration from MCP servers
- Integration with LangGraph workflows
- Health monitoring and error handling

Classes:
    MCPClient: Main client for MCP server integration
    MCPToolProvider: Provider for MCP tools in the registry
    MCPServerAdapter: Adapter for individual MCP servers
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools

from haive.dataflow.mcp.registry.models import (
    EntityType,
    MCPServerConfig,
    MCPServerHealth,
    MCPToolDefinition,
)

logger = logging.getLogger(__name__)

try:
    # Import LangChain MCP adapters if available

    LANGCHAIN_MCP_AVAILABLE = True
except ImportError:
    logger.warning(
        "langchain-mcp-adapters not available. Install with: pip install langchain-mcp-adapters"
    )
    LANGCHAIN_MCP_AVAILABLE = False

try:
    # Import official MCP SDK if available

    MCP_SDK_AVAILABLE = True
except ImportError:
    logger.warning("Official MCP SDK not available. Install with: pip install mcp")
    MCP_SDK_AVAILABLE = False


class MCPClient:
    """Client for managing MCP server connections and tools.

    This class provides a high-level interface for connecting to MCP servers,
    loading tools, and integrating with the Haive dataflow registry system.

    Attributes:
        registry_system: Reference to the dataflow registry
        mcp_client: Underlying MultiServerMCPClient instance
        connected_servers: Dictionary of connected server configurations
        available_tools: Cache of available tools from all servers

    Example:
        Basic usage:

        ```python
        from haive.dataflow.mcp import MCPClient
        from haive.dataflow import registry_system

        client = MCPClient(registry_system)
        await client.initialize_from_registry()

        # Get available tools
        tools = await client.get_available_tools()

        # Execute a tool
        result = await client.execute_tool("read_file", {"path": "/path/to/file"})
        ```
    """

    def __init__(self, registry_system=None):
        """Initialize MCP client.

        Args:
            registry_system: Optional registry system instance
        """
        self.registry_system = registry_system
        self.mcp_client: Any | None = None
        self.connected_servers: dict[str, MCPServerConfig] = {}
        self.available_tools: list[MCPToolDefinition] = []
        self.server_health: dict[str, MCPServerHealth] = {}

        if not LANGCHAIN_MCP_AVAILABLE:
            logger.error(
                "LangChain MCP adapters not available. Cannot initialize MCP client."
            )

    async def initialize_from_registry(self) -> bool:
        """Initialize MCP client with servers from the registry.

        Returns:
            True if initialization successful, False otherwise
        """
        if not LANGCHAIN_MCP_AVAILABLE:
            logger.error("Cannot initialize: LangChain MCP adapters not available")
            return False

        if not self.registry_system:
            logger.error("No registry system available for initialization")
            return False

        try:
            # Get MCP servers from registry
            mcp_servers = self.registry_system.get_entities_by_type(
                EntityType.MCP_SERVER
            )
            logger.info(f"Found {len(mcp_servers)} MCP servers in registry")

            if not mcp_servers:
                logger.warning("No MCP servers found in registry")
                return False

            # Convert registry items to server configurations
            server_configs = {}
            for server_item in mcp_servers:
                config = MCPServerConfig(**server_item.config)
                server_configs[config.name] = self._convert_to_langchain_config(config)
                self.connected_servers[config.name] = config

            # Initialize MultiServerMCPClient
            self.mcp_client = MultiServerMCPClient(server_configs)
            logger.info(f"Initialized MCP client with {len(server_configs)} servers")

            # Load available tools
            await self._load_available_tools()

            return True

        except Exception as e:
            logger.exception(f"Failed to initialize MCP client from registry: {e}")
            return False

    async def connect_to_servers(
        self, server_configs: dict[str, MCPServerConfig]
    ) -> bool:
        """Connect to specific MCP servers.

        Args:
            server_configs: Dictionary of server name to configuration

        Returns:
            True if connection successful, False otherwise
        """
        if not LANGCHAIN_MCP_AVAILABLE:
            logger.error("Cannot connect: LangChain MCP adapters not available")
            return False

        try:
            # Convert to LangChain format
            langchain_configs = {}
            for name, config in server_configs.items():
                langchain_configs[name] = self._convert_to_langchain_config(config)
                self.connected_servers[name] = config

            # Initialize client
            self.mcp_client = MultiServerMCPClient(langchain_configs)
            logger.info(f"Connected to {len(langchain_configs)} MCP servers")

            # Load tools
            await self._load_available_tools()

            return True

        except Exception as e:
            logger.exception(f"Failed to connect to MCP servers: {e}")
            return False

    async def get_available_tools(self) -> list[Any]:
        """Get all available tools from connected MCP servers.

        Returns:
            List of LangChain Tool objects
        """
        if not self.mcp_client:
            logger.error("MCP client not initialized")
            return []

        try:
            tools = await load_mcp_tools(self.mcp_client)
            logger.info(f"Loaded {len(tools)} tools from MCP servers")
            return tools

        except Exception as e:
            logger.exception(f"Failed to load MCP tools: {e}")
            return []

    async def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """Execute a specific MCP tool.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        tools = await self.get_available_tools()

        # Find the tool
        target_tool = None
        for tool in tools:
            if tool.name == tool_name:
                target_tool = tool
                break

        if not target_tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        try:
            result = await target_tool.arun(**parameters)
            logger.info(f"Successfully executed tool '{tool_name}'")
            return result

        except Exception as e:
            logger.exception(f"Failed to execute tool '{tool_name}': {e}")
            raise

    async def check_server_health(self, server_name: str) -> MCPServerHealth:
        """Check health of a specific MCP server.

        Args:
            server_name: Name of the server to check

        Returns:
            Server health information
        """
        start_time = datetime.now()

        try:
            # Try to get tools from the server (simple health check)
            tools = await self.get_available_tools()
            server_tools = [
                tool
                for tool in tools
                if hasattr(tool, "server_name") and tool.server_name == server_name
            ]

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            health = MCPServerHealth(
                server_name=server_name,
                is_healthy=True,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_count=0,
                capabilities_available=[tool.name for tool in server_tools],
            )

            self.server_health[server_name] = health
            return health

        except Exception as e:
            health = MCPServerHealth(
                server_name=server_name,
                is_healthy=False,
                last_check=datetime.now(),
                error_count=1,
                error_details=str(e),
                capabilities_available=[],
            )

            self.server_health[server_name] = health
            return health

    async def get_server_health_status(self) -> dict[str, MCPServerHealth]:
        """Get health status for all connected servers.

        Returns:
            Dictionary of server name to health status
        """
        health_tasks = []
        for server_name in self.connected_servers:
            task = self.check_server_health(server_name)
            health_tasks.append(task)

        if health_tasks:
            await asyncio.gather(*health_tasks, return_exceptions=True)

        return self.server_health

    def _convert_to_langchain_config(self, config: MCPServerConfig) -> dict[str, Any]:
        """Convert MCPServerConfig to LangChain MCP adapter format.

        Args:
            config: MCP server configuration

        Returns:
            Configuration dictionary for LangChain MCP adapter
        """
        langchain_config = {
            "transport": config.transport.value,
        }

        if config.transport.value == "stdio":
            if config.command:
                langchain_config["command"] = config.command
                if config.args:
                    langchain_config["args"] = config.args
        elif config.transport.value in ["http", "sse"] and config.url:
            langchain_config["url"] = config.url

        if config.env:
            langchain_config["env"] = config.env

        return langchain_config

    async def _load_available_tools(self):
        """Load and cache available tools from all servers."""
        try:
            tools = await self.get_available_tools()

            # Convert to MCPToolDefinition objects
            self.available_tools = []
            for tool in tools:
                # Extract server name from tool metadata if available
                server_name = getattr(tool, "server_name", "unknown")

                tool_def = MCPToolDefinition(
                    name=tool.name,
                    description=tool.description,
                    server_name=server_name,
                    schema=(
                        getattr(tool, "args_schema", {}).schema()
                        if hasattr(tool, "args_schema")
                        else {}
                    ),
                    tags=getattr(tool, "tags", []),
                )
                self.available_tools.append(tool_def)

            logger.info(f"Cached {len(self.available_tools)} tool definitions")

        except Exception as e:
            logger.exception(f"Failed to load available tools: {e}")


class MCPToolProvider:
    """Provider for registering MCP tools in the dataflow registry.

    This class handles the discovery and registration of tools from MCP
    servers into the Haive dataflow registry system for broader
    discovery and use.
    """

    def __init__(self, mcp_client: MCPClient, registry_system=None):
        """Initialize MCP tool provider.

        Args:
            mcp_client: MCP client instance
            registry_system: Registry system for tool registration
        """
        self.mcp_client = mcp_client
        self.registry_system = registry_system

    async def discover_and_register_tools(self) -> list[str]:
        """Discover MCP tools and register them in the dataflow registry.

        Returns:
            List of registry IDs for registered tools
        """
        if not self.registry_system:
            logger.error("No registry system available for tool registration")
            return []

        registered_ids = []

        try:
            tools = await self.mcp_client.get_available_tools()

            for tool in tools:
                # Create registry entry for the tool
                tool_id = self.registry_system.register_entity(
                    name=tool.name,
                    type=EntityType.MCP_TOOL,
                    description=tool.description,
                    module_path="haive.dataflow.mcp.client",
                    class_name="MCPToolWrapper",
                    config={
                        "server_name": getattr(tool, "server_name", "unknown"),
                        "tool_name": tool.name,
                        "schema": (
                            getattr(tool, "args_schema", {}).schema()
                            if hasattr(tool, "args_schema")
                            else {}
                        ),
                    },
                    tags=["mcp", "tool", *getattr(tool, "tags", [])],
                )
                registered_ids.append(tool_id)
                logger.info(f"Registered MCP tool: {tool.name} -> {tool_id}")

            logger.info(
                f"Registered {len(registered_ids)} MCP tools with dataflow registry"
            )

        except Exception as e:
            logger.exception(f"Failed to discover and register MCP tools: {e}")

        return registered_ids


class MCPServerAdapter:
    """Adapter for individual MCP servers.

    This class provides a consistent interface for working with
    individual MCP servers, handling connection, tool execution, and
    health monitoring.
    """

    def __init__(self, config: MCPServerConfig):
        """Initialize MCP server adapter.

        Args:
            config: Server configuration
        """
        self.config = config
        self.is_connected = False
        self.last_health_check: datetime | None = None
        self.health_status: MCPServerHealth | None = None

    async def connect(self) -> bool:
        """Connect to the MCP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Implementation would depend on the specific server type
            # For now, we'll simulate a connection
            self.is_connected = True
            logger.info(f"Connected to MCP server: {self.config.name}")
            return True

        except Exception as e:
            logger.exception(f"Failed to connect to MCP server {self.config.name}: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the MCP server."""
        self.is_connected = False
        logger.info(f"Disconnected from MCP server: {self.config.name}")

    async def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """Execute a tool on this server.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        if not self.is_connected:
            raise RuntimeError(f"Server {self.config.name} is not connected")

        # Implementation would execute the actual tool
        # For now, return a placeholder
        return f"Tool {tool_name} executed on server {
            self.config.name} with parameters: {parameters}"

    async def get_available_tools(self) -> list[str]:
        """Get list of available tools on this server.

        Returns:
            List of tool names
        """
        if not self.is_connected:
            return []

        # Implementation would query the server for available tools
        # For now, return capabilities as tools
        return self.config.capabilities

    def get_health_status(self) -> MCPServerHealth:
        """Get current health status.

        Returns:
            Current health status
        """
        if self.health_status:
            return self.health_status

        return MCPServerHealth(
            server_name=self.config.name,
            is_healthy=self.is_connected,
            last_check=datetime.now(),
            capabilities_available=(
                self.config.capabilities if self.is_connected else []
            ),
        )
