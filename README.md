# haive-dataflow

[![PyPI version](https://img.shields.io/pypi/v/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pr1m8/haive-dataflow/actions/workflows/ci.yml/badge.svg)](https://github.com/pr1m8/haive-dataflow/actions/workflows/ci.yml)
[![Docs](https://github.com/pr1m8/haive-dataflow/actions/workflows/docs.yml/badge.svg)](https://pr1m8.github.io/haive-dataflow/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/haive-dataflow.svg)](https://pypi.org/project/haive-dataflow/)

**Data processing pipelines and ETL workflows for Haive agents.**

A registry, discovery, and serialization system for managing components, persistence, and data flows in the Haive framework.

## Installation

```bash
pip install haive-dataflow
```

## Features

- **📦 Component Registry** — register and discover Haive components at runtime
- **🔄 Serialization** — robust serialization for agents, configs, and state
- **💾 Persistence** — Postgres + Supabase backends, async support
- **🔌 Streaming** — real-time data streaming for agent pipelines
- **🌐 API Integration** — FastAPI integration for serving dataflows

## Quick Start

```python
from haive.dataflow.registry import ComponentRegistry

registry = ComponentRegistry()
registry.register("my_agent", my_agent)
component = registry.get("my_agent")
```

## Documentation

📖 **Full documentation:** https://pr1m8.github.io/haive-dataflow/

## Related Packages

| Package | Description |
|---------|-------------|
| [haive-core](https://pypi.org/project/haive-core/) | Foundation: engines, graphs |
| [haive-agents](https://pypi.org/project/haive-agents/) | Production agents |
| [haive-mcp](https://pypi.org/project/haive-mcp/) | MCP integration |

## License

MIT © [pr1m8](https://github.com/pr1m8)
