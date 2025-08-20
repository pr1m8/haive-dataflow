# haive-dataflow/tests/platform/test_inheritance_patterns.py
"""
Test Intelligent Inheritance Patterns

This test module validates the intelligent inheritance patterns across all our platform models.
It tests the inheritance chain from BasePlatform through specialized platforms and validates
that the inheritance architecture works as designed in our plan.

Test Categories:
1. Platform inheritance chain validation
2. Server inheritance hierarchy validation  
3. Cross-inheritance functionality testing
4. Inheritance validation utilities
5. Real-world inheritance scenarios
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from haive.dataflow.platform.models import (
    BasePlatform,
    MCPPlatform,
    PluginPlatform,
    BaseServerInfo,
    MCPServerInfo,
    DownloadedServerInfo,
    PlatformStatus,
    ServerSource,
    MCPTransport,
    ConnectionConfig,
    validate_platform_inheritance,
    validate_server_inheritance,
)


class TestPlatformInheritanceChain:
    """Test platform inheritance patterns and hierarchy."""

    def test_mcp_platform_inherits_base_capabilities(self):
        """Test MCP platform inherits and extends base platform."""
        platform = MCPPlatform()
        
        # Inherited from BasePlatform
        assert hasattr(platform, 'platform_id')
        assert hasattr(platform, 'platform_name')
        assert hasattr(platform, 'created_at')
        assert hasattr(platform, 'status')
        assert hasattr(platform, 'config')
        assert hasattr(platform, 'metadata')
        
        # Extended in MCPPlatform
        assert hasattr(platform, 'supports_server_management')
        assert hasattr(platform, 'supports_tool_execution')
        assert hasattr(platform, 'api_config')
        assert hasattr(platform, 'discovery_config')
        assert hasattr(platform, 'plugins')
        
        # Inherited capabilities correctly overridden
        assert platform.supports_discovery is True
        assert platform.supports_health_monitoring is True
        assert platform.supports_authentication is True
        
        # MCP-specific capabilities
        assert platform.supports_server_management is True
        assert platform.supports_tool_execution is True
        assert platform.supports_bulk_operations is True
    
    def test_plugin_platform_inheritance(self):
        """Test plugin platform inheritance chain."""
        plugin = PluginPlatform(
            platform_id="test-plugin",
            platform_name="Test Plugin",
            description="Test plugin for inheritance",
            entry_point="test:TestPlugin",
            routes_prefix="/test"
        )
        
        # Inherited from BasePlatform
        assert plugin.platform_name == "Test Plugin"
        assert plugin.status == PlatformStatus.INITIALIZING
        assert isinstance(plugin.created_at, datetime)
        assert isinstance(plugin.config, dict)
        assert isinstance(plugin.metadata, dict)
        
        # Extended in PluginPlatform
        assert plugin.entry_point == "test:TestPlugin"
        assert plugin.routes_prefix == "/test"
        assert plugin.priority == 100  # Default
        assert plugin.dependencies == []  # Default
        
        # Plugin-specific capabilities
        assert plugin.provides_servers is False  # Default
        assert plugin.provides_tools is False    # Default
        assert plugin.provides_discovery is False
    
    def test_inheritance_method_propagation(self):
        """Test that methods are properly inherited across the chain."""
        platform = MCPPlatform()
        
        # Methods from BasePlatform should work
        platform.add_metadata("test_key", "test_value")
        assert platform.metadata["test_key"] == "test_value"
        
        platform.update_status(PlatformStatus.ACTIVE)
        assert platform.status == PlatformStatus.ACTIVE
        
        summary = platform.get_capability_summary()
        assert "discovery" in summary
        assert summary["discovery"] is True
        
        # Methods from MCPPlatform should work
        from haive.dataflow.platform.models import PluginConfig
        plugin_config = PluginConfig(
            name="test-plugin",
            entry_point="test:Plugin"
        )
        platform.add_plugin(plugin_config)
        assert len(platform.plugins) == 1
        
        retrieved_plugin = platform.get_plugin("test-plugin")
        assert retrieved_plugin is not None
        assert retrieved_plugin.name == "test-plugin"
        
        # Extended capability summary should work
        mcp_summary = platform.get_mcp_capability_summary()
        assert "discovery" in mcp_summary  # From base
        assert "server_management" in mcp_summary  # From MCP
        assert mcp_summary["server_management"] is True
    
    def test_field_override_behavior(self):
        """Test that field defaults can be properly overridden in inheritance."""
        # BasePlatform defaults
        base_platform = BasePlatform(
            platform_id="base",
            platform_name="Base",
            description="Base platform"
        )
        assert base_platform.supports_discovery is False
        assert base_platform.supports_health_monitoring is False
        
        # MCPPlatform overrides
        mcp_platform = MCPPlatform()
        assert mcp_platform.supports_discovery is True  # Overridden
        assert mcp_platform.supports_health_monitoring is True  # Overridden
        assert mcp_platform.platform_id == "haive-mcp-platform"  # Default override
        assert mcp_platform.platform_name == "Haive MCP Platform"  # Default override


class TestServerInheritanceHierarchy:
    """Test server model inheritance hierarchy."""
    
    def test_mcp_server_inherits_base_server(self):
        """Test MCPServerInfo inherits from BaseServerInfo correctly."""
        server = MCPServerInfo(
            server_id="test-mcp-server",
            server_name="Test MCP Server",
            description="Test server for inheritance validation",
            source=ServerSource.DOWNLOADED,
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(
                command="echo",
                args=["test"]
            ),
            managed_by_plugin="test-plugin"
        )
        
        # Inherited from BaseServerInfo
        assert hasattr(server, 'server_id')
        assert hasattr(server, 'server_name')
        assert hasattr(server, 'description')
        assert hasattr(server, 'status')
        assert hasattr(server, 'health_status')
        assert hasattr(server, 'version')
        assert hasattr(server, 'created_at')
        
        # Extended in MCPServerInfo
        assert hasattr(server, 'source')
        assert hasattr(server, 'transport')
        assert hasattr(server, 'connection_config')
        assert hasattr(server, 'tools')
        assert hasattr(server, 'resources')
        assert hasattr(server, 'managed_by_plugin')
        assert hasattr(server, 'repository_url')
        assert hasattr(server, 'stars')
        
        # Values should be correct
        assert server.server_id == "test-mcp-server"
        assert server.source == ServerSource.DOWNLOADED
        assert server.transport == MCPTransport.STDIO
        assert server.managed_by_plugin == "test-plugin"
    
    def test_downloaded_server_specialization(self):
        """Test DownloadedServerInfo specialized inheritance."""
        # Create with factory method
        csv_row = {
            'name': 'test/downloaded-server',
            'description': 'Test downloaded server',
            'repository_url': 'https://github.com/test/downloaded-server',
            'stars': 100.0,
            'language': 'JavaScript'
        }
        
        install_entry = {
            'name': 'test/downloaded-server',
            'command': 'npx -y downloaded-server',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "test-session-123"
        )
        
        # Inherited from BaseServerInfo
        assert hasattr(server, 'server_id')
        assert hasattr(server, 'created_at')
        
        # Inherited from MCPServerInfo
        assert hasattr(server, 'source')
        assert hasattr(server, 'transport')
        assert hasattr(server, 'tools')
        assert hasattr(server, 'managed_by_plugin')
        
        # Specialized in DownloadedServerInfo
        assert hasattr(server, 'download_timestamp')
        assert hasattr(server, 'install_command_used')
        assert hasattr(server, 'bulk_install_session')
        assert hasattr(server, 'csv_data_row')
        
        # Source should be frozen to DOWNLOADED
        assert server.source == ServerSource.DOWNLOADED
        
        # Values from factory method
        assert server.server_name == 'test/downloaded-server'
        assert server.repository_url == 'https://github.com/test/downloaded-server'
        assert server.stars == 100
        assert server.language == 'JavaScript'
        assert server.install_command_used == 'npx -y downloaded-server'
        assert server.bulk_install_session == "test-session-123"
    
    def test_server_method_inheritance(self):
        """Test that server methods are properly inherited."""
        server = MCPServerInfo(
            server_id="test-server",
            server_name="Test Server",
            source=ServerSource.DOWNLOADED,
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(command="test"),
            managed_by_plugin="test"
        )
        
        # Methods from BaseServerInfo
        from haive.dataflow.platform.models import ServerStatus, HealthStatus
        server.update_status(ServerStatus.ACTIVE)
        assert server.status == ServerStatus.ACTIVE
        
        server.update_health_status(HealthStatus.HEALTHY)
        assert server.health_status == HealthStatus.HEALTHY
        
        summary = server.get_server_summary()
        assert summary["server_id"] == "test-server"
        assert summary["status"] == ServerStatus.ACTIVE
        
        # Methods from MCPServerInfo
        server.record_connection_attempt(success=True)
        assert server.connection_attempts == 1
        assert server.successful_connections == 1
        assert server.connection_success_rate == 1.0
        
        server.record_connection_attempt(success=False)
        assert server.connection_attempts == 2
        assert server.successful_connections == 1
        assert server.connection_success_rate == 0.5
        
        capabilities = server.get_mcp_capabilities_summary()
        assert capabilities["transport"] == MCPTransport.STDIO
        assert capabilities["source"] == ServerSource.DOWNLOADED
        assert capabilities["connection_success_rate"] == 0.5


class TestInheritanceValidationUtilities:
    """Test inheritance validation utility functions."""
    
    def test_platform_inheritance_validation(self):
        """Test platform inheritance validation utility."""
        # Test BasePlatform
        base_platform = BasePlatform(
            platform_id="base",
            platform_name="Base",
            description="Base platform"
        )
        
        result = validate_platform_inheritance(base_platform)
        assert result["is_base_platform"] is True
        assert result["is_mcp_platform"] is False
        assert result["is_plugin_platform"] is False
        assert result["platform_type"] == "BasePlatform"
        assert result["platform_id"] == "base"
        assert "BasePlatform" in result["inheritance_chain"]
        
        # Test MCPPlatform
        mcp_platform = MCPPlatform()
        
        result = validate_platform_inheritance(mcp_platform)
        assert result["is_base_platform"] is True  # Should be True (inheritance)
        assert result["is_mcp_platform"] is True
        assert result["is_plugin_platform"] is False
        assert result["platform_type"] == "MCPPlatform"
        assert "BasePlatform" in result["inheritance_chain"]
        assert "MCPPlatform" in result["inheritance_chain"]
        
        # Test PluginPlatform
        plugin_platform = PluginPlatform(
            platform_id="plugin",
            platform_name="Plugin",
            description="Plugin platform",
            entry_point="test:Plugin",
            routes_prefix="/test"
        )
        
        result = validate_platform_inheritance(plugin_platform)
        assert result["is_base_platform"] is True  # Should be True (inheritance)
        assert result["is_mcp_platform"] is False
        assert result["is_plugin_platform"] is True
        assert result["platform_type"] == "PluginPlatform"
        assert "BasePlatform" in result["inheritance_chain"]
        assert "PluginPlatform" in result["inheritance_chain"]
    
    def test_server_inheritance_validation(self):
        """Test server inheritance validation utility."""
        # Test BaseServerInfo
        base_server = BaseServerInfo(
            server_id="base",
            server_name="Base Server"
        )
        
        result = validate_server_inheritance(base_server)
        assert result["is_base_server"] is True
        assert result["is_mcp_server"] is False
        assert result["is_downloaded_server"] is False
        assert result["server_type"] == "BaseServerInfo"
        assert result["server_id"] == "base"
        assert result["inheritance_depth"] == 1
        assert "BaseServerInfo" in result["inheritance_chain"]
        
        # Test MCPServerInfo
        mcp_server = MCPServerInfo(
            server_id="mcp",
            server_name="MCP Server",
            source=ServerSource.REGISTRY,
            transport=MCPTransport.HTTP,
            connection_config=ConnectionConfig(url="http://test"),
            managed_by_plugin="test"
        )
        
        result = validate_server_inheritance(mcp_server)
        assert result["is_base_server"] is True  # Should be True (inheritance)
        assert result["is_mcp_server"] is True
        assert result["is_downloaded_server"] is False
        assert result["server_type"] == "MCPServerInfo"
        assert result["inheritance_depth"] == 2
        assert "BaseServerInfo" in result["inheritance_chain"]
        assert "MCPServerInfo" in result["inheritance_chain"]
        
        # Test DownloadedServerInfo
        downloaded_server = DownloadedServerInfo(
            server_id="downloaded",
            server_name="Downloaded Server",
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(command="test"),
            managed_by_plugin="test"
        )
        
        result = validate_server_inheritance(downloaded_server)
        assert result["is_base_server"] is True    # Should be True (inheritance)
        assert result["is_mcp_server"] is True     # Should be True (inheritance)
        assert result["is_downloaded_server"] is True
        assert result["server_type"] == "DownloadedServerInfo"
        assert result["inheritance_depth"] == 3  # Base -> MCP -> Downloaded
        assert "BaseServerInfo" in result["inheritance_chain"]
        assert "MCPServerInfo" in result["inheritance_chain"]
        assert "DownloadedServerInfo" in result["inheritance_chain"]


class TestCrossInheritanceFunctionality:
    """Test functionality that crosses inheritance boundaries."""
    
    def test_platform_with_multiple_plugin_types(self):
        """Test platform can handle multiple inherited plugin types."""
        from haive.dataflow.platform.models import PluginConfig
        
        platform = MCPPlatform(
            plugins=[
                PluginConfig(
                    name="mcp-browser",
                    entry_point="haive.mcp:MCPBrowserPlugin"
                ),
                PluginConfig(
                    name="hap-agents",
                    entry_point="haive.agp:HAPPlugin"
                )
            ]
        )
        
        assert len(platform.plugins) == 2
        assert platform.supports_server_management is True
        assert platform.supports_bulk_operations is True
        
        # Both inheritance chains should work
        assert isinstance(platform, BasePlatform)  # Base inheritance
        assert isinstance(platform, MCPPlatform)   # Specialized inheritance
        
        # Methods from both levels should work
        platform.add_metadata("test", "value")    # From BasePlatform
        assert platform.get_plugin("mcp-browser") is not None  # From MCPPlatform
    
    def test_cross_inheritance_method_interaction(self):
        """Test that methods from different inheritance levels work together."""
        plugin = PluginPlatform(
            platform_id="test-plugin",
            platform_name="Test Plugin",
            description="Cross-inheritance test",
            entry_point="test:Plugin",
            routes_prefix="/test",
            provides_servers=True,
            provides_discovery=True
        )
        
        # Test interaction between base and specialized methods
        # Base platform method
        plugin.add_metadata("plugin_type", "test")
        
        # Plugin platform method
        plugin_info = plugin.get_plugin_info()
        
        # Should contain data from both inheritance levels
        assert plugin_info["basic_info"]["platform_id"] == "test-plugin"  # Base data
        assert plugin_info["plugin_config"]["entry_point"] == "test:Plugin"  # Plugin data
        assert plugin_info["capabilities"]["provides_servers"] is True  # Plugin capability
        assert plugin_info["inheritance_info"]["platform_metadata"]["plugin_type"] == "test"  # Base metadata
    
    def test_inheritance_with_real_world_scenario(self):
        """Test inheritance with realistic usage scenario."""
        # Create MCP platform with real configuration
        platform = MCPPlatform(
            platform_id="production-mcp",
            platform_name="Production MCP Platform",
            description="Production MCP management system"
        )
        
        # Use base platform capabilities
        platform.update_status(PlatformStatus.STARTING)
        platform.add_metadata("environment", "production")
        platform.add_metadata("region", "us-east-1")
        
        # Use MCP-specific capabilities
        from haive.dataflow.platform.models import PluginConfig
        
        browser_plugin = PluginConfig(
            name="mcp-browser",
            entry_point="haive.mcp.plugins:MCPBrowserPlugin",
            enabled=True
        )
        platform.add_plugin(browser_plugin)
        
        # Test that everything works together
        assert platform.status == PlatformStatus.STARTING  # Base functionality
        assert len(platform.plugins) == 1  # MCP functionality
        assert platform.supports_server_management is True  # MCP capability
        
        # Get comprehensive summary using both inheritance levels
        base_summary = platform.get_capability_summary()  # Base method
        mcp_summary = platform.get_mcp_capability_summary()  # MCP method
        
        # Should have capabilities from both levels
        assert base_summary["discovery"] is True
        assert mcp_summary["server_management"] is True
        
        # Inheritance validation should work
        inheritance_result = validate_platform_inheritance(platform)
        assert inheritance_result["is_base_platform"] is True
        assert inheritance_result["is_mcp_platform"] is True
        assert len(inheritance_result["inheritance_chain"]) >= 2