#!/usr/bin/env python3
"""Debug tools discovery."""

import os
import sys

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
haive_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
sys.path.insert(0, "src")
sys.path.insert(0, haive_root)

print("Testing tools discovery...")

try:
    from haive.dataflow.api.routes.tools_routes import discover_tools

    tools = discover_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name} ({tool.type}) from {tool.module}")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
