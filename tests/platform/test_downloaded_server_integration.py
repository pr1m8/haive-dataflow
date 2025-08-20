# haive-dataflow/tests/platform/test_downloaded_server_integration.py
"""
Test Downloaded Server Integration with Real Data

This test module validates the DownloadedServerInfo model with real data from our
63 downloaded MCP servers, testing the factory methods and integration patterns.

Test Categories:
1. Factory method validation with real CSV data
2. Connection configuration generation
3. Transport determination logic
4. Integration with install reports
5. Real-world server creation scenarios
"""

import pytest
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from haive.dataflow.platform.models import (
    DownloadedServerInfo,
    MCPTransport,
    ServerSource,
    ConnectionConfig,
    validate_server_inheritance,
)


class TestDownloadedServerFromRealData:
    """Test downloaded server model with real data from our bulk download."""
    
    def test_downloaded_server_from_real_csv_data(self):
        """Test creating server from our actual CSV data."""
        # Sample data from our real CSV (based on successful downloads)
        csv_row = {
            'name': 'AgentDeskAI/browser-tools-mcp',
            'description': 'Browser monitoring and interaction tool',
            'repository_url': 'https://github.com/AgentDeskAI/browser-tools-mcp',
            'repository_name': 'browser-tools-mcp',
            'stars': 5555.0,
            'language': 'JavaScript'
        }
        
        install_entry = {
            'name': 'AgentDeskAI/browser-tools-mcp',
            'command': 'npx -y browser-tools-mcp',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "bulk-session-20250819"
        )
        
        # Validate basic information
        assert server.server_name == 'AgentDeskAI/browser-tools-mcp'
        assert server.server_id == 'AgentDeskAI-browser-tools-mcp'  # Slash replaced with dash
        assert server.description == 'Browser monitoring and interaction tool'
        assert server.source == ServerSource.DOWNLOADED  # Should be frozen
        assert server.repository_url == 'https://github.com/AgentDeskAI/browser-tools-mcp'
        assert server.stars == 5555
        assert server.language == 'JavaScript'
        assert server.install_command_used == 'npx -y browser-tools-mcp'
        assert server.bulk_install_session == "bulk-session-20250819"
        
        # Validate transport determination for JavaScript
        assert server.transport == MCPTransport.STDIO  # JS/TS default
        
        # Validate connection configuration
        assert server.connection_config.command == "npx"
        assert server.connection_config.args == ["-y", "browser-tools-mcp"]
        assert server.connection_config.timeout == 30
        
        # Validate CSV data is preserved
        assert server.csv_data_row == csv_row
        assert server.managed_by_plugin == "mcp-browser"
    
    def test_python_server_configuration(self):
        """Test server configuration for Python-based servers."""
        csv_row = {
            'name': 'example/python-mcp-server',
            'description': 'Python MCP server implementation',
            'repository_url': 'https://github.com/example/python-mcp-server',
            'repository_name': 'python-mcp-server',
            'stars': 250.0,
            'language': 'Python'
        }
        
        install_entry = {
            'name': 'example/python-mcp-server',
            'command': 'python -m python_mcp_server',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "test-session"
        )
        
        # Python servers should use HTTP transport
        assert server.transport == MCPTransport.HTTP
        assert server.language == 'Python'
        
        # Connection config for Python
        assert server.connection_config.command == "python"
        assert server.connection_config.args == ["-m", "python_mcp_server"]
    
    def test_unknown_language_fallback(self):
        """Test fallback behavior for unknown languages."""
        csv_row = {
            'name': 'example/go-server',
            'description': 'Go-based server',
            'repository_url': 'https://github.com/example/go-server',
            'repository_name': 'go-server',
            'stars': 100.0,
            'language': 'Go'
        }
        
        install_entry = {
            'name': 'example/go-server',
            'command': 'echo "Server not configured"',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "test-session"
        )
        
        # Unknown language should default to stdio
        assert server.transport == MCPTransport.STDIO
        
        # Should have fallback connection config
        assert server.connection_config.command == "echo"
        assert server.connection_config.args == ["Server not configured - needs manual setup"]
        assert server.connection_config.timeout == 10
    
    def test_missing_language_handling(self):
        """Test handling of missing language field."""
        csv_row = {
            'name': 'example/no-language-server',
            'description': 'Server without language specified',
            'repository_url': 'https://github.com/example/no-language-server',
            'repository_name': 'no-language-server',
            'stars': None,  # Also test None stars
            # language field missing
        }
        
        install_entry = {
            'name': 'example/no-language-server',
            'command': 'echo "test"',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "test-session"
        )
        
        # Should handle missing language gracefully
        assert server.transport == MCPTransport.STDIO  # Default
        assert server.language is None
        assert server.stars is None
    
    def test_nan_values_handling(self):
        """Test handling of NaN values from pandas/CSV."""
        import numpy as np
        
        csv_row = {
            'name': 'example/nan-server',
            'description': 'Server with NaN values',
            'repository_url': 'https://github.com/example/nan-server',
            'repository_name': 'nan-server',
            'stars': np.nan,  # NaN value
            'language': 'JavaScript'
        }
        
        install_entry = {
            'name': 'example/nan-server',
            'command': 'npx -y nan-server',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "test-session"
        )
        
        # NaN should be converted to None
        assert server.stars is None
        assert server.language == 'JavaScript'  # Regular value should work
        
        # Other fields should work normally
        assert server.transport == MCPTransport.STDIO
        assert server.server_name == 'example/nan-server'


