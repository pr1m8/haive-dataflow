# Haive Dataflow Platform Module

This module provides the foundational platform architecture for the Haive framework, implementing Pydantic-first design principles with intelligent inheritance patterns.

## Overview

The platform module serves as the base layer for all platform-based components in Haive, including:

- **BasePlatform** - Core platform functionality
- **PluginPlatform** - Plugin architecture foundation  
- **BaseServerInfo** - Server information modeling
- **Platform composition patterns** - Intelligent design through inheritance

## Architecture Philosophy

### Pydantic-First Design

Following our core principle: "we will use pydantic and we will not use inits":

```python
# ✅ CORRECT - Pure Pydantic approach
class MyPlatform(BasePlatform):
    custom_field: str = Field(...)
    
    # NO __init__ method - Pydantic handles everything
    # Validation through field_validator
    # Configuration through ConfigDict

# ❌ WRONG - Manual initialization
class BadPlatform(BasePlatform):
    def __init__(self, **kwargs):  # Breaks our design principles
        super().__init__(**kwargs)
```

### Intelligent Inheritance

Platforms emphasize intelligent design through inheritance:

```python
# Platform hierarchy
BasePlatform
    ↓ (adds plugin functionality)
PluginPlatform  
    ↓ (adds domain-specific features)
MCPPlatform (in haive-mcp)
    ↓ (adds implementation details)
MCPBrowserPlugin (in haive-mcp)
```

## Core Components

### BasePlatform

The foundation for all platform components:

```python
from haive.dataflow.platform.models import BasePlatform

class BasePlatform(BaseModel):
    """Core platform functionality"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    version: str = Field(default="1.0.0")
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### PluginPlatform

Extended platform for plugin implementations:

```python
from haive.dataflow.platform.models import PluginPlatform

class PluginPlatform(BasePlatform):
    """Plugin-specific platform extensions"""
    
    plugin_type: str = Field(..., description="Type of plugin")
    enabled: bool = Field(default=True)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    
    def get_router(self) -> APIRouter:
        """FastAPI router generation"""
        # Method-based functionality, not __init__
```

## Usage Patterns

### Creating Platform Instances

```python
from haive.dataflow.platform import BasePlatform, PluginPlatform

# Basic platform
platform = BasePlatform(
    name="data-processor",
    description="Process streaming data",
    version="1.2.0",
    metadata={"author": "haive-team"}
)

# Plugin platform
plugin = PluginPlatform(
    name="mcp-browser",
    description="Browse MCP servers", 
    plugin_type="browser",
    configuration={
        "cache_ttl": 3600,
        "max_servers": 100
    }
)
```

### Platform Inheritance

```python
from haive.dataflow.platform import PluginPlatform

class StreamingPlatform(PluginPlatform):
    """Streaming data platform"""
    
    # Additional fields with validation
    buffer_size: int = Field(default=1000, ge=100, le=10000)
    batch_timeout: float = Field(default=5.0, ge=0.1, le=60.0)
    
    @field_validator("buffer_size")
    @classmethod
    def validate_buffer_size(cls, v: int) -> int:
        if v % 100 != 0:
            raise ValueError("Buffer size must be multiple of 100")
        return v

# Usage with validation
streaming = StreamingPlatform(
    name="stream-processor",
    plugin_type="streaming",
    buffer_size=2000  # Validated automatically
)
```

### Server Information Modeling

```python
from haive.dataflow.platform.models import BaseServerInfo

# Create server information
server = BaseServerInfo(
    name="PostgreSQL Server",  # Auto-normalized to "postgresql-server"
    description="Database connection server",
    version="1.3.0",
    capabilities=["database", "sql", "transactions"]
)

# Extend for specific server types
class DatabaseServerInfo(BaseServerInfo):
    connection_url: str = Field(...)
    max_connections: int = Field(default=100)
    ssl_enabled: bool = Field(default=True)
    
    @field_validator("connection_url")
    @classmethod
    def validate_connection(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "mysql://", "sqlite://")):
            raise ValueError("Invalid database URL format")
        return v
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, APIRouter
from haive.dataflow.platform import PluginPlatform

class APIEnabledPlatform(PluginPlatform):
    """Platform with FastAPI capabilities"""
    
    def get_router(self) -> APIRouter:
        router = APIRouter()
        
        @router.get("/status")
        async def get_status():
            return {
                "name": self.name,
                "enabled": self.enabled,
                "version": self.version
            }
        
        @router.post("/configure")
        async def update_config(config: Dict[str, Any]):
            # Use Pydantic validation for updates
            updated = self.model_copy(update={"configuration": config})
            return updated.model_dump()
        
        return router

# Integration
app = FastAPI()
platform = APIEnabledPlatform(
    name="api-platform",
    plugin_type="api"
)
app.include_router(platform.get_router(), prefix="/platform")
```

### Dataflow Integration

```python
from haive.dataflow.platform import BasePlatform

