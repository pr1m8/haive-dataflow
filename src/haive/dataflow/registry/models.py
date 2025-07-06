"""Models for the Haive Registry System.

This module defines the core data models used by the registry system to represent
different types of entities, configurations, dependencies, and other components.
These models provide a structured way to store and retrieve information about
various components in the Haive ecosystem.

The models use Pydantic for validation, serialization, and deserialization,
ensuring type safety and consistent data structures throughout the system.

Classes:
    EntityType: Enumeration of entity types that can be registered
    ConfigType: Enumeration of configuration types for registry items
    DependencyType: Enumeration of dependency relationships between entities
    ImportStatus: Enumeration of import operation status values
    RegistryItem: Base model for all registry entries
    Configuration: Model for configuration data associated with registry items
    GraphDefinition: Model for graph structure definitions (nodes and edges)
    Dependency: Model for dependency relationships between registry items
    EnvironmentVar: Model for environment variable requirements
    ImportLogItem: Model for logging import operations

Example:
    Creating registry models:

    >>> from haive.dataflow.registry.models import RegistryItem, EntityType
    >>> from datetime import datetime
    >>>
    >>> # Create a new registry item
    >>> item = RegistryItem(
    ...     name="TextClassifier",
    ...     type=EntityType.AGENT,
    ...     description="Classifies text into categories",
    ...     module_path="haive.agents.classifiers",
    ...     class_name="TextClassifierAgent",
    ...     created_at=datetime.now()
    ... )
    >>>
    >>> # Access properties
    >>> print(f"Registry item: {item.name} ({item.type})")
    >>> print(f"Created at: {item.created_at}")
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities that can be registered."""

    AGENT = "agent"
    TOOL = "tool"
    TOOLKIT = "toolkit"
    ENGINE = "engine"
    GAME = "game"
    LLM_MODEL = "llm_model"
    LLM_PROVIDER = "llm_provider"
    # MCP (Model Context Protocol) entity types
    MCP_SERVER = "mcp_server"
    MCP_CLIENT = "mcp_client"
    MCP_TOOL = "mcp_tool"
    MCP_RESOURCE = "mcp_resource"
    MCP_PROMPT = "mcp_prompt"


class ConfigType(str, Enum):
    """Types of configurations."""

    STATE_SCHEMA = "state_schema"
    INPUT_SCHEMA = "input_schema"
    OUTPUT_SCHEMA = "output_schema"
    ENGINE = "engine"
    PROMPT = "prompt"
    NODE = "node"
    GRAPH = "graph"


class DependencyType(str, Enum):
    """Types of dependencies between entities."""

    REQUIRES = "requires"  # Hard dependency
    USES = "uses"  # Soft dependency
    EXTENDS = "extends"  # Extension relationship


class ImportStatus(str, Enum):
    """Import operation status."""

    SUCCESS = "success"
    FAILURE = "failure"


