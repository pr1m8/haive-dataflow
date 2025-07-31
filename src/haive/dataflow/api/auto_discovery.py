"""Auto-discovery and pattern-based API generation for Haive Dataflow.

Similar to agent capture system, this provides:
- Auto-discovery of API endpoints and WebSocket handlers
- Pattern-based route generation
- Unified interface creation
- Dynamic documentation generation
- Performance monitoring and analytics
"""

import ast
import inspect
import json
import logging
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class APIPattern:
    """Represents a discovered API pattern."""

    def __init__(
        self,
        name: str,
        pattern_type: str,
        handler: Callable,
        route: str | None = None,
        method: str = "GET",
        websocket: bool = False,
        **metadata,
    ):
        self.name = name
        self.pattern_type = pattern_type  # 'rest', 'websocket', 'stream', 'agent'
        self.handler = handler
        self.route = route or f"/{name.lower().replace('_', '-')}"
        self.method = method.upper()
        self.websocket = websocket
        self.metadata = metadata

        # Extract pattern info
        self._analyze_handler()

    def _analyze_handler(self):
        """Analyze the handler to extract patterns and requirements."""
        if not self.handler:
            return

        # Get signature
        try:
            sig = inspect.signature(self.handler)
            self.parameters = list(sig.parameters.keys())
            self.return_annotation = sig.return_annotation
        except BaseException:
            self.parameters = []
            self.return_annotation = None

        # Get docstring
        self.docstring = inspect.getdoc(self.handler) or ""

        # Determine if it's async
        self.is_async = inspect.iscoroutinefunction(self.handler)

        # Analyze input/output patterns
        self._analyze_io_patterns()

    def _analyze_io_patterns(self):
        """Analyze input/output patterns from the handler."""
        # Look for common patterns in parameter names
        param_patterns = {
            "agent": ["agent", "agent_id", "agent_name"],
            "game": ["game", "game_id", "game_type", "game_state"],
            "conversation": ["conversation", "conv_id", "chat_id", "message"],
            "llm": ["llm", "model", "prompt", "completion"],
            "auth": ["user", "user_id", "token", "auth"],
            "stream": ["stream", "websocket", "ws", "connection"],
        }

        self.detected_patterns = []
        for pattern, keywords in param_patterns.items():
            if any(
                keyword in param.lower()
                for param in self.parameters
                for keyword in keywords
            ):
                self.detected_patterns.append(pattern)

        # Analyze docstring for more patterns
        doc_lower = self.docstring.lower()
        for pattern in param_patterns:
            if pattern in doc_lower and pattern not in self.detected_patterns:
                self.detected_patterns.append(pattern)


