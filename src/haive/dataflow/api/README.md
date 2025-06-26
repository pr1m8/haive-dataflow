# Haive API Module

RESTful and WebSocket API endpoints for the Haive framework, providing access to registry data, agent functionality, conversations, and LLM models.

## Overview

The API module provides HTTP and WebSocket endpoints for interacting with the Haive framework. It is built on FastAPI and includes:

- RESTful endpoints for registry data access
- WebSocket endpoints for real-time agent interactions
- Authentication and authorization
- Request logging and rate limiting
- Cross-Origin Resource Sharing (CORS) configuration

## Module Structure

```
api/
├── app.py                # Main FastAPI application definition
├── base.py               # Base classes and utilities
├── db.py                 # Database integration for API
├── middleware/           # API middleware components
│   ├── auth.py           # Authentication middleware
│   ├── logging.py        # Request logging middleware
│   └── rate_limit.py     # Rate limiting middleware
├── routes/               # API route definitions
│   ├── agent_routes.py   # Agent-related endpoints
│   ├── conversation_routes.py # Conversation endpoints
│   └── llm_routes.py     # LLM model endpoints
└── game_agent.py         # Game agent functionality
```

## Key Components

### FastAPI Application

The `app.py` module creates and configures the FastAPI application with:

- CORS middleware for cross-origin requests
- Authentication middleware for securing endpoints
- Request logging for debugging and analytics
- Rate limiting to prevent abuse
- Health check endpoint for monitoring

### API Routes

The API includes several route groups:

- **Agent Routes**: Endpoints for creating, querying, and interacting with agents
- **Conversation Routes**: Endpoints for managing and interacting with conversations
- **LLM Routes**: Endpoints for accessing and using LLM models

### WebSocket Support

WebSocket endpoints enable real-time interactions with:

- Interactive agent sessions
- Streaming LLM responses
- Game agent functionality

### Middleware

Custom middleware components include:

- **Authentication**: Validates user credentials and permissions
- **Logging**: Records API requests and responses
- **Rate Limiting**: Restricts request frequency by client

## Usage Examples

### Starting the API Server

```python
from haive.dataflow.api.app import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Accessing Agent Endpoints

```python
import requests

# Create a new agent
response = requests.post(
    "http://localhost:8000/api/agents",
    json={
        "name": "TextAnalyzer",
        "type": "analyzer",
        "config": {
            "llm": {
                "provider": "openai",
                "model": "gpt-4"
            }
        }
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

agent_id = response.json()["id"]

# Get agent details
agent = requests.get(
    f"http://localhost:8000/api/agents/{agent_id}",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
).json()
```

### WebSocket Agent Interaction

```javascript
// JavaScript example
const socket = new WebSocket(`ws://localhost:8000/api/agents/ws/${agentId}`);

socket.onopen = function (e) {
  console.log("WebSocket connection established");

  // Send a message to the agent
  socket.send(
    JSON.stringify({
      type: "message",
      content: "Analyze this text for sentiment: I love using this product!",
    }),
  );
};

socket.onmessage = function (event) {
  const response = JSON.parse(event.data);
  console.log("Received response:", response);
};
```

## API Documentation

When the API server is running, complete API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These interactive documentation pages show all available endpoints, request/response schemas, and allow testing the API directly.
