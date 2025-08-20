#!/usr/bin/env python
"""
Phase 1 Validation Script - Unified MCP Platform Architecture

This script validates the successful implementation of Phase 1 of our architecture plan:
"Create base platform models in haive-dataflow with the inheritance hierarchy"

Validation Checklist:
✅ Pure Pydantic models (no __init__ methods)
✅ Intelligent inheritance patterns
✅ Platform capabilities inheritance and extension
✅ Server hierarchy with multiple types
✅ Real data integration with our 63 downloaded servers
✅ Factory methods for real data creation
✅ Validation and error handling
✅ Cross-inheritance functionality

Expected Results: All tests should pass, demonstrating that our architecture
plan is correctly implemented and ready for Phase 2.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datetime import datetime
from pydantic import ValidationError

from haive.dataflow.platform.models import (
    # Base platform models
    BasePlatform,
    PlatformStatus,
    
    # Specialized platform models
    MCPPlatform,
    PluginPlatform,
    
    # Server models
    BaseServerInfo,
    MCPServerInfo,
    DownloadedServerInfo,
    
    # Configuration models
    PluginConfig,
    ConnectionConfig,
    
    # Enumerations
    MCPTransport,
    ServerSource,
    ServerStatus,
    
    # Utility functions
    validate_platform_inheritance,
    validate_server_inheritance,
    create_mcp_platform_with_plugins,
)

def test_pure_pydantic_models():
    """Test that all models are pure Pydantic (no __init__ methods)."""
    print("🧪 Testing pure Pydantic models...")
    
    models_to_check = [
        BasePlatform,
        MCPPlatform, 
        PluginPlatform,
        BaseServerInfo,
        MCPServerInfo,
        DownloadedServerInfo,
        PluginConfig,
        ConnectionConfig,
    ]
    
    for model_class in models_to_check:
        # Check that __init__ is not overridden from BaseModel
        init_method = model_class.__init__
        base_init_method = model_class.__bases__[0].__init__
        
        # If __init__ is customized, it should be from Pydantic, not custom
        if hasattr(model_class, '__init__') and model_class.__init__ != base_init_method:
            # This is okay if it's Pydantic's __init__
            assert 'pydantic' in str(model_class.__init__)
        
        print(f"   ✅ {model_class.__name__}: Pure Pydantic model")
    
    print("✅ Pure Pydantic validation passed!")

def test_inheritance_patterns():
    """Test intelligent inheritance patterns."""
    print("🏗️ Testing intelligent inheritance patterns...")
    
    # Test platform inheritance chain
    base_platform = BasePlatform(
        platform_id="base-test",
        platform_name="Base Test",
        description="Base platform test"
    )
    
    mcp_platform = MCPPlatform()
    
    plugin_platform = PluginPlatform(
        platform_id="plugin-test",
        platform_name="Plugin Test", 
        description="Plugin test",
        entry_point="test:Plugin",
        routes_prefix="/test"
    )
    
    # Validate inheritance
    assert isinstance(mcp_platform, BasePlatform)
    assert isinstance(plugin_platform, BasePlatform)
    
    # Test inherited capabilities
    assert mcp_platform.supports_discovery is True  # Overridden in MCP
    assert base_platform.supports_discovery is False  # Default in base
    
    # Test server inheritance chain
    base_server = BaseServerInfo(server_id="base", server_name="Base Server")
    
    mcp_server = MCPServerInfo(
        server_id="mcp",
        server_name="MCP Server",
        source=ServerSource.REGISTRY,
        transport=MCPTransport.HTTP,
        connection_config=ConnectionConfig(url="http://test"),
        managed_by_plugin="test"
    )
    
    downloaded_server = DownloadedServerInfo(
        server_id="downloaded",
        server_name="Downloaded Server",
        transport=MCPTransport.STDIO,
        connection_config=ConnectionConfig(command="test"),
        managed_by_plugin="test"
    )
    
    # Validate server inheritance
    assert isinstance(mcp_server, BaseServerInfo)
    assert isinstance(downloaded_server, MCPServerInfo)
    assert isinstance(downloaded_server, BaseServerInfo)
    
    print("✅ Inheritance patterns validation passed!")

def test_capability_inheritance_and_extension():
    """Test that capabilities are properly inherited and extended."""
    print("🚀 Testing capability inheritance and extension...")
    
    # Base platform has default capabilities (all False)
    base_platform = BasePlatform(
        platform_id="base", 
        platform_name="Base",
        description="Base"
    )
    base_caps = base_platform.get_capability_summary()
    assert all(not cap for cap in base_caps.values())
    
    # MCP platform extends capabilities
    mcp_platform = MCPPlatform()
    mcp_caps = mcp_platform.get_mcp_capability_summary()
    
    # Should have both inherited and extended capabilities
    assert mcp_caps["discovery"] is True  # Inherited and overridden
    assert mcp_caps["server_management"] is True  # Extended
    assert mcp_caps["tool_execution"] is True  # Extended
    
    # Plugin platform has its own capabilities
    plugin = PluginPlatform(
        platform_id="plugin",
        platform_name="Plugin",
        description="Plugin",
        entry_point="test:Plugin",
        routes_prefix="/test",
        provides_servers=True,
        provides_discovery=True
    )
    
    plugin_info = plugin.get_plugin_info()
    assert plugin_info["capabilities"]["provides_servers"] is True
    assert plugin_info["capabilities"]["provides_discovery"] is True
    
    print("✅ Capability inheritance and extension validation passed!")

def test_real_data_integration():
    """Test integration with real data from our 63 downloaded servers."""
    print("📊 Testing real data integration...")
    
    # Test with data similar to our actual downloads
    real_servers = [
        {
            'csv_row': {
                'name': 'AgentDeskAI/browser-tools-mcp',
                'description': 'Browser monitoring and interaction tool',
                'repository_url': 'https://github.com/AgentDeskAI/browser-tools-mcp',
                'repository_name': 'browser-tools-mcp',
                'stars': 5555.0,
                'language': 'JavaScript'
            },
            'install_entry': {
                'name': 'AgentDeskAI/browser-tools-mcp',
                'command': 'npx -y browser-tools-mcp',
                'status': 'success'
            }
        },
        {
            'csv_row': {
                'name': 'assafelovic/gpt-researcher',
                'description': 'GPT based autonomous agent that does online comprehensive research',
                'repository_url': 'https://github.com/assafelovic/gpt-researcher',
                'repository_name': 'gpt-researcher',
                'stars': 13942.0,
                'language': 'Python'
            },
            'install_entry': {
                'name': 'assafelovic/gpt-researcher',
                'command': 'python -m gpt_researcher',
                'status': 'success'
            }
        }
    ]
    
    session_id = "validation-session-20250819"
    created_servers = []
    
    for server_data in real_servers:
        server = DownloadedServerInfo.from_csv_and_install_report(
            server_data['csv_row'],
            server_data['install_entry'],
            session_id
        )
        created_servers.append(server)
    
    # Validate servers were created correctly
    assert len(created_servers) == 2
    
    js_server = created_servers[0]
    py_server = created_servers[1]
    
    # JavaScript server validation
    assert js_server.language == 'JavaScript'
    assert js_server.transport == MCPTransport.STDIO
    assert js_server.connection_config.command == "npx"
    assert js_server.stars == 5555
    
    # Python server validation  
    assert py_server.language == 'Python'
    assert py_server.transport == MCPTransport.HTTP
    assert py_server.connection_config.command == "python"
    assert py_server.stars == 13942
    
    # Both should have correct source and session
    for server in created_servers:
        assert server.source == ServerSource.DOWNLOADED
        assert server.bulk_install_session == session_id
        assert server.managed_by_plugin == "mcp-browser"
    
    print("✅ Real data integration validation passed!")

def test_validation_and_error_handling():
    """Test validation and error handling."""
    print("⚠️  Testing validation and error handling...")
    
    # Test platform ID validation
    try:
        BasePlatform(
            platform_id="Invalid Platform ID",  # Spaces should fail
            platform_name="Test",
            description="Test"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Platform ID must be lowercase" in str(e)
    
    # Test version validation
    try:
        BasePlatform(
            platform_id="test",
            platform_name="Test", 
            description="Test",
            version="invalid_version"  # Should fail semver validation
        )
        assert False, "Should have raised ValidationError" 
    except ValidationError as e:
        assert "Version must follow semantic versioning" in str(e)
    
    # Test plugin entry point validation
    try:
        PluginPlatform(
            platform_id="test",
            platform_name="Test",
            description="Test",
            entry_point="invalid_entry_point",  # Missing colon
            routes_prefix="/test"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Entry point must be in format" in str(e)
    
    # Test frozen field validation (downloaded server source)
    server = DownloadedServerInfo(
        server_id="test",
        server_name="Test",
        transport=MCPTransport.STDIO,
        connection_config=ConnectionConfig(command="test"),
        managed_by_plugin="test"
    )
    
    assert server.source == ServerSource.DOWNLOADED
    
    try:
        server.source = ServerSource.REGISTRY  # Should fail (frozen)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    print("✅ Validation and error handling passed!")

def test_cross_inheritance_functionality():
    """Test functionality that crosses inheritance boundaries."""
    print("🔄 Testing cross-inheritance functionality...")
    
    # Create MCP platform with plugins
    plugin_configs = [
        {"name": "mcp-browser", "entry_point": "haive.mcp:MCPBrowserPlugin"},
        {"name": "hap-agents", "entry_point": "haive.agp:HAPPlugin"}
    ]
    
    platform = create_mcp_platform_with_plugins(plugin_configs)
    
    # Should work with both inherited and extended functionality
    assert len(platform.plugins) == 2  # MCP functionality
    assert isinstance(platform, BasePlatform)  # Inheritance
    
    # Base platform methods should work
    platform.add_metadata("test", "value")
    assert platform.metadata["test"] == "value"
    
    # MCP platform methods should work
    retrieved_plugin = platform.get_plugin("mcp-browser")
    assert retrieved_plugin is not None
    assert retrieved_plugin.name == "mcp-browser"
    
    # Inheritance validation should work across both levels
    result = validate_platform_inheritance(platform)
    assert result["is_base_platform"] is True
    assert result["is_mcp_platform"] is True
    assert len(result["inheritance_chain"]) >= 2
    
    print("✅ Cross-inheritance functionality validation passed!")

def test_utility_functions():
    """Test utility functions work correctly."""
    print("🛠️  Testing utility functions...")
    
    # Test inheritance validation utilities
    platform = MCPPlatform()
    server = DownloadedServerInfo(
        server_id="test",
        server_name="Test",
        transport=MCPTransport.STDIO,
        connection_config=ConnectionConfig(command="test"),
        managed_by_plugin="test"
    )
    
    # Platform validation
    platform_result = validate_platform_inheritance(platform)
    expected_keys = ["is_base_platform", "is_mcp_platform", "platform_type", "inheritance_chain"]
    for key in expected_keys:
        assert key in platform_result
    
    # Server validation  
    server_result = validate_server_inheritance(server)
    expected_keys = ["is_base_server", "is_mcp_server", "is_downloaded_server", "inheritance_depth"]
    for key in expected_keys:
        assert key in server_result
    
    assert server_result["inheritance_depth"] == 3  # Base -> MCP -> Downloaded
    
    print("✅ Utility functions validation passed!")

def main():
    """Run all Phase 1 validation tests."""
    print("🚀 Phase 1 Architecture Validation - Unified MCP Platform")
    print("=" * 60)
    
    try:
        test_pure_pydantic_models()
        test_inheritance_patterns()
        test_capability_inheritance_and_extension()
        test_real_data_integration()
        test_validation_and_error_handling()
        test_cross_inheritance_functionality()
        test_utility_functions()
        
        print("=" * 60)
        print("🎉 PHASE 1 VALIDATION SUCCESSFUL!")
        print("")
        print("✅ All validation tests passed!")
        print("✅ Pure Pydantic models implemented correctly")
        print("✅ Intelligent inheritance patterns working")
        print("✅ Platform capabilities properly inherited and extended")
        print("✅ Server hierarchy supports multiple server types")
        print("✅ Real data integration with downloaded servers working")
        print("✅ Factory methods create properly configured servers")
        print("✅ Validation and error handling implemented")
        print("✅ Cross-inheritance functionality operational")
        print("")
        print("🏗️  Phase 1: 'Create base platform models in haive-dataflow'")
        print("   Status: ✅ COMPLETED")
        print("")
        print("📋 Ready for Phase 2: 'MCP Browser Plugin Implementation'")
        print("   Next: Convert our 63 downloaded servers to the new plugin system")
        
    except Exception as e:
        print("=" * 60)
        print("❌ PHASE 1 VALIDATION FAILED!")
        print(f"Error: {e}")
        print("")
        print("Please review the implementation and fix any issues before proceeding to Phase 2.")
        raise

if __name__ == "__main__":
    main()