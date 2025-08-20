"""Test base server management models."""

import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError

from haive.dataflow.server_management.models import (
    ServerStatus,
    BaseServerConfig,
    BaseServerInfo,
)


class TestBaseServerConfig:
    """Test BaseServerConfig validation and behavior."""
    
    def test_valid_config_creation(self):
        """Test creating valid server configuration."""
        config = BaseServerConfig(
            name="test-server",
            command=["python", "-m", "http.server", "8000"],
            description="Test HTTP server"
        )
        
        assert config.name == "test-server"
        assert config.command == ["python", "-m", "http.server", "8000"]
        assert config.description == "Test HTTP server"
        assert config.timeout_seconds == 300  # Default
        assert config.auto_restart is False  # Default
        assert config.health_check_enabled is True  # Default
    
    def test_name_validation(self):
        """Test server name validation rules."""
        # Valid names
        valid_names = ["server1", "test-server", "my_server", "s", "S123"]
        for name in valid_names:
            config = BaseServerConfig(
                name=name,
                command=["test"],
                description="Test"
            )
            assert config.name == name
        
        # Invalid names
        invalid_names = ["", "-server", "_server", "server!", "server name", "123-server-!@#"]
        for name in invalid_names:
            with pytest.raises(ValidationError) as exc:
                BaseServerConfig(
                    name=name,
                    command=["test"],
                    description="Test"
                )
            # Check meaningful error
            assert "name" in str(exc.value).lower()
    
    def test_command_validation(self):
        """Test command validation."""
        # Valid commands
        config = BaseServerConfig(
            name="test",
            command=["python", "-m", "server", "--port", "8000"],
            description="Test"
        )
        assert len(config.command) == 5
        
        # Empty command list
        with pytest.raises(ValidationError) as exc:
            BaseServerConfig(
                name="test",
                command=[],
                description="Test"
            )
        assert "at least 1 item" in str(exc.value)
        
        # Command with empty strings
        with pytest.raises(ValidationError) as exc:
            BaseServerConfig(
                name="test",
                command=["python", "", "server"],
                description="Test"
            )
        assert "empty string" in str(exc.value).lower()
    
    def test_extra_fields_rejected(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc:
            BaseServerConfig(
                name="test",
                command=["test"],
                description="Test",
                unknown_field="should fail"
            )
        assert "Extra inputs are not permitted" in str(exc.value)
    
    def test_environment_validation(self):
        """Test environment variable validation."""
        # Valid environment
        config = BaseServerConfig(
            name="test",
            command=["test"],
            description="Test",
            environment={
                "PATH": "/usr/bin",
                "MY_VAR": "value",
                "NUMBER_123": "456"
            }
        )
        assert len(config.environment) == 3
        
        # Invalid env var names
        with pytest.raises(ValidationError) as exc:
            BaseServerConfig(
                name="test",
                command=["test"],
                description="Test",
                environment={"INVALID-VAR": "value"}
            )
        assert "Invalid environment variable name" in str(exc.value)
    
    def test_timeout_validation(self):
        """Test timeout bounds validation."""
        # Valid timeouts
        config = BaseServerConfig(
            name="test",
            command=["test"],
            description="Test",
            timeout_seconds=60
        )
        assert config.timeout_seconds == 60
        
        # Out of bounds
        with pytest.raises(ValidationError):
            BaseServerConfig(
                name="test",
                command=["test"],
                description="Test",
                timeout_seconds=0  # Too low
            )
        
        with pytest.raises(ValidationError):
            BaseServerConfig(
                name="test",
                command=["test"],
                description="Test",
                timeout_seconds=3601  # Too high
            )
    
    def test_string_stripping(self):
        """Test that strings are stripped of whitespace."""
        config = BaseServerConfig(
            name="  test-server  ",
            command=["python"],
            description="  Test server  "
        )
        assert config.name == "test-server"
        assert config.description == "Test server"


class TestBaseServerInfo:
    """Test BaseServerInfo runtime information model."""
    
    def test_valid_info_creation(self):
        """Test creating valid server info."""
        info = BaseServerInfo(
            name="test-server",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={
                "name": "test-server",
                "command": ["python", "-m", "server"],
                "description": "Test server"
            }
        )
        
        assert info.name == "test-server"
        assert info.pid == 12345
        assert info.status == ServerStatus.RUNNING
        assert info.restart_count == 0
        assert info.error_message is None
        assert isinstance(info.started_at, datetime)
    
    def test_invalid_pid(self):
        """Test PID validation."""
        with pytest.raises(ValidationError):
            BaseServerInfo(
                name="test",
                pid=0,  # Invalid
                status=ServerStatus.RUNNING,
                config_snapshot={}
            )
        
        with pytest.raises(ValidationError):
            BaseServerInfo(
                name="test",
                pid=-1,  # Invalid
                status=ServerStatus.RUNNING,
                config_snapshot={}
            )
    
    def test_is_running_property(self):
        """Test is_running property logic."""
        # Running status
        info = BaseServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        assert info.is_running is True
        
        # Stopped status
        info.status = ServerStatus.STOPPED
        assert info.is_running is False
        
        # Error status
        info.status = ServerStatus.ERROR
        assert info.is_running is False
    
    def test_uptime_calculation(self):
        """Test uptime_seconds property."""
        # Create with specific start time
        start_time = datetime.now(timezone.utc) - timedelta(seconds=123)
        info = BaseServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={},
            started_at=start_time
        )
        
        # Uptime should be approximately 123 seconds
        assert 122 <= info.uptime_seconds <= 124
        
        # Stopped server has 0 uptime
        info.status = ServerStatus.STOPPED
        assert info.uptime_seconds == 0.0
    
    def test_update_status_method(self):
        """Test status update method."""
        info = BaseServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.STARTING,
            config_snapshot={}
        )
        
        # Update to running - clears error
        info.error_message = "old error"
        info.update_status(ServerStatus.RUNNING)
        assert info.status == ServerStatus.RUNNING
        assert info.error_message is None
        
        # Update with error
        info.update_status(ServerStatus.ERROR, "Connection failed")
        assert info.status == ServerStatus.ERROR
        assert info.error_message == "Connection failed"
    
    def test_health_check_recording(self):
        """Test health check recording."""
        info = BaseServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={}
        )
        
        # Successful health check
        info.record_health_check(success=True)
        assert info.last_health_check is not None
        assert info.status == ServerStatus.RUNNING
        
        # Failed health check
        info.record_health_check(success=False)
        assert info.status == ServerStatus.HEALTH_CHECK_FAILED
        
        # Recovery
        info.record_health_check(success=True)
        assert info.status == ServerStatus.RUNNING
    
    def test_process_excluded_from_serialization(self):
        """Test that process_handle field is excluded from serialization."""
        info = BaseServerInfo(
            name="test",
            pid=12345,
            status=ServerStatus.RUNNING,
            config_snapshot={},
            process_handle="mock_process"  # Should be excluded
        )
        
        # Serialize to dict
        data = info.model_dump()
        assert "process_handle" not in data
        assert "_process" not in data  # Alias should also be excluded
        assert "name" in data
        assert "pid" in data
    
    def test_server_status_enum(self):
        """Test ServerStatus enum values."""
        # All status values should be valid
        statuses = [
            ServerStatus.STARTING,
            ServerStatus.RUNNING,
            ServerStatus.STOPPING,
            ServerStatus.STOPPED,
            ServerStatus.ERROR,
            ServerStatus.HEALTH_CHECK_FAILED,
            ServerStatus.RESTARTING,
        ]
        
        for status in statuses:
            info = BaseServerInfo(
                name="test",
                pid=12345,
                status=status,
                config_snapshot={}
            )
            assert info.status == status
            assert isinstance(info.status.value, str)