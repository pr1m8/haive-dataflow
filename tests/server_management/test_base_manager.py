"""Test generic base server manager functionality."""

import pytest
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field, ValidationError

from haive.dataflow.server_management import (
    BaseServerManager,
    BaseServerConfig,
    BaseServerInfo,
    ServerStatus
)


class TestServerConfig(BaseServerConfig):
    """Test configuration with extra field."""
    test_mode: bool = Field(default=True, description="Test mode flag")
    custom_field: str = Field(default="test", description="Custom test field")


class TestServerInfo(BaseServerInfo):
    """Test info with extra field."""
    test_data: str = Field(default="", description="Test-specific data")


class ConcreteTestManager(BaseServerManager[TestServerConfig, TestServerInfo]):
    """Concrete implementation for testing."""
    
    config_class: type[TestServerConfig] = Field(default=TestServerConfig, exclude=True)
    info_class: type[TestServerInfo] = Field(default=TestServerInfo, exclude=True)
    
    # Track method calls for testing
    start_calls: list = Field(default_factory=list, exclude=True)
    stop_calls: list = Field(default_factory=list, exclude=True)
    
    async def start_server(self, name: str, config: Optional[TestServerConfig] = None) -> TestServerInfo:
        """Test implementation of start_server."""
        self.start_calls.append(name)
        
        # Get config
        if config is None:
            config = self.get_config(name)
            if config is None:
                raise ValueError(f"No configuration found for '{name}'")
        
        # Check if already running
        if name in self.servers:
            raise RuntimeError(f"Server '{name}' is already running")
        
        # Create server info
        info = TestServerInfo(
            name=name,
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot=config.model_dump(),
            test_data=f"Started with {config.custom_field}"
        )
        
        self.servers[name] = info
        
        # Start health monitoring if enabled
        if config.health_check_enabled:
            await self.start_health_monitoring(name)
        
        return info
    
    async def stop_server(self, name: str, force: bool = False) -> bool:
        """Test implementation of stop_server."""
        self.stop_calls.append((name, force))
        
        if name not in self.servers:
            return False
        
        # Stop health monitoring
        await self.stop_health_monitoring(name)
        
        # Update status
        self.servers[name].update_status(ServerStatus.STOPPED)
        
        # Remove from running servers
        del self.servers[name]
        
        return True
    
    async def restart_server(self, name: str) -> TestServerInfo:
        """Test implementation of restart_server."""
        # Stop if running
        if name in self.servers:
            await self.stop_server(name)
        
        # Start again
        return await self.start_server(name)
    
    async def health_check(self, name: str) -> bool:
        """Test implementation of health_check."""
        if name not in self.servers:
            return False
        
        # Simulate health check
        info = self.servers[name]
        healthy = info.status == ServerStatus.RUNNING
        info.record_health_check(healthy)
        
        return healthy