class APIDiscovery:
    """Discovers API patterns across the Haive Dataflow ecosystem."""

    def __init__(self, api_dir: Path):
        self.api_dir = Path(api_dir)
        self.discovered_patterns: list[APIPattern] = []
        self.failed_imports: list[str] = []

    def discover_all_patterns(self) -> list[APIPattern]:
        """Discover all API patterns in the codebase."""
        logger.info("🔍 Starting API pattern discovery...")

        # Scan Python files for handlers
        python_files = list(self.api_dir.rglob("*.py"))

        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                self._analyze_file(py_file)
            except Exception as e:
                logger.debug(f"Failed to analyze {py_file}: {e}")
                self.failed_imports.append(str(py_file))

        logger.info(f"✅ Discovered {len(self.discovered_patterns)} API patterns")
        logger.info(f"⚠️ Failed to analyze {len(self.failed_imports)} files")

        return self.discovered_patterns

    def _should_skip_file(self, py_file: Path) -> bool:
        """Check if we should skip analyzing this file."""
        skip_patterns = [
            "__pycache__",
            ".pytest_cache",
            "test_",
            "_test.py",
            "__init__.py",
            ".venv",
            "node_modules",
        ]
        return any(pattern in str(py_file) for pattern in skip_patterns)

    def _analyze_file(self, py_file: Path):
        """Analyze a Python file for API patterns."""
        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find API handlers
            tree = ast.parse(content)

            # Look for FastAPI-style decorators and function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    pattern = self._analyze_function(node, py_file, content)
                    if pattern:
                        self.discovered_patterns.append(pattern)

        except Exception as e:
            logger.debug(f"Error analyzing {py_file}: {e}")

    def _analyze_function(
        self, node: ast.FunctionDef, py_file: Path, content: str
    ) -> APIPattern | None:
        """Analyze a function to see if it's an API handler."""
        # Look for API decorators
        api_decorators = self._find_api_decorators(node)
        if not api_decorators:
            # Check if function name suggests it's a handler
            if not self._is_likely_handler(node.name):
                return None

        # Extract metadata from decorators
        metadata = self._extract_decorator_metadata(api_decorators, content)

        # Determine pattern type
        pattern_type = self._determine_pattern_type(node, metadata, content)

        # Create mock handler for analysis (since we can't import everything)
        mock_handler = self._create_mock_handler(node)

        return APIPattern(
            name=node.name,
            pattern_type=pattern_type,
            handler=mock_handler,
            route=metadata.get("route"),
            method=metadata.get("method", "GET"),
            websocket=metadata.get("websocket", False),
            file_path=str(py_file),
            line_number=node.lineno,
            decorators=api_decorators,
            **metadata,
        )

    def _find_api_decorators(self, node: ast.FunctionDef) -> list[str]:
        """Find API-related decorators on a function."""
        api_decorator_patterns = [
            "app.",
            "router.",
            "@app.",
            "@router.",
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "websocket",
            "ws",
            "socket",
        ]

        decorators = []
        for decorator in node.decorator_list:
            decorator_str = (
                ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
            )
            if any(
                pattern in decorator_str.lower() for pattern in api_decorator_patterns
            ):
                decorators.append(decorator_str)

        return decorators

    def _is_likely_handler(self, func_name: str) -> bool:
        """Check if function name suggests it's an API handler."""
        handler_patterns = [
            "get_",
            "post_",
            "put_",
            "delete_",
            "patch_",
            "_handler",
            "_endpoint",
            "_api",
            "websocket_",
            "ws_",
            "socket_",
            "handle_",
            "process_",
            "serve_",
        ]

        name_lower = func_name.lower()
        return any(pattern in name_lower for pattern in handler_patterns)

    def _extract_decorator_metadata(
        self, decorators: list[str], content: str
    ) -> dict[str, Any]:
        """Extract metadata from decorators."""
        metadata = {}

        for decorator in decorators:
            # Extract HTTP method
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                if method.lower() in decorator.lower():
                    metadata["method"] = method
                    break

            # Extract route path

            route_match = re.search(r'["\']([/\w\-\{\}:]+)["\']', decorator)
            if route_match:
                metadata["route"] = route_match.group(1)

            # Check for WebSocket
            if any(ws in decorator.lower() for ws in ["websocket", "ws"]):
                metadata["websocket"] = True

        return metadata

    def _determine_pattern_type(
        self, node: ast.FunctionDef, metadata: dict, content: str
    ) -> str:
        """Determine the type of API pattern."""
        func_name = node.name.lower()
        doc = ast.get_docstring(node) or ""
        doc_lower = doc.lower()

        # Check for WebSocket
        if metadata.get("websocket") or "websocket" in func_name or "ws" in func_name:
            return "websocket"

        # Check for streaming
        if "stream" in func_name or "stream" in doc_lower:
            return "stream"

        # Check for agent-related
        if "agent" in func_name or "agent" in doc_lower:
            return "agent"

        # Check for game-related
        if "game" in func_name or "game" in doc_lower:
            return "game"

        # Check for LLM-related
        if any(
            term in func_name or term in doc_lower
            for term in ["llm", "model", "completion", "chat"]
        ):
            return "llm"

        # Default to REST
        return "rest"

    def _create_mock_handler(self, node: ast.FunctionDef) -> Callable:
        """Create a mock handler for analysis purposes."""

        def mock_handler(*args, **kwargs):
            return {"mock": True, "function": node.name}

        # Copy basic attributes
        mock_handler.__name__ = node.name
        mock_handler.__doc__ = ast.get_docstring(node)

        return mock_handler


