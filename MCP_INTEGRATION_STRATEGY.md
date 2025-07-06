# 🔌 MCP Integration Strategy for Haive-Dataflow

## 📋 Integration Overview

Based on research of the MCP ecosystem, this document outlines the strategy to integrate Model Context Protocol capabilities into the haive-dataflow package, enabling comprehensive MCP server discovery, management, and tool integration.

## 🧰 Key MCP Technologies Identified

### 1. **Official MCP Python SDK** (`mcp` package)

- **Version**: 1.10.1 (latest, June 2025)
- **Purpose**: Official Python SDK for building MCP servers and clients
- **Key Features**:
  - FastMCP server framework
  - Resources, Tools, Prompts support
  - Multiple transports (stdio, SSE, HTTP)
  - Structured output validation
  - Lifecycle management

### 2. **LangChain MCP Adapters** (`langchain-mcp-adapters`)

- **Purpose**: Bridge MCP servers to LangChain/LangGraph ecosystems
- **Key Features**:
  - `MultiServerMCPClient`: Manage multiple MCP server connections
  - `load_mcp_tools()`: Convert MCP tools to LangChain tools
  - `to_fastmcp()`: Convert LangChain tools to FastMCP
  - Support for stdio, HTTP, SSE transports
  - Runtime tool loading

### 3. **FastMCP Integration**

- **Purpose**: High-performance MCP server creation
- **Key Features**:
  - Decorator-based resource/tool definition
  - Automatic type validation
  - ASGI server support
  - Development and production modes

## 🎯 Integration Strategy

### Phase 1: Registry Integration

**Goal**: Add MCP as first-class entity types in haive-dataflow registry

#### 1.1 Extend EntityType Enum

```python
# Add to haive/dataflow/registry/models.py
class EntityType(str, Enum):
    # ... existing types
    MCP_SERVER = "mcp_server"
    MCP_CLIENT = "mcp_client"
    MCP_TOOL = "mcp_tool"
    MCP_RESOURCE = "mcp_resource"
    MCP_PROMPT = "mcp_prompt"
```

#### 1.2 Create MCP-Specific Models

```python
class MCPServerConfig(BaseModel):
    name: str
    transport: MCPTransport  # stdio, sse, http
    command: Optional[str]
    args: List[str] = []
    env: Dict[str, str] = {}
    url: Optional[str]  # For HTTP transport
    capabilities: List[str] = []
    auth_config: Optional[Dict[str, Any]]

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    server_name: str
    schema: Dict[str, Any]

class MCPResourceDefinition(BaseModel):
    name: str
    uri: str
    server_name: str
    mime_type: Optional[str]
```

### Phase 2: MCP Discovery System

**Goal**: Automatically discover and register MCP servers

#### 2.1 MCP Server Discovery

```python
# haive/dataflow/mcp/discovery.py
class MCPServerDiscovery:
    async def discover_npm_servers(self) -> List[MCPServerConfig]
    async def discover_pip_servers(self) -> List[MCPServerConfig]
    async def discover_github_servers(self) -> List[MCPServerConfig]
    async def discover_local_servers(self) -> List[MCPServerConfig]
    async def discover_from_config(self, config_path: Path) -> List[MCPServerConfig]
```

#### 2.2 Integration with Existing Discovery

```python
# Extend haive/dataflow/registry/discovery.py
async def discover_mcp_servers() -> List[RegistryItem]:
    """Discover MCP servers and register them in the dataflow registry."""
    discovery = MCPServerDiscovery()
    servers = await discovery.discover_all()

    registry_items = []
    for server in servers:
        item = RegistryItem(
            name=server.name,
            type=EntityType.MCP_SERVER,
            module_path="haive.mcp.adapters",
            class_name="MCPServerAdapter",
            config=server.dict(),
            # ... other fields
        )
        registry_items.append(item)

    return registry_items
```

### Phase 3: LangGraph Adapter Integration

**Goal**: Use langchain-mcp-adapters for seamless LangGraph integration

#### 3.1 MCP Client Wrapper

```python
# haive/dataflow/mcp/client.py
from langchain_mcp_adapters import MultiServerMCPClient, load_mcp_tools

class HaiveMCPClient:
    def __init__(self, registry_system):
        self.registry = registry_system
        self.mcp_client = None

    async def initialize_from_registry(self):
        """Initialize MCP client with servers from registry."""
        mcp_servers = self.registry.get_entities_by_type(EntityType.MCP_SERVER)

        server_configs = {}
        for server in mcp_servers:
            server_configs[server.name] = server.config

        self.mcp_client = MultiServerMCPClient(server_configs)

    async def get_available_tools(self) -> List[Tool]:
        """Get all tools from connected MCP servers."""
        return await load_mcp_tools(self.mcp_client)
```

