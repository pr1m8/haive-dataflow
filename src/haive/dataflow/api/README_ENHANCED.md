# Haive Dataflow API

This directory contains the comprehensive API implementation for Haive's data flow and discovery system, including RESTful endpoints, WebSocket support, and game interaction capabilities.

## Overview

The Haive Dataflow API provides a unified interface for discovering, managing, and interacting with various Haive components including agents, tools, games, and LLM providers. Built on FastAPI, it leverages the unified discovery system from haive-core to ensure consistency across all endpoints.

## Module Structure

```
api/
├── routes/                                # API route implementations
│   ├── agent_discovery_routes_enhanced.py # Enhanced agent discovery with v1/v2 support
│   ├── tools_routes_enhanced.py          # Tool discovery with schema extraction
│   ├── agent_routes.py                   # Legacy agent endpoints
│   ├── conversation_routes.py            # Conversation management
│   └── llm_routes.py                     # LLM provider configuration
├── game_router_enhanced.py               # Game discovery and WebSocket API
├── app.py                                # Main FastAPI application
├── base.py                               # Base classes and utilities
├── db.py                                 # Database integration
├── middleware/                           # API middleware components
│   ├── auth.py                          # Authentication middleware
│   ├── logging.py                       # Request logging
│   └── rate_limit.py                    # Rate limiting
└── static/                               # Static files for web clients
```

## Key Features

### 1. Unified Discovery System

All API components use the centralized discovery system from haive-core:

- **Consistent Behavior**: Same discovery logic across all endpoints
- **No Code Duplication**: Single implementation in haive-core
- **Automatic Updates**: Changes in discovery system reflect everywhere

### 2. Enhanced Route System

#### Agent Discovery Routes (`routes/agent_discovery_routes_enhanced.py`)

- Discovers both v1 (config-based) and v2 (class-based) agents
- Rich metadata extraction and categorization
- Performance caching with force refresh option
- Comprehensive search and filtering capabilities

#### Tool Discovery Routes (`routes/tools_routes_enhanced.py`)

- Automatic schema extraction from tool classes
- Category inference from module paths
- Support for both individual tools and toolkits
- Experimental tool invocation endpoints

### 3. Game Router System (`game_router_enhanced.py`)

A comprehensive game discovery and management system:

**Features:**

- Automatic discovery of game agents from haive-games package
- WebSocket-based real-time game state streaming
- HTML client generation for browser-based gameplay
- Support for multiple concurrent game sessions
- Flexible agent initialization patterns

**WebSocket Protocol:**

```json
// Client to Server
{"type": "get_state"}
{"type": "make_move", "move": {...}}
{"type": "ai_move"}

// Server to Client
{"type": "state_update", "state": {...}, "game_type": "chess", "game_id": "abc123"}
{"type": "error", "message": "Invalid move"}
```

### 4. Performance Optimizations

- **In-Memory Caching**: Discovery results cached to avoid repeated scans
- **Lazy Loading**: Components loaded only when needed
- **Connection Pooling**: Efficient WebSocket connection management
- **Async Operations**: Non-blocking I/O for better scalability

## Usage Examples

### Starting the Complete API Server

```python
from haive.dataflow.api.app import app
import uvicorn

# Configure all routes
from haive.dataflow.api.routes.agent_discovery_routes_enhanced import router as agent_router
from haive.dataflow.api.routes.tools_routes_enhanced import router as tool_router
from haive.dataflow.api.game_router_enhanced import get_router as get_game_router

# Add discovery routes
app.include_router(agent_router, prefix="/api/v1")
app.include_router(tool_router, prefix="/api/v1")

# Add game routes
games_router = get_game_router()
app.include_router(games_router, prefix="/games")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Running Standalone Game Server

```python
from haive.dataflow.api.game_router_enhanced import main

# Run standalone game server on port 8005
if __name__ == "__main__":
    main()
```

### API Client Examples

```python
import requests
import asyncio
import websockets
import json

