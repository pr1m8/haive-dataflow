# haive-dataflow/tests/platform/test_base_platform.py
"""
Test Base Platform Model and Inheritance Patterns

This test module validates the foundation platform model and the intelligent
inheritance patterns as specified in our architecture plan.

Test Categories:
1. BasePlatform model validation
2. Platform ID validation rules
3. Capability management
4. Inheritance pattern validation
5. Real-world usage scenarios
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from haive.dataflow.platform.models import BasePlatform, PlatformStatus


class TestBasePlatform:
    """Test base platform model and inheritance patterns."""

    def test_base_platform_validation(self):
        """Test base platform model validates correctly."""
        platform = BasePlatform(
            platform_id="test-platform",
            platform_name="Test Platform",
            description="A test platform"
        )
        assert platform.platform_id == "test-platform"
        assert platform.platform_name == "Test Platform"
        assert platform.description == "A test platform"
        assert platform.status == PlatformStatus.INITIALIZING
        assert platform.created_at <= datetime.utcnow()
        assert platform.version == "1.0.0"  # Default version
    
    def test_platform_id_validation_rules(self):
        """Test platform ID validation with various inputs."""
        # Valid cases - these should all work
        valid_ids = ["test-platform", "mcp_browser", "haive-dataflow-v2", "simple123", "a"]
        for platform_id in valid_ids:
            platform = BasePlatform(
                platform_id=platform_id,
                platform_name="Test",
                description="Test"
            )
            assert platform.platform_id == platform_id
        
        # Invalid cases - these should all raise ValidationError
        invalid_ids = ["Test Platform", "platform!", "123-ABC", "Platform With Spaces", ""]
        for platform_id in invalid_ids:
            with pytest.raises(ValidationError) as exc_info:
                BasePlatform(
                    platform_id=platform_id,
                    platform_name="Test",
                    description="Test"
                )
            assert "Platform ID must be lowercase" in str(exc_info.value)
    
    def test_version_validation(self):
        """Test semantic version validation."""
        # Valid versions
        valid_versions = ["1.0.0", "2.1.3", "10.20.30", "1.0.0-beta.1", "2.0.0+build.123"]
        for version in valid_versions:
            platform = BasePlatform(
                platform_id="test",
                platform_name="Test",
                description="Test",
                version=version
            )
            assert platform.version == version
        
        # Invalid versions
        invalid_versions = ["1.0", "v1.0.0", "1.0.0.0", "invalid"]
        for version in invalid_versions:
            with pytest.raises(ValidationError) as exc_info:
                BasePlatform(
                    platform_id="test",
                    platform_name="Test", 
                    description="Test",
                    version=version
                )
            assert "Version must follow semantic versioning" in str(exc_info.value)
    
    def test_capability_flags_default_behavior(self):
        """Test that capability flags have correct defaults."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test",
            description="Test"
        )
        
        # All capabilities should default to False
        assert platform.supports_discovery is False
        assert platform.supports_health_monitoring is False
        assert platform.supports_authentication is False
        assert platform.supports_caching is False
    
    def test_capability_flags_can_be_overridden(self):
        """Test that capability flags can be set to True."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test",
            description="Test",
            supports_discovery=True,
            supports_health_monitoring=True,
            supports_authentication=True,
            supports_caching=True
        )
        
        assert platform.supports_discovery is True
        assert platform.supports_health_monitoring is True
        assert platform.supports_authentication is True
        assert platform.supports_caching is True
    
    def test_status_management(self):
        """Test platform status management methods."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test",
            description="Test"
        )
        
        # Initial status
        assert platform.status == PlatformStatus.INITIALIZING
        
        # Update status with timestamp
        original_updated_at = platform.updated_at
        platform.update_status(PlatformStatus.ACTIVE, update_timestamp=True)
        
        assert platform.status == PlatformStatus.ACTIVE
        assert platform.updated_at > original_updated_at
        
        # Update status without timestamp
        current_timestamp = platform.updated_at
        platform.update_status(PlatformStatus.INACTIVE, update_timestamp=False)
        
        assert platform.status == PlatformStatus.INACTIVE
        assert platform.updated_at == current_timestamp  # Unchanged
    
    def test_metadata_management(self):
        """Test platform metadata management."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test", 
            description="Test"
        )
        
        # Initial metadata should be empty
        assert platform.metadata == {}
        
        # Add metadata
        platform.add_metadata("test_key", "test_value")
        assert platform.metadata["test_key"] == "test_value"
        assert platform.updated_at is not None
        
        # Add more metadata
        platform.add_metadata("numeric_key", 123)
        platform.add_metadata("dict_key", {"nested": "value"})
        
        assert platform.metadata["numeric_key"] == 123
        assert platform.metadata["dict_key"]["nested"] == "value"
        assert len(platform.metadata) == 3
    
    def test_capability_summary(self):
        """Test capability summary generation."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test",
            description="Test",
            supports_discovery=True,
            supports_health_monitoring=True,
            supports_authentication=False,
            supports_caching=False
        )
        
        summary = platform.get_capability_summary()
        expected = {
            "discovery": True,
            "health_monitoring": True,
            "authentication": False,
            "caching": False
        }
        
        assert summary == expected
    
    def test_pydantic_model_dump(self):
        """Test that platform can be serialized properly."""
        platform = BasePlatform(
            platform_id="test-platform",
            platform_name="Test Platform",
            description="A test platform for validation",
            supports_discovery=True,
            supports_health_monitoring=True
        )
        
        # Add some metadata
        platform.add_metadata("environment", "test")
        platform.add_metadata("feature_flags", {"new_ui": True})
        
        # Serialize to dict
        data = platform.model_dump()
        
        # Validate structure
        assert data["platform_id"] == "test-platform"
        assert data["platform_name"] == "Test Platform"
        assert data["supports_discovery"] is True
        assert data["supports_health_monitoring"] is True
        assert data["metadata"]["environment"] == "test"
        assert data["metadata"]["feature_flags"]["new_ui"] is True
        
        # Deserialize back
        restored = BasePlatform.model_validate(data)
        assert restored.platform_id == platform.platform_id
        assert restored.metadata == platform.metadata
    
    def test_model_config_validation(self):
        """Test that model configuration works as expected."""
        # Test str_strip_whitespace
        platform = BasePlatform(
            platform_id=" test-platform ",  # Whitespace should be stripped
            platform_name=" Test Platform ",
            description=" A test platform "
        )
        
        assert platform.platform_id == "test-platform"
        assert platform.platform_name == "Test Platform"
        assert platform.description == "A test platform"
        
        # Test extra="forbid" - should reject unknown fields
        with pytest.raises(ValidationError) as exc_info:
            BasePlatform(
                platform_id="test",
                platform_name="Test",
                description="Test",
                unknown_field="should_be_rejected"  # This should cause error
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestPlatformInheritance:
    """Test inheritance patterns and extensibility."""
    
    def test_inheritance_foundation(self):
        """Test that BasePlatform provides proper inheritance foundation."""
        platform = BasePlatform(
            platform_id="test",
            platform_name="Test",
            description="Test"
        )
        
        # Should be instance of BasePlatform
        assert isinstance(platform, BasePlatform)
        
        # Should have all required fields
        required_fields = [
            "platform_id", "platform_name", "description", "version",
            "supports_discovery", "supports_health_monitoring", 
            "supports_authentication", "supports_caching",
            "config", "metadata", "created_at", "status"
        ]
        
        for field in required_fields:
            assert hasattr(platform, field)
    
    def test_field_inheritance_behavior(self):
        """Test that fields can be properly inherited and overridden."""
        # Create a simple subclass to test inheritance
        class TestPlatform(BasePlatform):
            # Override some defaults
            supports_discovery: bool = True
            supports_health_monitoring: bool = True
            custom_field: str = "test_value"
        
        platform = TestPlatform(
            platform_id="test",
            platform_name="Test",
            description="Test"
        )
        
        # Inherited fields should work
        assert platform.platform_id == "test"
        assert platform.created_at <= datetime.utcnow()
        
        # Overridden defaults should work
        assert platform.supports_discovery is True
        assert platform.supports_health_monitoring is True
        
        # Custom fields should work
        assert platform.custom_field == "test_value"
    
    def test_method_inheritance(self):
        """Test that methods are properly inherited."""
        class TestPlatform(BasePlatform):
            custom_capability: bool = True
            
            def get_extended_summary(self):
                base_summary = self.get_capability_summary()
                base_summary["custom"] = self.custom_capability
                return base_summary
        
        platform = TestPlatform(
            platform_id="test",
            platform_name="Test",
            description="Test",
            supports_discovery=True
        )
        
        # Inherited methods should work
        platform.add_metadata("test", "value")
        assert platform.metadata["test"] == "value"
        
        # Extended methods should work
        summary = platform.get_extended_summary()
        assert summary["discovery"] is True  # From base method
        assert summary["custom"] is True     # From extended method


class TestRealWorldUsage:
    """Test real-world usage scenarios."""
    
    def test_platform_lifecycle(self):
        """Test complete platform lifecycle."""
        # Create platform
        platform = BasePlatform(
            platform_id="production-platform",
            platform_name="Production Platform",
            description="Production environment platform",
            supports_discovery=True,
            supports_health_monitoring=True,
            supports_authentication=True
        )
        
        # Initial state
        assert platform.status == PlatformStatus.INITIALIZING
        assert platform.updated_at is None
        
        # Initialize
        platform.update_status(PlatformStatus.STARTING)
        starting_time = platform.updated_at
        assert starting_time is not None
        
        # Add configuration
        platform.add_metadata("environment", "production")
        platform.add_metadata("region", "us-east-1") 
        platform.add_metadata("version", "2.1.0")
        
        # Go active
        platform.update_status(PlatformStatus.ACTIVE)
        active_time = platform.updated_at
        assert active_time > starting_time
        
        # Verify final state
        assert platform.status == PlatformStatus.ACTIVE
        assert len(platform.metadata) == 3
        assert platform.metadata["environment"] == "production"
        
        # Get comprehensive state
        summary = platform.get_capability_summary()
        assert summary["discovery"] is True
        assert summary["health_monitoring"] is True
        assert summary["authentication"] is True
    
    def test_configuration_validation_edge_cases(self):
        """Test edge cases in configuration validation."""
        # Minimum length platform_id (should work)
        platform = BasePlatform(
            platform_id="a",  # Single character
            platform_name="Single",
            description="Single character platform"
        )
        assert platform.platform_id == "a"
        
        # Long but valid platform_id
        long_id = "a" * 50  # 50 characters
        platform = BasePlatform(
            platform_id=long_id,
            platform_name="Long",
            description="Long platform ID"
        )
        assert platform.platform_id == long_id
        
        # Maximum valid version complexity
        platform = BasePlatform(
            platform_id="complex",
            platform_name="Complex",
            description="Complex version",
            version="12.34.56-beta.78+build.90.timestamp.123456789"
        )
        assert "12.34.56" in platform.version