class TestConnectionConfigGeneration:
    """Test connection configuration generation logic."""
    
    def test_javascript_connection_config(self):
        """Test connection config for JavaScript servers."""
        csv_row = {
            'name': 'test/js-server',
            'repository_name': 'js-server',
            'language': 'JavaScript'
        }
        
        config = DownloadedServerInfo._create_connection_config_from_csv(csv_row)
        
        assert config.command == "npx"
        assert config.args == ["-y", "js-server"]
        assert config.timeout == 30
        assert config.is_command_based() is True
        assert config.is_url_based() is False
    
    def test_typescript_connection_config(self):
        """Test connection config for TypeScript servers."""
        csv_row = {
            'name': 'test/ts-server',
            'repository_name': 'ts-server',
            'language': 'TypeScript'
        }
        
        config = DownloadedServerInfo._create_connection_config_from_csv(csv_row)
        
        assert config.command == "npx"
        assert config.args == ["-y", "ts-server"]
        assert config.timeout == 30
    
    def test_python_connection_config(self):
        """Test connection config for Python servers."""
        csv_row = {
            'name': 'test/python-server',
            'repository_name': 'python-server',
            'language': 'Python'
        }
        
        config = DownloadedServerInfo._create_connection_config_from_csv(csv_row)
        
        assert config.command == "python"
        assert config.args == ["-m", "python_server"]  # Hyphens replaced with underscores
        assert config.timeout == 30
    
    def test_fallback_connection_config(self):
        """Test fallback connection config for unknown languages."""
        csv_row = {
            'name': 'test/unknown-server',
            'repository_name': 'unknown-server',
            'language': 'Rust'
        }
        
        config = DownloadedServerInfo._create_connection_config_from_csv(csv_row)
        
        assert config.command == "echo"
        assert config.args == ["Server not configured - needs manual setup"]
        assert config.timeout == 10


class TestTransportDetermination:
    """Test transport protocol determination logic."""
    
    def test_transport_for_javascript(self):
        """Test transport determination for JavaScript."""
        transport = DownloadedServerInfo._determine_transport_from_language("JavaScript")
        assert transport == MCPTransport.STDIO
        
        transport = DownloadedServerInfo._determine_transport_from_language("javascript")
        assert transport == MCPTransport.STDIO
    
    def test_transport_for_typescript(self):
        """Test transport determination for TypeScript."""
        transport = DownloadedServerInfo._determine_transport_from_language("TypeScript")
        assert transport == MCPTransport.STDIO
        
        transport = DownloadedServerInfo._determine_transport_from_language("typescript")
        assert transport == MCPTransport.STDIO
    
    def test_transport_for_python(self):
        """Test transport determination for Python."""
        transport = DownloadedServerInfo._determine_transport_from_language("Python")
        assert transport == MCPTransport.HTTP
        
        transport = DownloadedServerInfo._determine_transport_from_language("python")
        assert transport == MCPTransport.HTTP
    
    def test_transport_for_unknown_language(self):
        """Test transport determination for unknown languages."""
        transport = DownloadedServerInfo._determine_transport_from_language("Go")
        assert transport == MCPTransport.STDIO
        
        transport = DownloadedServerInfo._determine_transport_from_language("Rust")
        assert transport == MCPTransport.STDIO
        
        transport = DownloadedServerInfo._determine_transport_from_language("Unknown")
        assert transport == MCPTransport.STDIO
    
    def test_transport_for_none_language(self):
        """Test transport determination when language is None."""
        transport = DownloadedServerInfo._determine_transport_from_language(None)
        assert transport == MCPTransport.STDIO
        
        transport = DownloadedServerInfo._determine_transport_from_language("")
        assert transport == MCPTransport.STDIO


