# Platform Models Module

This module contains the foundational Pydantic models for the Haive platform architecture, implementing pure Pydantic patterns with no `__init__` methods.

## Platform Hierarchy

The platform models follow a clear inheritance hierarchy:

```
BasePlatform (core platform functionality)
    ↓
PluginPlatform (plugin-specific extensions)
    ↓
MCPPlatform (MCP-specific platform) - in haive-mcp
```

## Core Models

### BasePlatform

The foundation for all platform components:

```python
from haive.dataflow.platform.models import BasePlatform
from pydantic import Field

class BasePlatform(BaseModel):
    """Pure Pydantic platform base - no __init__ methods"""
    
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
    """Platform extension for plugin functionality"""
    
    plugin_type: str = Field(..., description="Type of plugin")
    enabled: bool = Field(default=True)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    
    def get_router(self) -> APIRouter:
        """Get FastAPI router for this plugin"""
        # Implementation provided via methods, not __init__
```

### BaseServerInfo

Foundation for server information models:

```python
from haive.dataflow.platform.models import BaseServerInfo

class BaseServerInfo(BaseModel):
    """Base server information model"""
    
    name: str = Field(..., description="Server identifier")
    description: str = Field(default="", description="Server description")
    version: str = Field(default="1.0.0", description="Server version")
    capabilities: List[str] = Field(default_factory=list)
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize server names to lowercase-hyphen format"""
        return v.lower().replace(" ", "-").replace("_", "-")
```

## Design Principles

### 1. No `__init__` Methods

All models use pure Pydantic initialization:

```python
# ✅ CORRECT - Pure Pydantic
class MyPlatform(BasePlatform):
    custom_field: str = Field(...)
    
    # NO __init__ method defined
    # Pydantic handles all initialization

# ❌ WRONG - Manual __init__
class BadPlatform(BasePlatform):
    def __init__(self, **kwargs):  # Breaks Pydantic!
        super().__init__(**kwargs)
```

### 2. Field Validation

Comprehensive validation using Pydantic validators:

```python
class ValidatedPlatform(BasePlatform):
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Name must be alphanumeric with hyphens/underscores")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_configuration(self) -> "ValidatedPlatform":
        # Cross-field validation
        return self
```

### 3. ConfigDict Usage

All models include proper configuration:

```python
class ConfiguredPlatform(BasePlatform):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True  # When needed for complex types
    )
```

## Usage Examples

### Creating Platform Instances

```python
from haive.dataflow.platform.models import BasePlatform, PluginPlatform

# Basic platform
platform = BasePlatform(
    name="My Platform",
    description="Example platform",
    version="2.0.0"
)

# Plugin platform
plugin = PluginPlatform(
    name="MCP Browser",
    description="Browse MCP servers",
    plugin_type="browser",
    configuration={"cache_ttl": 3600}
)
```

### Inheritance Patterns

```python
from haive.dataflow.platform.models import PluginPlatform

class CustomPlugin(PluginPlatform):
    """Custom plugin with additional fields"""
    
    custom_setting: int = Field(default=100, ge=1, le=1000)
    advanced_config: Dict[str, str] = Field(default_factory=dict)
    
    @field_validator("custom_setting")
    @classmethod
    def validate_setting(cls, v: int) -> int:
        # Custom validation logic
        return v

# Usage
plugin = CustomPlugin(
    name="custom-plugin",
    plugin_type="advanced",
    custom_setting=500
)
```

### Serialization and Validation

```python
# Serialization
platform_dict = platform.model_dump()
platform_json = platform.model_dump_json()

# Validation from external data
try:
    platform = BasePlatform.model_validate(external_data)
except ValidationError as e:
    print(f"Validation errors: {e}")

# Partial updates
updated_platform = platform.model_copy(
    update={"version": "2.1.0"}
)
```

## Server Information Models

### BaseServerInfo Usage

```python
from haive.dataflow.platform.models import BaseServerInfo

# Create server info
server = BaseServerInfo(
    name="PostgreSQL Server",  # Auto-normalized to "postgresql-server"
    description="Database MCP server",
    version="1.2.0",
    capabilities=["database", "sql", "postgres"]
)

# Validation ensures consistency
print(server.name)  # "postgresql-server"
```

### Extending Server Models

```python
class DatabaseServerInfo(BaseServerInfo):
    """Extended server info for database servers"""
    
    connection_string: Optional[str] = Field(default=None)
    max_connections: int = Field(default=100, ge=1)
    supports_transactions: bool = Field(default=True)
    
    @field_validator("connection_string")
    @classmethod
    def validate_connection(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(("postgresql://", "mysql://", "sqlite://")):
            raise ValueError("Invalid connection string format")
        return v
```

## Integration with FastAPI

Platform models integrate seamlessly with FastAPI:

```python
from fastapi import FastAPI, APIRouter
from haive.dataflow.platform.models import PluginPlatform

class APIPlugin(PluginPlatform):
    """Plugin with FastAPI integration"""
    
    def get_router(self) -> APIRouter:
        """Generate FastAPI router for this plugin"""
        router = APIRouter()
        
        @router.get("/info")
        async def get_plugin_info():
            return self.model_dump()
        
        @router.post("/configure")
        async def configure_plugin(config: Dict[str, Any]):
            # Update configuration using Pydantic validation
            updated = self.model_copy(update={"configuration": config})
            return updated.model_dump()
        
        return router

# Usage
app = FastAPI()
plugin = APIPlugin(name="api-plugin", plugin_type="api")
app.include_router(plugin.get_router(), prefix="/plugin")
```

## Factory Methods

Platform models support factory methods for common creation patterns:

```python
class PlatformFactory:
    """Factory methods for platform creation"""
    
    @classmethod
    def from_config_file(cls, config_path: Path) -> BasePlatform:
        """Create platform from configuration file"""
        with open(config_path) as f:
            config = json.load(f)
        return cls.model_validate(config)
    
    @classmethod
    def from_environment(cls) -> BasePlatform:
        """Create platform from environment variables"""
        return cls(
            name=os.getenv("PLATFORM_NAME", "default"),
            version=os.getenv("PLATFORM_VERSION", "1.0.0")
        )
```

## Testing Patterns

Testing platform models with real validation:

```python
import pytest
from pydantic import ValidationError

def test_platform_validation():
    """Test platform validation with real Pydantic"""
    # Valid creation
    platform = BasePlatform(name="test", description="Test platform")
    assert platform.name == "test"
    
    # Invalid creation
    with pytest.raises(ValidationError):
        BasePlatform(name="")  # Empty name not allowed

def test_server_info_normalization():
    """Test server name normalization"""
    server = BaseServerInfo(name="My Server Name")
    assert server.name == "my-server-name"
```

## Performance Considerations

### Efficient Model Operations

```python
# Use model_copy for updates (faster than re-creation)
updated = platform.model_copy(update={"version": "2.0.0"})

# Use model_dump for serialization
data = platform.model_dump(exclude={"metadata"})

# Use model_construct for trusted data (skips validation)
fast_platform = BasePlatform.model_construct(
    name="trusted",
    version="1.0.0"
)
```

## Related Documentation

- [MCP Models](../../../haive-mcp/src/haive/mcp/models/README.md) - MCP-specific server models
- [MCPBrowserPlugin](../../../haive-mcp/src/haive/mcp/plugins/README.md) - Plugin using these models
- [Pydantic Patterns](../../../../project_docs/active/standards/coding/PYDANTIC_PATTERNS.md) - Coding standards