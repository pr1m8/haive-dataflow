# Haive API Routes

This directory contains the FastAPI route implementations for the Haive discovery system.

## Overview

The routes in this directory provide RESTful APIs for discovering and managing Haive components including agents, tools, and games. All routes use the unified discovery system from haive-core to ensure consistency and prevent code duplication.

## Key Components

### Agent Discovery Routes (`agent_discovery_routes_enhanced.py`)

Provides endpoints for discovering and managing agents.

**Key Features:**

- Discovers both v1 (config-based) and v2 (class-based) agents
- Rich metadata extraction and categorization
- Caching for improved performance
- Comprehensive search and filtering

**Endpoints:**

- `GET /agents` - List all agents with optional filtering
- `GET /agents/search` - Search agents by query
- `GET /agents/{agent_name}` - Get detailed agent information
- `GET /agents/stats` - Get agent discovery statistics

### Tool Discovery Routes (`tools_routes_enhanced.py`)

Provides endpoints for discovering and managing tools and toolkits.

**Key Features:**

- Automatic schema extraction from tools
- Category inference from module paths
- Support for both individual tools and toolkits
- Tool invocation capabilities (experimental)

**Endpoints:**

- `GET /tools` - List all tools with filtering
- `GET /tools/search` - Search tools by query
- `GET /tools/{tool_name}/schema` - Get tool input/output schema
- `GET /tools/categories` - Get all tool categories
- `GET /tools/stats` - Get tool statistics

### Conversation Routes (`conversation_routes.py`)

Manages conversation sessions and state.

### LLM Routes (`llm_routes.py`)

Provides endpoints for LLM provider management and configuration.

## Installation

This module is part of the `haive-dataflow` package. Install it using:

```bash
pip install haive-dataflow
```

## Usage Examples

### Basic Usage

```python
from fastapi import FastAPI
from haive.dataflow.api.routes.agent_discovery_routes_enhanced import router as agent_router
from haive.dataflow.api.routes.tools_routes_enhanced import router as tool_router

app = FastAPI()
app.include_router(agent_router, prefix="/api/v1")
app.include_router(tool_router, prefix="/api/v1")

# Run with: uvicorn app:app --reload
```

### Discovery System Integration

All routes use the `HaiveComponentDiscovery` class from haive-core:

```python
from haive.core.utils.haive_discovery import HaiveComponentDiscovery

discovery = HaiveComponentDiscovery(haive_root)
components = discovery.discover_from_directory(path, module_base, create_tools=False)
```

### Example API Calls

```bash
# List all agents
curl http://localhost:8000/api/v1/agents

# Search for chat agents
curl http://localhost:8000/api/v1/agents/search?query=chat

# Get tool schema
curl http://localhost:8000/api/v1/tools/GoogleSearchTool/schema
```

## API Reference

For detailed API documentation, see the [API Reference](../../../docs/source/api/routes/index.rst).

## Testing

Unit tests are available in `/packages/haive-dataflow/tests/api/routes/`:

```bash
poetry run pytest packages/haive-dataflow/tests/api/routes/ -v
```

## See Also

- [Discovery System Documentation](/project_docs/DISCOVERY_SYSTEM_FIXES.md)
- [Circular Import Analysis](/project_docs/CIRCULAR_IMPORT_ANALYSIS.md)
- [Game Router Documentation](../game_router_enhanced.py)
