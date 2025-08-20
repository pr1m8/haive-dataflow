# haive-dataflow/src/haive/dataflow/platform/models/servers.py
"""
Server Models - Intelligent Inheritance Hierarchy for All Server Types

This module provides a comprehensive server model hierarchy using intelligent inheritance patterns.
All server models inherit from BaseServerInfo and specialize for different server types.

Inheritance Hierarchy:
- BaseServerInfo (foundation)
  ├── MCPServerInfo (MCP-specific servers)
  │   └── DownloadedServerInfo (our 63 downloaded servers)
  └── [Future server types: HAP, Custom, etc.]

Key Features:
- Pure Pydantic models with intelligent inheritance
- Specialized models for different server sources
- Comprehensive validation and field management
- Factory methods for creating servers from real data
- Connection configuration and health monitoring
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .mcp import MCPTransport, ServerSource, ServerStatus, HealthStatus


class ConnectionConfig(BaseModel):
    """Server connection configuration.
    
    This model defines how to connect to and communicate with servers,
    supporting multiple transport protocols and connection methods.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Command-based connections (stdio, process)
    command: Optional[str] = Field(
        None,
        description="Command to start server (e.g., 'npx', 'python')",
        examples=["npx", "python", "node", "java"]
    )
    args: List[str] = Field(
        default_factory=list,
        description="Command arguments",
        examples=[["-y", "server-name"], ["-m", "server.module"], ["--port", "8080"]]
    )
    env: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for server process",
        examples=[{"NODE_ENV": "production"}, {"API_KEY": "secret"}]
    )
    
    # URL-based connections (http, sse, websocket)
    url: Optional[str] = Field(
        None,
        description="URL for HTTP/SSE/WebSocket transport",
        examples=["http://localhost:8080", "wss://api.example.com/mcp"]
    )
    
    # Connection settings
    timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )
    max_retries: int = Field(
        default=3,
        description="Maximum connection retry attempts",
        ge=0,
        le=10
    )
    retry_delay: int = Field(
        default=5,
        description="Delay between retries in seconds",
        ge=1,
        le=60
    )
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v and not v.startswith(('http://', 'https://', 'ws://', 'wss://')):
            raise ValueError("URL must start with http://, https://, ws://, or wss://")
        return v
    
    def is_command_based(self) -> bool:
        """Check if connection is command-based."""
        return self.command is not None
    
    def is_url_based(self) -> bool:
        """Check if connection is URL-based."""
        return self.url is not None
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get connection configuration summary."""
        if self.is_command_based():
            return {
                "type": "command",
                "command": self.command,
                "args": self.args,
                "timeout": self.timeout
            }
        elif self.is_url_based():
            return {
                "type": "url",
                "url": self.url,
                "timeout": self.timeout
            }
        else:
            return {"type": "unconfigured"}


class ToolInfo(BaseModel):
    """Information about a server tool."""
    
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    schema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")


class ResourceInfo(BaseModel):
    """Information about a server resource."""
    
    model_config = ConfigDict(extra="forbid")
    
    uri: str = Field(..., description="Resource URI")
    name: Optional[str] = Field(None, description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    mime_type: Optional[str] = Field(None, description="Resource MIME type")


class PromptInfo(BaseModel):
    """Information about a server prompt."""
    
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    arguments: List[Dict[str, Any]] = Field(default_factory=list, description="Prompt arguments")


class PerformanceMetrics(BaseModel):
    """Server performance metrics."""
    
    model_config = ConfigDict(extra="forbid")
    
    average_response_time: Optional[float] = Field(None, description="Average response time in seconds")
    success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Success rate (0-1)")
    total_requests: int = Field(default=0, ge=0, description="Total number of requests")
    failed_requests: int = Field(default=0, ge=0, description="Number of failed requests")
    last_response_time: Optional[float] = Field(None, description="Last response time in seconds")


class BaseServerInfo(BaseModel):
    """Foundation server model - all servers inherit from this.
    
    This is the base class for all server models in the Haive ecosystem.
    It provides core identification, operational status, and metadata management
    that all server types need, regardless of their specific protocol or purpose.
    
    Design Philosophy:
    - Pure Pydantic model (no __init__ method)
    - Foundation for intelligent inheritance
    - Common fields that ALL servers need
    - Extensible through inheritance
    - Comprehensive validation
    
    Inheritance Strategy:
    - BaseServerInfo (this class): Core server identity and status
    - MCPServerInfo: Adds MCP-specific fields and capabilities
    - DownloadedServerInfo: Specialized for our 63 downloaded servers
    - [Future]: HAPServerInfo, CustomServerInfo, etc.
    
    Examples:
        Basic server::
        
            server = BaseServerInfo(
                server_id="my-server",
                server_name="My Test Server",
                description="A basic server for testing"
            )
            
        Server with status::
        
            server = BaseServerInfo(
                server_id="prod-server",
                server_name="Production Server",
                description="Production service",
                status=ServerStatus.ACTIVE,
                health_status=HealthStatus.HEALTHY
            )
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "server_id": "example-server",
                    "server_name": "Example Server",
                    "description": "An example server configuration",
                    "status": "active",
                    "health_status": "healthy"
                }
            ]
        }
    )
    
    # Core identification - required for all servers
    server_id: str = Field(
        ...,
        description="Unique server identifier (alphanumeric with - and _)",
        examples=["mcp-browser-server", "filesystem_server", "agent-proxy-01"]
    )
    server_name: str = Field(
        ...,
        description="Human-readable server name",
        examples=["MCP Browser Server", "Filesystem MCP Server", "Agent Proxy"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed server description",
        examples=["Provides file system access via MCP", "Exposes agent functionality"]
    )
    
    # Core operational data - status and health
    status: ServerStatus = Field(
        default=ServerStatus.UNKNOWN,
        description="Current operational status of the server"
    )
    health_status: HealthStatus = Field(
        default=HealthStatus.UNKNOWN,
        description="Current health status from health checks"
    )
    
    # Metadata common to all servers
    version: Optional[str] = Field(
        None,
        description="Server version",
        examples=["1.0.0", "2.1.3-beta"]
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Server record creation timestamp"
    )
    last_updated: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    @field_validator("server_id")
    @classmethod
    def validate_server_id_format(cls, v: str) -> str:
        """Ensure server ID is valid.
        
        Server IDs must be:
        - Alphanumeric characters only
        - Hyphens (-) and underscores (_) allowed
        - No spaces or special characters
        - Between 3 and 100 characters
        
        Args:
            v: Server ID to validate
            
        Returns:
            Validated server ID
            
        Raises:
            ValueError: If server ID format is invalid
        """
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Server ID must be alphanumeric with - and _")
        
        if len(v) < 3:
            raise ValueError("Server ID must be at least 3 characters")
        
        if len(v) > 100:
            raise ValueError("Server ID must be at most 100 characters")
        
        return v
    
    def update_status(self, new_status: ServerStatus, update_timestamp: bool = True) -> None:
        """Update server status and optionally timestamp.
        
        Args:
            new_status: New server status
            update_timestamp: Whether to update last_updated timestamp
        """
        self.status = new_status
        if update_timestamp:
            self.last_updated = datetime.utcnow()
    
    def update_health_status(self, new_health_status: HealthStatus) -> None:
        """Update server health status with timestamp.
        
        Args:
            new_health_status: New health status
        """
        self.health_status = new_health_status
        self.last_updated = datetime.utcnow()
    
    def get_server_summary(self) -> Dict[str, Any]:
        """Get basic server information summary.
        
        Returns:
            Dictionary with core server information
        """
        return {
            "server_id": self.server_id,
            "server_name": self.server_name,
            "description": self.description,
            "status": self.status,
            "health_status": self.health_status,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class MCPServerInfo(BaseServerInfo):
    """MCP-specific server - inherits base + adds MCP capabilities.
    
    This model extends BaseServerInfo with MCP (Model Context Protocol) specific
    functionality while maintaining the inheritance pattern. It adds MCP transport,
    tools, resources, and plugin management.
    
    Inheritance Features:
    - Inherits: server_id, server_name, status, timestamps from BaseServerInfo
    - Extends: MCP transport, connection config, tools, resources
    - Adds: Plugin management, performance metrics, source tracking
    
    Examples:
        Basic MCP server::
        
            server = MCPServerInfo(
                server_id="mcp-filesystem",
                server_name="MCP Filesystem Server",
                description="File system access via MCP",
                source=ServerSource.NPM_PACKAGE,
                transport=MCPTransport.STDIO,
                connection_config=ConnectionConfig(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem"]
                ),
                managed_by_plugin="mcp-browser"
            )
            
        Server with tools and resources::
        
            server = MCPServerInfo(
                server_id="mcp-web-tools",
                server_name="Web Tools MCP Server", 
                source=ServerSource.DOWNLOADED,
                transport=MCPTransport.STDIO,
                connection_config=connection_config,
                managed_by_plugin="mcp-browser",
                tools=[
                    ToolInfo(name="web_search", description="Search the web"),
                    ToolInfo(name="web_scrape", description="Scrape web pages")
                ],
                resources=[
                    ResourceInfo(uri="web://search", name="search_results")
                ]
            )
    """
    
    # MCP-specific identification and source tracking
    source: ServerSource = Field(
        ...,
        description="Where this server came from (downloaded, registry, etc.)"
    )
    transport: MCPTransport = Field(
        ...,
        description="MCP transport protocol (stdio, http, sse, websocket)"
    )
    connection_config: ConnectionConfig = Field(
        ...,
        description="Connection configuration for this server"
    )
    
    # MCP capabilities - structured inheritance of functionality
    tools: List[ToolInfo] = Field(
        default_factory=list,
        description="Tools provided by this MCP server"
    )
    resources: List[ResourceInfo] = Field(
        default_factory=list,
        description="Resources provided by this MCP server"
    )
    prompts: List[PromptInfo] = Field(
        default_factory=list,
        description="Prompts provided by this MCP server"
    )
    
    # Plugin management - inherited and extended from BaseServerInfo
    managed_by_plugin: str = Field(
        ...,
        description="Which plugin manages this server",
        examples=["mcp-browser", "hap-agents", "custom-plugin"]
    )
    plugin_specific_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin-specific data and configuration"
    )
    
    # Enhanced metadata for MCP servers - extends base metadata
    repository_url: Optional[str] = Field(None, description="Source code repository URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    stars: Optional[int] = Field(None, ge=0, description="GitHub stars (if applicable)")
    language: Optional[str] = Field(None, description="Implementation language")
    author: Optional[str] = Field(None, description="Server author/organization")
    
    # Performance and health - inherited and extended from BaseServerInfo
    performance_metrics: Optional[PerformanceMetrics] = Field(
        None,
        description="Performance metrics and statistics"
    )
    last_health_check: Optional[datetime] = Field(None, description="Last health check timestamp")
    connection_attempts: int = Field(default=0, ge=0, description="Total connection attempts")
    successful_connections: int = Field(default=0, ge=0, description="Successful connections")
    
    @field_validator("stars")
    @classmethod
    def validate_stars_reasonable(cls, v: Optional[int]) -> Optional[int]:
        """Validate star count is reasonable."""
        if v is not None and v > 1000000:  # 1M stars seems like a reasonable upper bound
            raise ValueError("Star count seems unreasonably high (>1M)")
        return v
    
    @property
    def connection_success_rate(self) -> float:
        """Calculate connection success rate.
        
        Returns:
            Success rate as float between 0.0 and 1.0
        """
        if self.connection_attempts == 0:
            return 0.0
        return self.successful_connections / self.connection_attempts
    
    def record_connection_attempt(self, success: bool) -> None:
        """Record a connection attempt.
        
        Args:
            success: Whether the connection was successful
        """
        self.connection_attempts += 1
        if success:
            self.successful_connections += 1
        self.last_updated = datetime.utcnow()
    
    def get_mcp_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of MCP capabilities.
        
        Returns:
            Dictionary with MCP-specific capability information
        """
        return {
            "transport": self.transport,
            "source": self.source,
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "prompts_count": len(self.prompts),
            "connection_success_rate": self.connection_success_rate,
            "managed_by": self.managed_by_plugin,
            "has_performance_data": self.performance_metrics is not None
        }
    
    def get_tool_names(self) -> List[str]:
        """Get list of tool names provided by this server.
        
        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]
    
    def get_resource_uris(self) -> List[str]:
        """Get list of resource URIs provided by this server.
        
        Returns:
            List of resource URIs
        """
        return [resource.uri for resource in self.resources]


class DownloadedServerInfo(MCPServerInfo):
    """Specialized for our 63 downloaded servers - intelligent specialization.
    
    This model is specialized for the servers we successfully downloaded using our
    bulk installer. It inherits all MCPServerInfo capabilities and adds specific
    fields and methods for managing downloaded servers.
    
    Specialized Features:
    - Always has source=ServerSource.DOWNLOADED (frozen field)
    - Tracks download metadata (timestamp, local directory, install command)
    - Links to original CSV data and install reports
    - Factory methods for creating from real download data
    - Enhanced for our specific bulk download workflow
    
    Examples:
        From our download data::
        
            server = DownloadedServerInfo(
                server_id="browser-tools-mcp",
                server_name="AgentDeskAI/browser-tools-mcp",
                description="Browser monitoring and interaction tool",
                transport=MCPTransport.STDIO,
                connection_config=ConnectionConfig(
                    command="npx",
                    args=["-y", "browser-tools-mcp"]
                ),
                managed_by_plugin="mcp-browser",
                repository_url="https://github.com/AgentDeskAI/browser-tools-mcp",
                stars=5555,
                language="JavaScript",
                install_command_used="npx -y browser-tools-mcp",
                bulk_install_session="bulk-session-20250819"
            )
    """
    
    # Always downloaded source - frozen field
    source: ServerSource = Field(
        default=ServerSource.DOWNLOADED,
        frozen=True,
        description="Always DOWNLOADED for this server type"
    )
    
    # Downloaded-specific metadata - extends MCP server metadata
    download_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this server was downloaded"
    )
    local_directory: Optional[Path] = Field(
        None,
        description="Local directory path where server was downloaded"
    )
    install_command_used: Optional[str] = Field(
        None,
        description="Actual command used for installation",
        examples=["npx -y browser-tools-mcp", "pip install git+https://github.com/..."]
    )
    bulk_install_session: Optional[str] = Field(
        None,
        description="Which bulk install session this was part of",
        examples=["bulk-session-20250819", "manual-install-001"]
    )
    
    # Enhanced for our specific download data - links back to original sources
    csv_data_row: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original CSV data row from our server database"
    )
    readme_content: Optional[str] = Field(
        None,
        description="README file content if available"
    )
    detected_tools: List[str] = Field(
        default_factory=list,
        description="Auto-detected tools from analysis"
    )
    
    @field_validator("local_directory")
    @classmethod
    def validate_directory_exists(cls, v: Optional[Path]) -> Optional[Path]:
        """Validate local directory exists if specified."""
        if v is not None and not v.exists():
            raise ValueError(f"Local directory does not exist: {v}")
        return v
    
    @classmethod
    def from_csv_and_install_report(
        cls,
        csv_row: Dict[str, Any],
        install_report_entry: Dict[str, Any],
        bulk_session_id: str
    ) -> 'DownloadedServerInfo':
        """Factory method to create from our actual download data.
        
        This factory method creates a DownloadedServerInfo instance from the real
        CSV data and install report that we generated during our bulk download session.
        
        Args:
            csv_row: Row from our mcp_servers_data.csv
            install_report_entry: Entry from install report JSON
            bulk_session_id: ID of the bulk install session
            
        Returns:
            DownloadedServerInfo instance configured from real data
            
        Examples:
            >>> csv_row = {
            ...     'name': 'AgentDeskAI/browser-tools-mcp',
            ...     'description': 'Browser monitoring tool',
            ...     'repository_url': 'https://github.com/AgentDeskAI/browser-tools-mcp',
            ...     'stars': 5555.0,
            ...     'language': 'JavaScript'
            ... }
            >>> install_entry = {
            ...     'name': 'AgentDeskAI/browser-tools-mcp',
            ...     'command': 'npx -y browser-tools-mcp',
            ...     'status': 'success'
            ... }
            >>> server = DownloadedServerInfo.from_csv_and_install_report(
            ...     csv_row, install_entry, "bulk-session-20250819"
            ... )
        """
        return cls(
            server_id=csv_row['name'].replace('/', '-'),
            server_name=csv_row['name'],
            description=csv_row.get('description', ''),
            transport=cls._determine_transport_from_language(csv_row.get('language')),
            connection_config=cls._create_connection_config_from_csv(csv_row),
            managed_by_plugin="mcp-browser",
            repository_url=csv_row.get('repository_url'),
            stars=int(csv_row['stars']) if pd.notna(csv_row.get('stars')) else None,
            language=csv_row.get('language'),
            csv_data_row=csv_row,
            bulk_install_session=bulk_session_id,
            install_command_used=install_report_entry.get('command')
        )
    
    @staticmethod
    def _determine_transport_from_language(language: Optional[str]) -> MCPTransport:
        """Intelligent transport determination based on language.
        
        Args:
            language: Programming language of the server
            
        Returns:
            Most appropriate MCPTransport for the language
        """
        if not language:
            return MCPTransport.STDIO
        
        language_lower = language.lower()
        if language_lower in ['javascript', 'typescript']:
            return MCPTransport.STDIO  # Most npm MCP packages use stdio
        elif language_lower == 'python':
            return MCPTransport.HTTP    # Python servers often use HTTP
        else:
            return MCPTransport.STDIO   # Safe default
    
    @staticmethod
    def _create_connection_config_from_csv(csv_row: Dict[str, Any]) -> ConnectionConfig:
        """Create connection config from CSV data.
        
        Args:
            csv_row: CSV data row
            
        Returns:
            ConnectionConfig appropriate for the server
        """
        repo_name = csv_row.get('repository_name', csv_row.get('name', 'unknown'))
        language = csv_row.get('language', '')
        
        if language.lower() in ['javascript', 'typescript']:
            # Most npm packages
            return ConnectionConfig(
                command="npx",
                args=["-y", repo_name.split('/')[-1]],  # Use just the package name
                timeout=30
            )
        elif language.lower() == 'python':
            # Python packages - might need different approach
            return ConnectionConfig(
                command="python",
                args=["-m", repo_name.split('/')[-1].replace('-', '_')],
                timeout=30
            )
        else:
            # Fallback - probably needs git clone approach
            return ConnectionConfig(
                command="echo",
                args=["Server not configured - needs manual setup"],
                timeout=10
            )
    
    def get_download_summary(self) -> Dict[str, Any]:
        """Get download-specific information summary.
        
        Returns:
            Dictionary with download metadata and status
        """
        return {
            "download_info": {
                "download_timestamp": self.download_timestamp.isoformat(),
                "bulk_install_session": self.bulk_install_session,
                "install_command_used": self.install_command_used,
                "local_directory": str(self.local_directory) if self.local_directory else None
            },
            "source_data": {
                "has_csv_data": bool(self.csv_data_row),
                "has_readme": bool(self.readme_content),
                "detected_tools_count": len(self.detected_tools)
            },
            "repository_info": {
                "repository_url": self.repository_url,
                "stars": self.stars,
                "language": self.language,
                "author": self.author
            },
            "connection_info": self.connection_config.get_connection_summary(),
            "inherited_info": self.get_mcp_capabilities_summary()
        }