class RegistryItem(BaseModel):
    """Base model for registry items.

    This model represents a component registered in the registry system,
    such as an agent, tool, engine, or game. It stores essential metadata
    about the component, including its type, location, and description.

    Attributes:
        id (str): Unique identifier for the registry item
        name (str): Human-readable name for the component
        type (EntityType): Type of the component (AGENT, TOOL, etc.)
        description (str, optional): Detailed description of the component
        module_path (str, optional): Python module path where the component is defined
        class_name (str, optional): Class name of the component within the module
        created_at (datetime, optional): Timestamp when the item was created
        updated_at (datetime, optional): Timestamp when the item was last updated
        metadata (dict): Additional metadata about the component

    Example:
        >>> from haive.dataflow.registry.models import RegistryItem, EntityType
        >>> from datetime import datetime
        >>>
        >>> item = RegistryItem(
        ...     name="TextSummarizer",
        ...     type=EntityType.TOOL,
        ...     description="Summarizes long text documents",
        ...     module_path="haive.tools.summarizers",
        ...     class_name="TextSummarizerTool",
        ...     created_at=datetime.now(),
        ...     metadata={"version": "1.0", "author": "Haive Team"}
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: EntityType
    description: str | None = None
    module_path: str | None = None
    class_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Configuration(BaseModel):
    """Configuration for a registry item.

    This model represents configuration data associated with a registry item.
    Configurations can include schema definitions, initialization parameters,
    prompt templates, and other settings needed for component operation.

    Attributes:
        id (str): Unique identifier for the configuration
        registry_id (str): ID of the associated registry item
        config_type (ConfigType): Type of configuration (STATE_SCHEMA, INPUT_SCHEMA, etc.)
        config_data (dict): The actual configuration data
        created_at (datetime, optional): Timestamp when the configuration was created
        updated_at (datetime, optional): Timestamp when the configuration was last updated

    Example:
        >>> from haive.dataflow.registry.models import Configuration, ConfigType
        >>> from datetime import datetime
        >>>
        >>> config = Configuration(
        ...     registry_id="tool-123",
        ...     config_type=ConfigType.INPUT_SCHEMA,
        ...     config_data={
        ...         "type": "object",
        ...         "properties": {
        ...             "text": {"type": "string", "description": "Text to process"},
        ...             "max_length": {"type": "integer", "default": 100}
        ...         },
        ...         "required": ["text"]
        ...     },
        ...     created_at=datetime.now()
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    config_type: ConfigType
    config_data: dict[str, Any]
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GraphDefinition(BaseModel):
    """Graph definition for a registry item.

    This model represents a graph structure definition for a component, such as
    an agent or engine. It stores the nodes and edges that define the component's
    execution flow or structure.

    Attributes:
        id (str): Unique identifier for the graph definition
        registry_id (str): ID of the associated registry item
        nodes (List[Dict[str, Any]]): List of node definitions in the graph
        edges (List[Dict[str, Any]]): List of edge definitions connecting nodes
        created_at (datetime, optional): Timestamp when the graph was created
        updated_at (datetime, optional): Timestamp when the graph was last updated

    Example:
        >>> from haive.dataflow.registry.models import GraphDefinition
        >>> from datetime import datetime
        >>>
        >>> graph = GraphDefinition(
        ...     registry_id="agent-123",
        ...     nodes=[
        ...         {"id": "node1", "type": "input", "config": {...}},
        ...         {"id": "node2", "type": "processing", "config": {...}},
        ...         {"id": "node3", "type": "output", "config": {...}}
        ...     ],
        ...     edges=[
        ...         {"source": "node1", "target": "node2"},
        ...         {"source": "node2", "target": "node3"}
        ...     ],
        ...     created_at=datetime.now()
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Dependency(BaseModel):
    """Dependency relationship between registry items.

    This model represents a dependency relationship between two registry items,
    such as a tool requiring a specific engine, or an agent extending another agent.
    It captures the type of relationship and the entities involved.

    Attributes:
        id (str): Unique identifier for the dependency
        registry_id (str): ID of the registry item that has the dependency
        dependent_id (str): ID of the registry item that is depended upon
        dependency_type (DependencyType): Type of dependency relationship
        created_at (datetime, optional): Timestamp when the dependency was created

    Example:
        >>> from haive.dataflow.registry.models import Dependency, DependencyType
        >>> from datetime import datetime
        >>>
        >>> dependency = Dependency(
        ...     registry_id="tool-123",
        ...     dependent_id="engine-456",
        ...     dependency_type=DependencyType.REQUIRES,
        ...     created_at=datetime.now()
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    dependent_id: str
    dependency_type: DependencyType
    created_at: datetime | None = None


class EnvironmentVar(BaseModel):
    """Environment variable requirement for a registry item.

    This model represents an environment variable that a component requires
    or can use. It tracks whether the variable is required, and can provide
    a default value for optional variables.

    Attributes:
        id (str): Unique identifier for the environment variable entry
        registry_id (str): ID of the registry item that requires this variable
        env_name (str): Name of the environment variable (e.g., "OPENAI_API_KEY")
        is_required (bool): Whether the variable is required for the component to function
        default_value (str, optional): Default value for the variable if not provided
        created_at (datetime, optional): Timestamp when the entry was created

    Example:
        >>> from haive.dataflow.registry.models import EnvironmentVar
        >>> from datetime import datetime
        >>>
        >>> env_var = EnvironmentVar(
        ...     registry_id="agent-123",
        ...     env_name="OPENAI_API_KEY",
        ...     is_required=True,
        ...     created_at=datetime.now()
        ... )
        >>>
        >>> optional_var = EnvironmentVar(
        ...     registry_id="tool-456",
        ...     env_name="DEBUG_LEVEL",
        ...     is_required=False,
        ...     default_value="INFO",
        ...     created_at=datetime.now()
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    env_name: str
    is_required: bool = False
    default_value: str | None = None
    created_at: datetime | None = None


class ImportLogItem(BaseModel):
    """Log entry for import operations.

    This model represents a log entry for an import operation, recording the details
    of a single entity import attempt. It tracks the status, any error messages,
    and the session it belongs to.

    Attributes:
        id (str): Unique identifier for the log entry
        import_session (str): ID of the import session this log belongs to
        entity_name (str): Name of the entity being imported
        entity_type (str): Type of the entity being imported
        status (ImportStatus): Status of the import operation (SUCCESS, FAILURE)
        message (str, optional): Optional message or details about the import
        traceback (str, optional): Error traceback if the import failed

    Example:
        >>> from haive.dataflow.registry.models import ImportLogItem, ImportStatus
        >>> from datetime import datetime
        >>>
        >>> log_entry = ImportLogItem(
        ...     import_session="session-123",
        ...     entity_name="gpt-4",
        ...     entity_type="llm_model",
        ...     status=ImportStatus.SUCCESS,
        ...     message="Successfully imported model"
        ... )
        >>>
        >>> error_log = ImportLogItem(
        ...     import_session="session-123",
        ...     entity_name="invalid-model",
        ...     entity_type="llm_model",
        ...     status=ImportStatus.FAILURE,
        ...     message="Failed to import model",
        ...     traceback="ImportError: Model not found"
        ... )
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    import_session: str
    entity_name: str
    entity_type: str
    status: ImportStatus
    message: str | None = None
    traceback: str | None = None
    created_at: datetime | None = None


# MCP (Model Context Protocol) Specific Models


class MCPTransport(str, Enum):
    """Transport types for MCP servers."""

    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server.

    This model represents the configuration needed to connect to and interact
    with an MCP (Model Context Protocol) server, including connection details,
    authentication, and capabilities.

    Attributes:
        name (str): Unique name for the MCP server
        transport (MCPTransport): Communication transport type
        command (str, optional): Command to run the server (for stdio transport)
        args (list[str]): Arguments for the server command
        env (dict[str, str]): Environment variables for the server
        url (str, optional): URL for HTTP/SSE transports
        capabilities (list[str]): List of server capabilities
        auth_config (dict[str, Any], optional): Authentication configuration
        health_check_interval (int): Seconds between health checks
        timeout (int): Connection timeout in seconds
        max_retries (int): Maximum connection retry attempts

    Example:
        >>> config = MCPServerConfig(
        ...     name="filesystem",
        ...     transport=MCPTransport.STDIO,
        ...     command="npx",
        ...     args=["-y", "@modelcontextprotocol/server-filesystem"],
        ...     capabilities=["file_read", "file_write", "directory_list"]
        ... )
    """

    name: str
    transport: MCPTransport
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    auth_config: dict[str, Any] | None = None
    health_check_interval: int = 30
    timeout: int = 10
    max_retries: int = 3


class MCPToolDefinition(BaseModel):
    """Definition of an MCP tool.

    This model represents a tool provided by an MCP server, including its
    name, description, schema, and metadata needed for execution.

    Attributes:
        name (str): Tool name
        description (str): Tool description
        server_name (str): Name of the MCP server providing this tool
        schema (dict[str, Any]): JSON schema for tool parameters
        input_schema (dict[str, Any], optional): Input validation schema
        output_schema (dict[str, Any], optional): Output validation schema
        tags (list[str]): Tags for categorization
        version (str): Tool version

    Example:
        >>> tool = MCPToolDefinition(
        ...     name="read_file",
        ...     description="Read contents of a file",
        ...     server_name="filesystem",
        ...     schema={"type": "object", "properties": {"path": {"type": "string"}}},
        ...     tags=["filesystem", "read"]
        ... )
    """

    name: str
    description: str
    server_name: str
    tool_schema: dict[str, Any] = Field(..., alias="schema")
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    tags: list[str] = Field(default_factory=list)
    version: str = "1.0.0"


class MCPResourceDefinition(BaseModel):
    """Definition of an MCP resource.

    This model represents a resource provided by an MCP server, such as
    files, datasets, or other data sources that can be accessed by LLMs.

    Attributes:
        name (str): Resource name
        uri (str): Resource URI
        server_name (str): Name of the MCP server providing this resource
        mime_type (str, optional): MIME type of the resource
        description (str, optional): Resource description
        annotations (dict[str, Any]): Additional metadata
        size (int, optional): Resource size in bytes
        last_modified (datetime, optional): Last modification timestamp

    Example:
        >>> resource = MCPResourceDefinition(
        ...     name="project_docs",
        ...     uri="file:///project/docs/",
        ...     server_name="filesystem",
        ...     mime_type="text/markdown",
        ...     description="Project documentation files"
        ... )
    """

    name: str
    uri: str
    server_name: str
    mime_type: str | None = None
    description: str | None = None
    annotations: dict[str, Any] = Field(default_factory=dict)
    size: int | None = None
    last_modified: datetime | None = None


class MCPPromptDefinition(BaseModel):
    """Definition of an MCP prompt template.

    This model represents a prompt template provided by an MCP server,
    including variables, instructions, and metadata for prompt execution.

    Attributes:
        name (str): Prompt name
        description (str): Prompt description
        server_name (str): Name of the MCP server providing this prompt
        template (str): Prompt template string
        variables (list[dict[str, Any]]): Template variable definitions
        instructions (str, optional): Usage instructions
        examples (list[dict[str, Any]]): Example inputs/outputs
        tags (list[str]): Tags for categorization

    Example:
        >>> prompt = MCPPromptDefinition(
        ...     name="code_review",
        ...     description="Review code for best practices",
        ...     server_name="github",
        ...     template="Review this code: {code}",
        ...     variables=[{"name": "code", "type": "string", "required": True}],
        ...     tags=["code", "review"]
        ... )
    """

    name: str
    description: str
    server_name: str
    template: str
    variables: list[dict[str, Any]] = Field(default_factory=list)
    instructions: str | None = None
    examples: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class MCPServerHealth(BaseModel):
    """Health status of an MCP server.

    This model tracks the health and performance metrics of an MCP server,
    including connection status, response times, and error rates.

    Attributes:
        server_name (str): Name of the MCP server
        is_healthy (bool): Whether the server is healthy
        last_check (datetime): Last health check timestamp
        response_time_ms (float, optional): Average response time in milliseconds
        error_count (int): Number of recent errors
        uptime_seconds (float, optional): Server uptime in seconds
        capabilities_available (list[str]): Currently available capabilities
        error_details (str, optional): Details of recent errors

    Example:
        >>> health = MCPServerHealth(
        ...     server_name="filesystem",
        ...     is_healthy=True,
        ...     last_check=datetime.now(),
        ...     response_time_ms=50.0,
        ...     error_count=0,
        ...     capabilities_available=["file_read", "file_write"]
        ... )
    """

    server_name: str
    is_healthy: bool
    last_check: datetime
    response_time_ms: float | None = None
    error_count: int = 0
    uptime_seconds: float | None = None
    capabilities_available: list[str] = Field(default_factory=list)
    error_details: str | None = None