class TestServerIntegrationMethods:
    """Test integration methods and functionality."""
    
    def test_download_summary_generation(self):
        """Test download summary with comprehensive information."""
        csv_row = {
            'name': 'test/comprehensive-server',
            'description': 'Comprehensive test server',
            'repository_url': 'https://github.com/test/comprehensive-server',
            'repository_name': 'comprehensive-server',
            'stars': 999.0,
            'language': 'JavaScript'
        }
        
        install_entry = {
            'name': 'test/comprehensive-server',
            'command': 'npx -y comprehensive-server',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "comprehensive-session"
        )
        
        # Add some additional data
        server.readme_content = "# Comprehensive Server\nThis is a test server."
        server.detected_tools = ["tool1", "tool2", "tool3"]
        
        summary = server.get_download_summary()
        
        # Validate structure
        assert "download_info" in summary
        assert "source_data" in summary
        assert "repository_info" in summary
        assert "connection_info" in summary
        assert "inherited_info" in summary
        
        # Validate download info
        download_info = summary["download_info"]
        assert download_info["bulk_install_session"] == "comprehensive-session"
        assert download_info["install_command_used"] == "npx -y comprehensive-server"
        
        # Validate source data
        source_data = summary["source_data"]
        assert source_data["has_csv_data"] is True
        assert source_data["has_readme"] is True
        assert source_data["detected_tools_count"] == 3
        
        # Validate repository info
        repo_info = summary["repository_info"]
        assert repo_info["repository_url"] == 'https://github.com/test/comprehensive-server'
        assert repo_info["stars"] == 999
        assert repo_info["language"] == 'JavaScript'
        
        # Validate connection info
        connection_info = summary["connection_info"]
        assert connection_info["type"] == "command"
        assert connection_info["command"] == "npx"
        
        # Validate inherited MCP capabilities
        inherited_info = summary["inherited_info"]
        assert inherited_info["transport"] == MCPTransport.STDIO
        assert inherited_info["source"] == ServerSource.DOWNLOADED
        assert inherited_info["managed_by"] == "mcp-browser"
    
    def test_inheritance_validation_with_downloaded_server(self):
        """Test inheritance validation specifically for downloaded servers."""
        server = DownloadedServerInfo(
            server_id="inheritance-test",
            server_name="Inheritance Test Server",
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(command="test"),
            managed_by_plugin="test-plugin"
        )
        
        # Test inheritance validation
        result = validate_server_inheritance(server)
        
        assert result["is_base_server"] is True      # From BaseServerInfo
        assert result["is_mcp_server"] is True       # From MCPServerInfo  
        assert result["is_downloaded_server"] is True # From DownloadedServerInfo
        assert result["server_type"] == "DownloadedServerInfo"
        assert result["inheritance_depth"] == 3     # Three levels deep
        
        # Check inheritance chain
        chain = result["inheritance_chain"]
        assert "BaseServerInfo" in chain
        assert "MCPServerInfo" in chain  
        assert "DownloadedServerInfo" in chain
    
    def test_frozen_source_field(self):
        """Test that source field is frozen to DOWNLOADED."""
        server = DownloadedServerInfo(
            server_id="frozen-test",
            server_name="Frozen Test Server",
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(command="test"),
            managed_by_plugin="test"
        )
        
        # Source should be DOWNLOADED by default
        assert server.source == ServerSource.DOWNLOADED
        
        # Should not be able to change it (Pydantic frozen field)
        with pytest.raises(ValidationError):
            server.source = ServerSource.REGISTRY
    
    def test_connection_success_rate_tracking(self):
        """Test connection success rate tracking inherited from MCPServerInfo."""
        server = DownloadedServerInfo(
            server_id="connection-test",
            server_name="Connection Test Server", 
            transport=MCPTransport.STDIO,
            connection_config=ConnectionConfig(command="test"),
            managed_by_plugin="test"
        )
        
        # Initially no connections
        assert server.connection_success_rate == 0.0
        
        # Record some attempts
        server.record_connection_attempt(success=True)
        server.record_connection_attempt(success=True)
        server.record_connection_attempt(success=False)
        
        # Should calculate correctly
        assert server.connection_attempts == 3
        assert server.successful_connections == 2
        assert server.connection_success_rate == 2/3
        
        # Download summary should include this data
        summary = server.get_download_summary()
        assert summary["inherited_info"]["connection_success_rate"] == 2/3