class APIRouterGenerator:
    """Generates router configurations from discovered patterns."""

    def __init__(self, patterns: list[APIPattern]):
        self.patterns = patterns

    def generate_unified_router(self, output_file: Path | None = None) -> str:
        """Generate a unified router that includes all discovered patterns."""
        # Group patterns by type
        patterns_by_type = {}
        for pattern in self.patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            patterns_by_type[pattern_type].append(pattern)

        # Generate router code
        router_code = self._generate_router_code(patterns_by_type)

        if output_file:
            output_file.write_text(router_code)
            logger.info(f"Generated unified router: {output_file}")

        return router_code

    def _generate_router_code(
        self, patterns_by_type: dict[str, list[APIPattern]]
    ) -> str:
        """Generate the actual router code."""
        imports = [
            "from fastapi import APIRouter, WebSocket, Depends, HTTPException",
            "from typing import Any, Dict, List, Optional",
            "import logging",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "# Auto-generated unified router",
            f"# Generated at: {datetime.now().isoformat()}",
            f"# Patterns discovered: {sum(len(patterns) for patterns in patterns_by_type.values())}",
            "",
            "router = APIRouter()",
            "",
        ]

        # Generate route handlers for each pattern type
        handlers = []

        for pattern_type, patterns in patterns_by_type.items():
            handlers.append(f"# {pattern_type.upper()} Endpoints")
            handlers.append("")

            for pattern in patterns:
                handler_code = self._generate_handler_code(pattern)
                handlers.append(handler_code)
                handlers.append("")

        # Add pattern registry
        registry_code = self._generate_pattern_registry(patterns_by_type)

        return "\\n".join(imports + handlers + [registry_code])

    def _generate_handler_code(self, pattern: APIPattern) -> str:
        """Generate code for a specific handler pattern."""
        if pattern.websocket:
            return self._generate_websocket_handler(pattern)
        return self._generate_rest_handler(pattern)

    def _generate_rest_handler(self, pattern: APIPattern) -> str:
        """Generate REST endpoint handler."""
        method = pattern.method.lower()
        route = pattern.route or f"/{pattern.name.replace('_', '-')}"

        # Generate parameters based on detected patterns
        params = self._generate_parameters(pattern)

        return f'''@router.{method}("{route}")
async def {pattern.name}({params}):
    """
    {pattern.docstring or f"Auto-generated {pattern.pattern_type} endpoint"}

    Pattern Type: {pattern.pattern_type}
    Detected Patterns: {", ".join(pattern.detected_patterns)}
    """
    logger.info(f"Handling {pattern.pattern_type} request: {pattern.name}")

    try:
        # TODO: Implement actual logic for {pattern.name}
        # This is auto-generated - replace with real implementation

        result = {{
            "endpoint": "{pattern.name}",
            "pattern_type": "{pattern.pattern_type}",
            "method": "{pattern.method}",
            "detected_patterns": {pattern.detected_patterns},
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }}

        return result

    except Exception as e:
        logger.error(f"Error in {pattern.name}: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))'''

    def _generate_websocket_handler(self, pattern: APIPattern) -> str:
        """Generate WebSocket handler."""
        route = pattern.route or f"/ws/{pattern.name.replace('_', '-')}"

        return f'''@router.websocket("{route}")
async def {pattern.name}(websocket: WebSocket):
    """
    {pattern.docstring or f"Auto-generated {pattern.pattern_type} WebSocket handler"}

    Pattern Type: {pattern.pattern_type}
    Detected Patterns: {", ".join(pattern.detected_patterns)}
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established: {pattern.name}")

    try:
        while True:
            # TODO: Implement actual WebSocket logic for {pattern.name}
            # This is auto-generated - replace with real implementation

            data = await websocket.receive_json()

            response = {{
                "endpoint": "{pattern.name}",
                "pattern_type": "{pattern.pattern_type}",
                "detected_patterns": {pattern.detected_patterns},
                "received_data": data,
                "timestamp": datetime.now().isoformat(),
                "status": "processed"
            }}

            await websocket.send_json(response)

    except Exception as e:
        logger.error(f"WebSocket error in {pattern.name}: {{e}}")
        await websocket.close()'''

    def _generate_parameters(self, pattern: APIPattern) -> str:
        """Generate parameter list for a handler."""
        # Basic parameters based on detected patterns
        params = []

        if "agent" in pattern.detected_patterns:
            params.append("agent_id: Optional[str] = None")

        if "game" in pattern.detected_patterns:
            params.append("game_id: Optional[str] = None")
            params.append("game_state: Optional[Dict[str, Any]] = None")

        if "conversation" in pattern.detected_patterns:
            params.append("conversation_id: Optional[str] = None")
            params.append("message: Optional[str] = None")

        if "llm" in pattern.detected_patterns:
            params.append("model: Optional[str] = None")
            params.append("prompt: Optional[str] = None")

        # Always include request data
        if pattern.method in ["POST", "PUT", "PATCH"]:
            params.append("request_data: Optional[Dict[str, Any]] = None")

        return ", ".join(params) if params else ""

    def _generate_pattern_registry(
        self, patterns_by_type: dict[str, list[APIPattern]]
    ) -> str:
        """Generate a registry of all discovered patterns."""
        registry_data = {}

        for pattern_type, patterns in patterns_by_type.items():
            registry_data[pattern_type] = [
                {
                    "name": p.name,
                    "route": p.route,
                    "method": p.method,
                    "websocket": p.websocket,
                    "detected_patterns": p.detected_patterns,
                    "file_path": p.metadata.get("file_path", ""),
                    "line_number": p.metadata.get("line_number", 0),
                }
                for p in patterns
            ]

        return f'''
# Pattern Registry
DISCOVERED_PATTERNS = {json.dumps(registry_data, indent=2)}

@router.get("/api/patterns")
async def get_discovered_patterns():
    """Get all discovered API patterns."""
    return {{
        "total_patterns": {sum(len(patterns) for patterns in patterns_by_type.values())},
        "pattern_types": list(DISCOVERED_PATTERNS.keys()),
        "patterns": DISCOVERED_PATTERNS,
        "generated_at": "{datetime.now().isoformat()}"
    }}'''


