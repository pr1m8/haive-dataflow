"""Base models for server management.

This module defines the fundamental Pydantic models used for server configuration
and runtime information across all server types.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
import logging

logger = logging.getLogger(__name__)


class ServerStatus(str, Enum):
    """Universal server status enum."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    HEALTH_CHECK_FAILED = "health_check_failed"
    RESTARTING = "restarting"


class BaseServerConfig(BaseModel):
    """Base configuration all servers must have.
    
    This model defines the minimum configuration required for any server type.
    Subclasses should extend this with type-specific fields.
    
    Attributes:
        name: Unique server identifier
        command: Command to execute (executable + args)
        description: Human-readable description
        working_directory: Optional working directory for process
        environment: Additional environment variables
        timeout_seconds: Startup timeout in seconds
        auto_restart: Whether to restart on failure
        health_check_enabled: Whether to perform health checks
        
    Example:
        Basic server configuration::
        
            config = BaseServerConfig(
                name="my-server",
                command=["python", "-m", "server"],
                description="My custom server"
            )
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "example-server",
                    "command": ["python", "-m", "http.server", "8000"],
                    "description": "Simple HTTP server",
                    "working_directory": "/tmp",
                    "timeout_seconds": 30
                }
            ]
        }
    )
    
    # Required fields
    name: str = Field(
        ..., 
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$',
        description="Server identifier (alphanumeric, hyphens, underscores)"
    )
    command: List[str] = Field(
        ..., 
        min_length=1,
        description="Command to execute [executable, ...args]"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable description"
    )
    
    # Optional fields with smart defaults
    working_directory: Optional[str] = Field(
        None,
        description="Working directory for the process"
    )
    environment: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional environment variables"
    )
    timeout_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Startup timeout in seconds (1-3600)"
    )
    auto_restart: bool = Field(
        default=False,
        description="Automatically restart on failure"
    )
    health_check_enabled: bool = Field(
        default=True,
        description="Enable health checking"
    )
    
    @field_validator("command")
    @classmethod
    def validate_command_not_empty(cls, v: List[str]) -> List[str]:
        """Validate command has executable and no empty strings."""
        if not v:
            raise ValueError("Command must have at least one element")
        
        # Check for empty strings
        if any(not cmd.strip() for cmd in v):
            raise ValueError("Command cannot contain empty strings")
            
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Validate name follows naming convention."""
        if v.startswith("-") or v.startswith("_"):
            raise ValueError("Name cannot start with hyphen or underscore")
        return v
    
    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, v: Optional[str]) -> Optional[str]:
        """Validate working directory if provided."""
        if v is not None:
            # Just check it's not empty
            if not v.strip():
                raise ValueError("Working directory cannot be empty string")
        return v
    
    @field_validator("environment")
    @classmethod
    def validate_environment_vars(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate environment variable names and values."""
        for key, value in v.items():
            if not key.replace("_", "").isalnum():
                raise ValueError(f"Invalid environment variable name: {key}")
            if not isinstance(value, str):
                raise ValueError(f"Environment value must be string, got {type(value)}")
        return v


class BaseServerInfo(BaseModel):
    """Base runtime info all servers have.
    
    This model represents the runtime state of a server process.
    It excludes the actual process handle from serialization.
    
    Attributes:
        name: Server name
        pid: Process ID
        status: Current server status
        started_at: When the server was started
        config_snapshot: Configuration used to start server
        error_message: Last error message if any
        restart_count: Number of times server has been restarted
        last_health_check: Last successful health check time
        uptime_seconds: Computed uptime in seconds
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,  # For process object
        json_schema_extra={
            "examples": [
                {
                    "name": "example-server",
                    "pid": 12345,
                    "status": "running",
                    "started_at": "2025-01-20T12:00:00Z",
                    "config_snapshot": {
                        "name": "example-server",
                        "command": ["python", "-m", "server"],
                        "description": "Example server"
                    }
                }
            ]
        }
    )
    
    # Core runtime fields
    name: str = Field(
        ...,
        description="Server name"
    )
    pid: int = Field(
        ...,
        gt=0,
        description="Process ID"
    )
    status: ServerStatus = Field(
        ...,
        description="Current server status"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When server was started"
    )
    
    # Runtime metadata
    config_snapshot: Dict[str, Any] = Field(
        ...,
        description="Configuration used to start this server"
    )
    error_message: Optional[str] = Field(
        None,
        max_length=1000,
        description="Last error message if any"
    )
    restart_count: int = Field(
        default=0,
        ge=0,
        description="Number of times server has been restarted"
    )
    last_health_check: Optional[datetime] = Field(
        None,
        description="Last successful health check time"
    )
    
    # Process handle (excluded from serialization)
    process_handle: Optional[Any] = Field(
        None,
        exclude=True,
        description="subprocess.Popen instance",
        alias="_process"
    )
    
    @property
    def is_running(self) -> bool:
        """Check if server process is currently running."""
        if self.process_handle is None:
            return self.status == ServerStatus.RUNNING
        return self.process_handle.poll() is None
    
    @property
    def uptime_seconds(self) -> float:
        """Calculate server uptime in seconds."""
        if self.status not in (ServerStatus.RUNNING, ServerStatus.HEALTH_CHECK_FAILED):
            return 0.0
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    def update_status(self, new_status: ServerStatus, error: Optional[str] = None) -> None:
        """Update server status with optional error message."""
        self.status = new_status
        if error:
            self.error_message = error
        elif new_status == ServerStatus.RUNNING:
            # Clear error on successful running state
            self.error_message = None
    
    def record_health_check(self, success: bool) -> None:
        """Record health check result."""
        if success:
            self.last_health_check = datetime.now(timezone.utc)
            if self.status == ServerStatus.HEALTH_CHECK_FAILED:
                self.status = ServerStatus.RUNNING
        else:
            self.status = ServerStatus.HEALTH_CHECK_FAILED