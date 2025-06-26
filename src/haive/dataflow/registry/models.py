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
from typing import Any, Dict, List, Optional

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
    description: Optional[str] = None
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


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
    config_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    created_at: Optional[datetime] = None


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
    default_value: Optional[str] = None
    created_at: Optional[datetime] = None


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
    message: Optional[str] = None
    traceback: Optional[str] = None
    created_at: Optional[datetime] = None