class APIDocumentationGenerator:
    """Generates documentation for discovered API patterns."""

    def __init__(self, patterns: list[APIPattern]):
        self.patterns = patterns

    def generate_api_docs(self, output_dir: Path) -> list[Path]:
        """Generate comprehensive API documentation."""
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # Generate overview
        overview_file = output_dir / "api_overview.md"
        overview_content = self._generate_overview()
        overview_file.write_text(overview_content)
        generated_files.append(overview_file)

        # Generate pattern-specific docs
        patterns_by_type = {}
        for pattern in self.patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            patterns_by_type[pattern_type].append(pattern)

        for pattern_type, patterns in patterns_by_type.items():
            doc_file = output_dir / f"{pattern_type}_api.md"
            doc_content = self._generate_pattern_docs(pattern_type, patterns)
            doc_file.write_text(doc_content)
            generated_files.append(doc_file)

        # Generate OpenAPI spec
        openapi_file = output_dir / "openapi.json"
        openapi_spec = self._generate_openapi_spec()
        openapi_file.write_text(json.dumps(openapi_spec, indent=2))
        generated_files.append(openapi_file)

        logger.info(f"Generated {len(generated_files)} API documentation files")
        return generated_files

    def _generate_overview(self) -> str:
        """Generate API overview documentation."""
        patterns_by_type = {}
        for pattern in self.patterns:
            pattern_type = pattern.pattern_type
            patterns_by_type.setdefault(pattern_type, []).append(pattern)

        return f"""# Haive Dataflow API Documentation

Auto-generated API documentation based on discovered patterns.

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

The Haive Dataflow API provides {len(self.patterns)} endpoints across {len(patterns_by_type)} different pattern types:

{self._generate_pattern_summary_table(patterns_by_type)}

## Quick Start

```python
import requests

# Example REST API call
response = requests.get("http://localhost:8000/api/patterns")
print(response.json())

# Example WebSocket connection
import websockets
async with websockets.connect("ws://localhost:8000/ws/example") as websocket:
    await websocket.send(json.dumps({{"message": "Hello"}}))
    response = await websocket.recv()
```

## Pattern Types

{self._generate_pattern_descriptions()}

## Authentication

Most endpoints support optional authentication. Include your API key in headers:

```
Authorization: Bearer your-api-key-here
```

## Rate Limiting

API calls are rate limited to prevent abuse. Current limits:
- REST endpoints: 100 requests/minute
- WebSocket connections: 10 concurrent connections per IP

## Error Handling

All endpoints follow consistent error response format:

```json
{{
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2025-01-01T00:00:00Z",
  "endpoint": "/api/example"
}}
```
"""

    def _generate_pattern_summary_table(
        self, patterns_by_type: dict[str, list[APIPattern]]
    ) -> str:
        """Generate summary table of patterns."""
        table_rows = []

        for pattern_type, patterns in patterns_by_type.items():
            rest_count = sum(1 for p in patterns if not p.websocket)
            ws_count = sum(1 for p in patterns if p.websocket)

            table_rows.append(
                f"| {
                    pattern_type.title()} | {
                    len(patterns)} | {rest_count} | {ws_count} |"
            )

        table_header = """| Pattern Type | Total | REST | WebSocket |
|--------------|-------|------|-----------|"""

        return table_header + "\\n" + "\\n".join(table_rows)

    def _generate_pattern_descriptions(self) -> str:
        """Generate descriptions for each pattern type."""
        descriptions = {
            "rest": "Standard HTTP REST endpoints for CRUD operations",
            "websocket": "Real-time bidirectional communication endpoints",
            "stream": "Server-sent events and streaming data endpoints",
            "agent": "AI agent interaction and management endpoints",
            "game": "Game-related endpoints for multiplayer interactions",
            "llm": "Large Language Model integration endpoints",
        }

        pattern_types = {p.pattern_type for p in self.patterns}

        result = []
        for pattern_type in sorted(pattern_types):
            desc = descriptions.get(pattern_type, f"{pattern_type.title()} endpoints")
            result.append(f"- **{pattern_type.title()}**: {desc}")

        return "\\n".join(result)

    def _generate_pattern_docs(
        self, pattern_type: str, patterns: list[APIPattern]
    ) -> str:
        """Generate documentation for a specific pattern type."""
        return f"""# {pattern_type.title()} API Endpoints

{len(patterns)} endpoints discovered for {pattern_type} pattern.

## Endpoints

{self._generate_endpoint_docs(patterns)}

## Usage Examples

{self._generate_usage_examples(patterns)}
"""

    def _generate_endpoint_docs(self, patterns: list[APIPattern]) -> str:
        """Generate documentation for individual endpoints."""
        docs = []

        for pattern in patterns:
            method = pattern.method.upper() if not pattern.websocket else "WebSocket"
            route = pattern.route or f"/{pattern.name.replace('_', '-')}"

            doc = f"""### {pattern.name}

**{method}** `{route}`

{pattern.docstring or "No description available"}

**Detected Patterns:** {", ".join(pattern.detected_patterns) if pattern.detected_patterns else "None"}

**Parameters:**
{self._generate_parameter_docs(pattern)}

**Response:**
```json
{{
  "endpoint": "{pattern.name}",
  "pattern_type": "{pattern.pattern_type}",
  "status": "success",
  "timestamp": "2025-01-01T00:00:00Z"
}}
```
"""
            docs.append(doc)

        return "\\n\\n".join(docs)

    def _generate_parameter_docs(self, pattern: APIPattern) -> str:
        """Generate parameter documentation."""
        if not pattern.detected_patterns:
            return "No specific parameters detected."

        param_docs = []

        if "agent" in pattern.detected_patterns:
            param_docs.append("- `agent_id` (optional): Agent identifier")

        if "game" in pattern.detected_patterns:
            param_docs.append("- `game_id` (optional): Game session identifier")
            param_docs.append("- `game_state` (optional): Current game state")

        if "conversation" in pattern.detected_patterns:
            param_docs.append("- `conversation_id` (optional): Conversation identifier")
            param_docs.append("- `message` (optional): Message content")

        if "llm" in pattern.detected_patterns:
            param_docs.append("- `model` (optional): LLM model name")
            param_docs.append("- `prompt` (optional): Input prompt")

        return (
            "\\n".join(param_docs)
            if param_docs
            else "Parameters determined by detected patterns."
        )

    def _generate_usage_examples(self, patterns: list[APIPattern]) -> str:
        """Generate usage examples for patterns."""
        if not patterns:
            return "No examples available."

        # Take first pattern as example
        pattern = patterns[0]

        if pattern.websocket:
            return f"""```python
import asyncio
import websockets
import json

async def connect_to_{pattern.name}():
    uri = "ws://localhost:8000{pattern.route or "/ws/" + pattern.name.replace("_", "-")}"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({{"action": "example"}}))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(data)

# Run the example
asyncio.run(connect_to_{pattern.name}())
```"""

        return f"""```python
import requests

# {pattern.method} request example
url = "http://localhost:8000{pattern.route or "/" + pattern.name.replace("_", "-")}"

response = requests.{pattern.method.lower()}(url, json={{
    "example": "data"
}})

print(response.json())
```"""

    def _generate_openapi_spec(self) -> dict[str, Any]:
        """Generate OpenAPI specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Haive Dataflow API",
                "version": "1.0.0",
                "description": "Auto-generated API specification",
                "generated_at": datetime.now().isoformat(),
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
            },
        }

        # Add paths from patterns
        for pattern in self.patterns:
            if not pattern.websocket:  # OpenAPI doesn't support WebSocket directly
                route = pattern.route or f"/{pattern.name.replace('_', '-')}"
                method = pattern.method.lower()

                if route not in spec["paths"]:
                    spec["paths"][route] = {}

                spec["paths"][route][method] = {
                    "summary": pattern.name.replace("_", " ").title(),
                    "description": pattern.docstring
                    or f"Auto-generated {pattern.pattern_type} endpoint",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "endpoint": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                    "tags": [pattern.pattern_type],
                }

        return spec