class TestBaseServerManager:
    """Test BaseServerManager functionality."""
    
    @pytest.fixture
    def manager(self):
        """Create test manager instance."""
        return ConcreteTestManager()
    
    @pytest.fixture
    def sample_config(self):
        """Create sample test config."""
        return TestServerConfig(
            name="test-server",
            command=["python", "-m", "test"],
            description="Test server",
            custom_field="sample"
        )
    
    def test_manager_creation(self):
        """Test creating manager with defaults."""
        manager = ConcreteTestManager()
        
        assert manager.servers == {}
        assert manager.available_configs == {}
        assert manager.auto_restart is False
        assert manager.max_restart_attempts == 3
        assert manager.health_check_interval == 60
        assert manager.restart_tracking == {}
    
    def test_manager_with_initial_configs(self):
        """Test creating manager with initial configs."""
        configs = {
            "server1": TestServerConfig(
                name="server1",
                command=["test1"],
                description="Test 1"
            ),
            "server2": TestServerConfig(
                name="server2",
                command=["test2"],
                description="Test 2"
            )
        }
        
        manager = ConcreteTestManager(available_configs=configs)
        
        assert len(manager.available_configs) == 2
        assert "server1" in manager.available_configs
        assert "server2" in manager.available_configs
        assert manager.available_configs["server1"].custom_field == "test"
    
    def test_type_validation(self):
        """Test that config/info types are validated."""
        manager = ConcreteTestManager()
        
        # Correct type works
        config = TestServerConfig(
            name="test",
            command=["test"],
            description="Test"
        )
        manager.add_config("test", config)
        assert isinstance(manager.available_configs["test"], TestServerConfig)
        
        # Wrong config type should be detected when using add_config
        wrong_config = BaseServerConfig(
            name="bad",
            command=["bad"],
            description="Bad type"
        )
        # Since add_config checks type, this should raise TypeError
        with pytest.raises(TypeError) as exc:
            manager.add_config("bad", wrong_config)
        assert "TestServerConfig" in str(exc.value)
    
    def test_config_coercion(self):
        """Test configs can be coerced from dicts."""
        manager = ConcreteTestManager()
        
        # Add config as dict
        config = manager.add_config("test", {
            "command": ["python", "test.py"],
            "description": "Test server"
        })
        
        assert isinstance(config, TestServerConfig)
        assert config.name == "test"
        assert config.test_mode is True  # Default value
        assert config.custom_field == "test"  # Default value
    
    def test_add_remove_config(self, manager, sample_config):
        """Test adding and removing configurations."""
        # Add config
        result = manager.add_config("test", sample_config)
        assert result == sample_config
        assert manager.get_config("test") == sample_config
        
        # Update config
        updated = manager.add_config("test", {
            "command": ["new", "command"],
            "description": "Updated",
            "custom_field": "updated"
        })
        assert updated.custom_field == "updated"
        
        # Remove config
        assert manager.remove_config("test") is True
        assert manager.get_config("test") is None
        
        # Remove non-existent
        assert manager.remove_config("non-existent") is False
    
    def test_cannot_remove_running_server_config(self, manager, sample_config):
        """Test that configs for running servers cannot be removed."""
        manager.add_config("test", sample_config)
        
        # Simulate running server
        manager.servers["test"] = TestServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        
        # Should raise error
        with pytest.raises(RuntimeError) as exc:
            manager.remove_config("test")
        assert "running server" in str(exc.value)
    
    def test_restart_policy_validation(self):
        """Test restart policy validation."""
        # Valid config
        manager = ConcreteTestManager(
            auto_restart=True,
            max_restart_attempts=5
        )
        assert manager.auto_restart is True
        
        # Invalid config
        with pytest.raises(ValidationError) as exc:
            ConcreteTestManager(
                auto_restart=True,
                max_restart_attempts=0
            )
        assert "requires max_restart_attempts > 0" in str(exc.value)
    
    def test_server_consistency_validation(self):
        """Test that orphaned servers get configs created."""
        # Create manager with orphaned server
        manager = ConcreteTestManager(
            servers={
                "orphan": TestServerInfo(
                    name="orphan",
                    pid=12345,
                    status=ServerStatus.RUNNING,
                    config_snapshot={
                        "name": "orphan",
                        "command": ["test"],
                        "description": "Orphaned server"
                    }
                )
            }
        )
        
        # Should auto-create config
        assert "orphan" in manager.available_configs
        assert manager.available_configs["orphan"].name == "orphan"
        assert manager.available_configs["orphan"].command == ["test"]
    
    @pytest.mark.asyncio
    async def test_start_server(self, manager, sample_config):
        """Test starting a server."""
        manager.add_config("test", sample_config)
        
        # Start server
        info = await manager.start_server("test")
        
        assert isinstance(info, TestServerInfo)
        assert info.name == "test"
        assert info.status == ServerStatus.RUNNING
        assert info.test_data == "Started with sample"
        assert "test" in manager.servers
        assert manager.start_calls == ["test"]
    
    @pytest.mark.asyncio
    async def test_start_server_already_running(self, manager, sample_config):
        """Test starting an already running server."""
        manager.add_config("test", sample_config)
        await manager.start_server("test")
        
        # Try to start again
        with pytest.raises(RuntimeError) as exc:
            await manager.start_server("test")
        assert "already running" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_start_server_no_config(self, manager):
        """Test starting server without config."""
        with pytest.raises(ValueError) as exc:
            await manager.start_server("non-existent")
        assert "No configuration found" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_stop_server(self, manager, sample_config):
        """Test stopping a server."""
        manager.add_config("test", sample_config)
        await manager.start_server("test")
        
        # Stop server
        result = await manager.stop_server("test")
        
        assert result is True
        assert "test" not in manager.servers
        assert manager.stop_calls == [("test", False)]
    
    @pytest.mark.asyncio
    async def test_stop_non_existent_server(self, manager):
        """Test stopping non-existent server."""
        result = await manager.stop_server("non-existent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_restart_server(self, manager, sample_config):
        """Test restarting a server."""
        manager.add_config("test", sample_config)
        info1 = await manager.start_server("test")
        
        # Restart
        info2 = await manager.restart_server("test")
        
        assert info2.name == "test"
        assert info2.status == ServerStatus.RUNNING
        assert manager.start_calls == ["test", "test"]  # Started twice
        assert manager.stop_calls == [("test", False)]  # Stopped once
    
    @pytest.mark.asyncio
    async def test_health_check(self, manager, sample_config):
        """Test health check functionality."""
        manager.add_config("test", sample_config)
        await manager.start_server("test")
        
        # Health check should succeed
        result = await manager.health_check("test")
        assert result is True
        
        # Check that health check was recorded
        info = manager.get_server_info("test")
        assert info.last_health_check is not None
    
    def test_is_running(self, manager):
        """Test checking if server is running."""
        # Not running
        assert manager.is_running("test") is False
        
        # Add running server
        manager.servers["test"] = TestServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        assert manager.is_running("test") is True
        
        # Change status
        manager.servers["test"].status = ServerStatus.STOPPED
        assert manager.is_running("test") is False
    
    def test_list_servers(self, manager):
        """Test listing servers by status."""
        # Add servers with different statuses
        manager.servers["running1"] = TestServerInfo(
            name="running1",
            pid=1,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        manager.servers["running2"] = TestServerInfo(
            name="running2",
            pid=2,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        manager.servers["stopped"] = TestServerInfo(
            name="stopped",
            pid=3,
            status=ServerStatus.STOPPED,
            config_snapshot={}
        )
        manager.servers["error"] = TestServerInfo(
            name="error",
            pid=4,
            status=ServerStatus.ERROR,
            config_snapshot={}
        )
        
        # List all
        all_servers = manager.list_servers()
        assert len(all_servers) == 4
        
        # List by status
        running = manager.list_servers(ServerStatus.RUNNING)
        assert set(running) == {"running1", "running2"}
        
        stopped = manager.list_servers(ServerStatus.STOPPED)
        assert stopped == ["stopped"]
        
        errors = manager.list_servers(ServerStatus.ERROR)
        assert errors == ["error"]
    
    def test_get_stats(self, manager):
        """Test getting manager statistics."""
        # Add configs
        manager.add_config("server1", {
            "command": ["test1"],
            "description": "Test 1"
        })
        manager.add_config("server2", {
            "command": ["test2"],
            "description": "Test 2"
        })
        
        # Add running servers
        manager.servers["server1"] = TestServerInfo(
            name="server1",
            pid=1,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        manager.servers["server2"] = TestServerInfo(
            name="server2",
            pid=2,
            status=ServerStatus.ERROR,
            config_snapshot={}
        )
        
        # Set restart counts
        manager.restart_tracking["server1"] = 2
        manager.restart_tracking["server2"] = 5
        
        stats = manager.get_stats()
        
        assert stats["total_configured"] == 2
        assert stats["total_running"] == 2
        assert stats["servers_by_status"] == {
            "running": 1,
            "error": 1
        }
        assert stats["restart_counts"] == {
            "server1": 2,
            "server2": 5
        }
        assert stats["health_check_active"] == 0
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, manager, sample_config):
        """Test health monitoring lifecycle."""
        manager.add_config("test", sample_config)
        
        # Start server (should start monitoring)
        await manager.start_server("test")
        
        # Should have health check task
        assert "test" in manager.health_check_tasks
        
        # Stop server (should stop monitoring)
        await manager.stop_server("test")
        
        # Should not have health check task
        assert "test" not in manager.health_check_tasks
    
    @pytest.mark.asyncio
    async def test_auto_restart_on_health_failure(self):
        """Test auto-restart when health check fails."""
        # Create manager with auto-restart
        manager = ConcreteTestManager(
            auto_restart=True,
            max_restart_attempts=2,
            health_check_interval=10  # Short interval for testing
        )
        
        # Add config and start server
        manager.add_config("test", {
            "command": ["test"],
            "description": "Test"
        })
        await manager.start_server("test")
        
        # Record initial start calls
        initial_start_count = len(manager.start_calls)
        
        # Simulate health check failure
        manager.servers["test"].status = ServerStatus.ERROR
        
        # Manually trigger failure handler
        await manager._handle_server_failure("test")
        
        # Should have attempted restart
        assert len(manager.start_calls) == initial_start_count + 1  # One more start call
        assert manager.start_calls[-1] == "test"  # Restarted correct server
        
        # Restart was successful, so counter should be reset to 0
        assert manager.restart_tracking["test"] == 0
        
        # Server should be running again
        assert "test" in manager.servers
        assert manager.servers["test"].status == ServerStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_max_restart_attempts(self):
        """Test that max restart attempts is respected."""
        manager = ConcreteTestManager(
            auto_restart=True,
            max_restart_attempts=2
        )
        
        manager.add_config("test", {
            "command": ["test"],
            "description": "Test"
        })
        
        # Simulate multiple failures
        manager.restart_tracking["test"] = 2  # Already at max
        
        # Add fake server
        manager.servers["test"] = TestServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        
        # Try to handle failure
        await manager._handle_server_failure("test")
        
        # Should not restart
        assert manager.servers["test"].status == ServerStatus.ERROR
        assert "Exceeded max restart attempts" in manager.servers["test"].error_message
    
    @pytest.mark.asyncio
    async def test_cleanup(self, manager, sample_config):
        """Test cleanup stops all servers."""
        # Start multiple servers
        manager.add_config("server1", sample_config)
        manager.add_config("server2", {
            "command": ["test2"],
            "description": "Test 2"
        })
        
        await manager.start_server("server1")
        await manager.start_server("server2")
        
        # Both should be running
        assert len(manager.servers) == 2
        assert len(manager.health_check_tasks) == 2
        
        # Cleanup
        await manager.cleanup()
        
        # All servers stopped
        assert len(manager.servers) == 0
        assert len(manager.health_check_tasks) == 0
        assert ("server1", True) in manager.stop_calls
        assert ("server2", True) in manager.stop_calls
    
    def test_generic_type_hints(self):
        """Test that generic type hints work properly."""
        manager = ConcreteTestManager()
        
        # Type hints should know the concrete types
        config = manager.add_config("test", {
            "command": ["test"],
            "description": "Test"
        })
        
        # IDE/type checker knows this is TestServerConfig
        assert config.test_mode is True
        assert config.custom_field == "test"
        
        # Same for info
        manager.servers["test"] = TestServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={},
            test_data="specific"
        )
        
        info = manager.get_server_info("test")
        # IDE/type checker knows this is TestServerInfo
        assert info.test_data == "specific"
    
    def test_field_exclusion_in_serialization(self, manager):
        """Test that internal fields are excluded from serialization."""
        # Add some data
        manager.add_config("test", {
            "command": ["test"],
            "description": "Test"
        })
        manager.restart_tracking["test"] = 3
        
        # Serialize
        data = manager.model_dump()
        
        # Check exclusions
        assert "config_class" not in data
        assert "info_class" not in data
        assert "restart_tracking" not in data
        assert "health_check_tasks" not in data
        
        # Check inclusions
        assert "available_configs" in data
        assert "servers" in data
        assert "auto_restart" in data