#### 3.2 Tool Registration Integration

```python
# haive/dataflow/mcp/tools.py
class MCPToolProvider:
    async def discover_and_register_tools(self):
        """Discover MCP tools and register them in dataflow registry."""
        tools = await self.mcp_client.get_available_tools()

        for tool in tools:
            registry_system.register_entity(
                name=tool.name,
                type=EntityType.MCP_TOOL,
                description=tool.description,
                module_path="haive.mcp.tools",
                class_name="MCPToolWrapper",
                config={
                    "server_name": tool.server_name,
                    "tool_name": tool.name,
                    "schema": tool.schema
                }
            )
```

### Phase 4: API Integration

**Goal**: Expose MCP functionality through dataflow API

#### 4.1 MCP API Routes

```python
# haive/dataflow/api/routes/mcp_routes.py
@router.get("/mcp/servers")
async def list_mcp_servers():
    """List all registered MCP servers."""

@router.post("/mcp/servers/{server_name}/connect")
async def connect_mcp_server(server_name: str):
    """Connect to an MCP server."""

@router.get("/mcp/servers/{server_name}/tools")
async def get_server_tools(server_name: str):
    """Get tools from a specific MCP server."""

@router.post("/mcp/tools/{tool_name}/execute")
async def execute_mcp_tool(tool_name: str, params: Dict[str, Any]):
    """Execute an MCP tool."""
```

#### 4.2 WebSocket Support for MCP

```python
# haive/dataflow/api/mcp_websocket.py
class MCPWebSocketManager:
    async def handle_mcp_tool_execution(self, websocket, tool_name, params):
        """Handle real-time MCP tool execution via WebSocket."""
```

### Phase 5: Advanced Features

**Goal**: Add advanced MCP capabilities

#### 5.1 MCP Server Health Monitoring

```python
class MCPHealthMonitor:
    async def check_server_health(self, server_name: str) -> bool
    async def reconnect_failed_servers(self)
    async def monitor_server_performance(self)
```

#### 5.2 MCP Resource Management

```python
class MCPResourceManager:
    async def discover_resources(self, server_name: str) -> List[MCPResource]
    async def cache_resources(self, resource_uri: str) -> bytes
    async def get_resource_metadata(self, resource_uri: str) -> Dict[str, Any]
```

#### 5.3 MCP Prompt Management

```python
class MCPPromptManager:
    async def discover_prompts(self, server_name: str) -> List[MCPPrompt]
    async def execute_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> str
    async def register_prompt_templates(self)
```

## 🔗 Integration with Existing haive-mcp Package

The haive-dataflow MCP integration will leverage and extend the existing haive-mcp package:

### Shared Components

1. **Server Configurations**: Use the 941 downloaded servers from haive-mcp
2. **Installation Management**: Leverage the installer system
3. **Agent Integration**: Connect with MCPAgent classes

### Enhanced Capabilities

1. **Registry Management**: Full registry support for MCP components
2. **API Exposure**: REST and WebSocket APIs for MCP operations
3. **Discovery Automation**: Automatic background discovery and registration
4. **Health Monitoring**: Server health and performance tracking
5. **Resource Management**: Advanced resource and prompt handling

## 📦 Dependencies to Add

```toml
# Add to pyproject.toml
[tool.poetry.dependencies]
mcp = "^1.10.1"  # Official MCP SDK
langchain-mcp-adapters = "^0.1.0"  # LangChain integration
haive-mcp = { path = "../haive-mcp", develop = true }  # Our MCP package
```

## 🚀 Implementation Order

1. ✅ **Research Phase** - Complete
2. 🔄 **Registry Models** - Add MCP entity types and models
3. 🔄 **Discovery Integration** - MCP server discovery in dataflow
4. 🔄 **Client Wrapper** - LangGraph adapter integration
5. 🔄 **API Routes** - REST endpoints for MCP operations
6. 🔄 **Advanced Features** - Health monitoring, resources, prompts

## 🎯 Expected Outcomes

After implementation, haive-dataflow will provide:

1. **Unified MCP Management**: All 941+ MCP servers discoverable and manageable through dataflow registry
2. **Seamless LangGraph Integration**: MCP tools automatically available in LangGraph workflows
3. **REST API Access**: Full API for MCP server and tool management
4. **Real-time Operations**: WebSocket support for live MCP tool execution
5. **Enterprise Features**: Health monitoring, caching, and performance tracking

This integration positions Haive as a comprehensive platform for MCP-powered AI applications with enterprise-grade management capabilities.
