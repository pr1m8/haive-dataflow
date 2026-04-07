# haive-dataflow

[![PyPI version](https://img.shields.io/pypi/v/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pr1m8/haive-dataflow/actions/workflows/ci.yml/badge.svg)](https://github.com/pr1m8/haive-dataflow/actions/workflows/ci.yml)
[![Docs](https://github.com/pr1m8/haive-dataflow/actions/workflows/docs.yml/badge.svg)](https://pr1m8.github.io/haive-dataflow/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)

**Data processing pipelines and ETL workflows for Haive agents.**

A registry, discovery, and serialization system for managing components, persistence, and data flows in the Haive framework. Use it for component management, agent persistence, dataflow orchestration, and FastAPI integration.

---

## Why haive-dataflow?

Production agent systems need more than just agents — they need:

- **Component registry** — track which agents, tools, and configs are available
- **Serialization** — save and load complex agent configs across processes
- **Persistence** — store agent state, conversation history, results
- **Streaming** — real-time data flows for production pipelines
- **API integration** — serve agents as HTTP endpoints

`haive-dataflow` provides all of this. It's the production infrastructure layer.

---

## Features

### 📦 Component Registry

Register and discover Haive components at runtime:

```python
from haive.dataflow.registry import ComponentRegistry

registry = ComponentRegistry()

# Register agents
registry.register("research_agent", researcher)
registry.register("writer_agent", writer)

# Discover by type
all_agents = registry.list_components(component_type="agent")

# Retrieve
agent = registry.get("research_agent")
```

### 🔄 Serialization

Save and restore agent configs:

```python
from haive.dataflow.serialization import serialize_agent, deserialize_agent

# Save to JSON
config_json = serialize_agent(my_agent)
with open("agent.json", "w") as f:
    f.write(config_json)

# Restore
with open("agent.json") as f:
    restored = deserialize_agent(f.read())
```

### 💾 Persistence

Multiple backends with sync and async support:

```python
from haive.dataflow.persistence import PostgresBackend, SupabaseBackend

# PostgreSQL
backend = PostgresBackend(
    connection_string="postgresql://haive:haive@localhost/haive",
    pool_size=10,
)

# Supabase
backend = SupabaseBackend(
    url="https://your-project.supabase.co",
    key="your-anon-key",
)

# Save state
await backend.save_state("session_123", agent_state)

# Restore
state = await backend.load_state("session_123")
```

### 🌐 FastAPI Integration

Serve agents as HTTP endpoints:

```python
from fastapi import FastAPI
from haive.dataflow.api import create_agent_router

app = FastAPI()
app.include_router(create_agent_router(my_agent), prefix="/agents/researcher")

# Now POST to /agents/researcher/run with JSON body
```

---

## Installation

```bash
pip install haive-dataflow

# With FastAPI integration
pip install haive-dataflow[api]

# With Supabase backend
pip install haive-dataflow[supabase]
```

---

## Quick Start

```python
from haive.dataflow.registry import ComponentRegistry
from haive.agents.simple.agent import SimpleAgent
from haive.core.engine.aug_llm import AugLLMConfig

# Create and register
registry = ComponentRegistry()
agent = SimpleAgent(name="hello", engine=AugLLMConfig())
registry.register("hello", agent)

# Use
component = registry.get("hello")
result = component.run("Hello world")
```

---

## Documentation

📖 **Full documentation:** https://pr1m8.github.io/haive-dataflow/

---

## Related Packages

| Package | Description |
|---------|-------------|
| [haive-core](https://pypi.org/project/haive-core/) | Foundation: engines, graphs, persistence |
| [haive-agents](https://pypi.org/project/haive-agents/) | Production agents (registered in dataflow) |
| [haive-mcp](https://pypi.org/project/haive-mcp/) | MCP integration |

---

## License

MIT © [pr1m8](https://github.com/pr1m8)