class TestRealWorldIntegrationScenarios:
    """Test real-world scenarios based on our actual downloaded servers."""
    
    def test_high_star_popular_server(self):
        """Test creating server for high-star popular repository."""
        # Based on n8n (workflow automation)
        csv_row = {
            'name': 'n8n-io/n8n',
            'description': 'Free and source-available fair-code licensed workflow automation tool',
            'repository_url': 'https://github.com/n8n-io/n8n',
            'repository_name': 'n8n',
            'stars': 44234.0,  # Very high star count
            'language': 'TypeScript'
        }
        
        install_entry = {
            'name': 'n8n-io/n8n',
            'command': 'npx -y n8n',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "bulk-popular-20250819"
        )
        
        assert server.server_name == 'n8n-io/n8n'
        assert server.stars == 44234  # High star count should be preserved
        assert server.language == 'TypeScript'
        assert server.transport == MCPTransport.STDIO  # TypeScript uses stdio
        assert server.connection_config.command == "npx"
        assert server.connection_config.args == ["-y", "n8n"]
    
    def test_ai_research_server(self):
        """Test creating server for AI research repository."""
        # Based on gpt-researcher
        csv_row = {
            'name': 'assafelovic/gpt-researcher',
            'description': 'GPT based autonomous agent that does online comprehensive research',
            'repository_url': 'https://github.com/assafelovic/gpt-researcher',
            'repository_name': 'gpt-researcher',
            'stars': 13942.0,
            'language': 'Python'
        }
        
        install_entry = {
            'name': 'assafelovic/gpt-researcher',
            'command': 'python -m gpt_researcher',
            'status': 'success'
        }
        
        server = DownloadedServerInfo.from_csv_and_install_report(
            csv_row, install_entry, "bulk-ai-research-20250819"
        )
        
        assert server.server_name == 'assafelovic/gpt-researcher'
        assert server.stars == 13942
        assert server.language == 'Python'
        assert server.transport == MCPTransport.HTTP  # Python uses HTTP
        assert server.connection_config.command == "python"
        assert server.connection_config.args == ["-m", "gpt_researcher"]
        
        # AI research servers might have specific metadata
        assert "gpt" in server.description.lower()
        assert "research" in server.description.lower()
    
    def test_batch_server_creation_from_install_report(self):
        """Test creating multiple servers from a batch install report."""
        # Simulate our actual install report structure
        servers_data = [
            {
                'csv_row': {
                    'name': 'test/server1',
                    'description': 'First test server',
                    'repository_url': 'https://github.com/test/server1',
                    'repository_name': 'server1',
                    'stars': 100.0,
                    'language': 'JavaScript'
                },
                'install_entry': {
                    'name': 'test/server1',
                    'command': 'npx -y server1',
                    'status': 'success'
                }
            },
            {
                'csv_row': {
                    'name': 'test/server2', 
                    'description': 'Second test server',
                    'repository_url': 'https://github.com/test/server2',
                    'repository_name': 'server2',
                    'stars': 200.0,
                    'language': 'Python'
                },
                'install_entry': {
                    'name': 'test/server2',
                    'command': 'python -m server2',
                    'status': 'success'
                }
            }
        ]
        
        session_id = "batch-test-20250819"
        created_servers = []
        
        for data in servers_data:
            server = DownloadedServerInfo.from_csv_and_install_report(
                data['csv_row'],
                data['install_entry'], 
                session_id
            )
            created_servers.append(server)
        
        # Validate batch creation
        assert len(created_servers) == 2
        
        # All should have same session ID
        for server in created_servers:
            assert server.bulk_install_session == session_id
            assert server.source == ServerSource.DOWNLOADED
            assert server.managed_by_plugin == "mcp-browser"
        
        # Should have different configurations based on language
        js_server = created_servers[0]
        py_server = created_servers[1]
        
        assert js_server.transport == MCPTransport.STDIO
        assert js_server.connection_config.command == "npx"
        
        assert py_server.transport == MCPTransport.HTTP
        assert py_server.connection_config.command == "python"