class DataflowPlatform(BasePlatform):
    """Platform for data processing workflows"""
    
    input_schema: Dict[str, str] = Field(default_factory=dict)
    output_schema: Dict[str, str] = Field(default_factory=dict)
    processing_mode: str = Field(default="batch", pattern="^(batch|stream|realtime)$")
    
    def process_data(self, data: Any) -> Any:
        """Process data according to platform configuration"""
        # Implementation using self.configuration
        # No __init__ needed - all config in Pydantic fields
```

## Factory Patterns

### Configuration-Based Creation

```python
class PlatformFactory:
    """Factory for platform creation"""
    
    @classmethod
    def from_config(cls, config_path: Path) -> BasePlatform:
        """Create platform from configuration file"""
        with open(config_path) as f:
            config = json.load(f)
        return BasePlatform.model_validate(config)
    
    @classmethod
    def from_environment(cls, prefix: str = "PLATFORM_") -> BasePlatform:
        """Create platform from environment variables"""
        env_config = {
            key.lower().replace(prefix.lower(), ""): value
            for key, value in os.environ.items()
            if key.startswith(prefix)
        }
        return BasePlatform.model_validate(env_config)
```

### Plugin Discovery

```python
def discover_plugins(plugin_dir: Path) -> List[PluginPlatform]:
    """Discover and load plugins from directory"""
    plugins = []
    
    for plugin_file in plugin_dir.glob("*.json"):
        try:
            with open(plugin_file) as f:
                config = json.load(f)
            plugin = PluginPlatform.model_validate(config)
            plugins.append(plugin)
        except ValidationError as e:
            logger.warning(f"Invalid plugin config {plugin_file}: {e}")
    
    return plugins
```

## Testing Patterns

### Real Component Testing

Following our "no mocks" philosophy:

```python
import pytest
from pydantic import ValidationError

def test_platform_validation_real():
    """Test platform with real Pydantic validation"""
    # Valid creation
    platform = BasePlatform(
        name="test-platform",
        description="Test platform"
    )
    assert platform.name == "test-platform"
    assert platform.version == "1.0.0"  # Default value
    
    # Validation errors
    with pytest.raises(ValidationError) as exc_info:
        BasePlatform(name="")  # Empty name not allowed
    
    assert "name" in str(exc_info.value)

def test_plugin_inheritance_real():
    """Test plugin inheritance with real validation"""
    plugin = PluginPlatform(
        name="test-plugin",
        plugin_type="test",
        enabled=True
    )
    
    # Verify inheritance
    assert isinstance(plugin, BasePlatform)
    assert plugin.plugin_type == "test"
    assert plugin.enabled is True
```

### Integration Testing

```python
def test_fastapi_integration_real():
    """Test FastAPI integration with real router"""
    from fastapi.testclient import TestClient
    
    platform = APIEnabledPlatform(
        name="test-api",
        plugin_type="api"
    )
    
    app = FastAPI()
    app.include_router(platform.get_router(), prefix="/test")
    
    client = TestClient(app)
    response = client.get("/test/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-api"
    assert "enabled" in data
```

## Performance Considerations

### Efficient Operations

```python
# Use model_copy for updates (faster than recreation)
updated_platform = platform.model_copy(
    update={"version": "2.0.0", "metadata": {"updated": True}}
)

# Use model_dump for serialization with options
lightweight_data = platform.model_dump(
    exclude={"metadata"},
    by_alias=True
)

# Use model_construct for trusted data (skips validation)
fast_platform = BasePlatform.model_construct(
    name="trusted",
    version="1.0.0"
)
```

### Caching Strategies

```python
from functools import lru_cache

class CachedPlatform(BasePlatform):
    """Platform with caching capabilities"""
    
    @lru_cache(maxsize=128)
    def get_configuration_hash(self) -> str:
        """Cached configuration hash"""
        config_str = json.dumps(self.configuration, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
```

## Directory Structure

```
haive-dataflow/src/haive/dataflow/platform/
├── __init__.py           # Platform exports
├── models/               # Core platform models
│   ├── __init__.py      # Model exports
│   ├── base.py          # BasePlatform, BaseServerInfo
│   ├── plugin.py        # PluginPlatform
│   └── README.md        # Model documentation
├── factory/             # Platform creation patterns
├── utils/               # Platform utilities
└── README.md           # This file
```

## Related Documentation

- [MCP Platform](../../haive-mcp/src/haive/mcp/README.md) - MCP-specific platform implementation
- [MCPBrowserPlugin](../../haive-mcp/src/haive/mcp/plugins/README.md) - Real-world plugin example
- [Pydantic Patterns](../../../project_docs/active/standards/coding/PYDANTIC_PATTERNS.md) - Coding standards
- [Testing Philosophy](../../../project_docs/active/standards/testing/philosophy.md) - No-mocks approach

## Next Steps

1. **Extend Platform Types** - Add more specialized platform classes
2. **Plugin Registry** - Centralized plugin discovery and management
3. **Configuration Management** - Advanced configuration patterns
4. **Performance Optimization** - Caching and serialization improvements