# List all agents
response = requests.get("http://localhost:8000/api/v1/agents")
agents = response.json()["agents"]

# Search for chat agents
response = requests.get(
    "http://localhost:8000/api/v1/agents/search",
    params={"query": "chat", "agent_type": "v2"}
)

# Get tool schema
response = requests.get("http://localhost:8000/api/v1/tools/GoogleSearchTool/schema")
schema = response.json()

# WebSocket game interaction
async def play_game():
    uri = "ws://localhost:8000/ws/chess/game123"
    async with websockets.connect(uri) as websocket:
        # Get initial state
        await websocket.send(json.dumps({"type": "get_state"}))
        state = await websocket.recv()
        print(f"Game state: {state}")

        # Make a move
        await websocket.send(json.dumps({
            "type": "make_move",
            "move": {"from": "e2", "to": "e4"}
        }))
        response = await websocket.recv()
        print(f"Move response: {response}")
```

## Configuration

Environment variables for API configuration:

```bash
# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Game Server Configuration
GAME_SERVER_HOST=0.0.0.0
GAME_SERVER_PORT=8005

# Discovery Configuration
HAIVE_ROOT=/path/to/haive
DISCOVERY_CACHE_TTL=3600

# Security
API_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]

# Performance
MAX_CONNECTIONS=100
REQUEST_TIMEOUT=30
```

## API Documentation

Interactive API documentation is available when the server is running:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API explorer
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation UI
- **OpenAPI Schema**: `http://localhost:8000/openapi.json` - Raw API specification

## Testing

Comprehensive test suite available:

```bash
# Run all API tests
poetry run pytest packages/haive-dataflow/tests/api/ -v

# Test specific components
poetry run pytest packages/haive-dataflow/tests/api/routes/test_discovery_apis_fixed.py -v
poetry run pytest packages/haive-dataflow/tests/api/test_game_router.py -v

# Run with coverage
poetry run pytest packages/haive-dataflow/tests/api/ --cov=haive.dataflow.api --cov-report=html
```

## Error Handling

Consistent error handling across all endpoints:

- **HTTP Status Codes**: Proper status codes for all responses
- **Error Messages**: Clear, actionable error messages
- **Validation**: Pydantic models validate all inputs
- **Logging**: Comprehensive logging for debugging

Example error response:

```json
{
  "detail": "Agent 'NonExistentAgent' not found",
  "status_code": 404,
  "type": "not_found_error"
}
```

## Security Considerations

1. **Authentication**: JWT-based authentication for protected endpoints
2. **CORS**: Configurable CORS settings for browser security
3. **Rate Limiting**: Prevent API abuse with configurable limits
4. **Input Validation**: All inputs validated with Pydantic
5. **WebSocket Security**: Connection validation and cleanup

## Performance Considerations

1. **Caching Strategy**: LRU cache for discovery results
2. **Connection Management**: Proper WebSocket lifecycle handling
3. **Async Operations**: All I/O operations are async
4. **Resource Cleanup**: Automatic cleanup of abandoned connections

## Monitoring

Built-in monitoring capabilities:

- **Health Check**: `/health` endpoint for service monitoring
- **Metrics**: Prometheus-compatible metrics at `/metrics`
- **Logging**: Structured logging with contextual information
- **Tracing**: OpenTelemetry support for distributed tracing

## Future Enhancements

1. **GraphQL API**: Alternative query interface for complex data fetching
2. **gRPC Support**: High-performance binary protocol option
3. **API Versioning**: Proper version management with deprecation
4. **Batch Operations**: Bulk discovery and management endpoints
5. **Streaming Updates**: Server-sent events for real-time updates

## Related Documentation

- [Routes Documentation](./routes/README.md)
- [Discovery System Fixes](/project_docs/DISCOVERY_SYSTEM_FIXES.md)
- [Circular Import Analysis](/project_docs/CIRCULAR_IMPORT_ANALYSIS.md)
- [Game Router Documentation](./game_router_enhanced.py)
- [API Design Patterns](/docs/source/api/patterns.md)
