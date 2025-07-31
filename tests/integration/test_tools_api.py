#!/usr/bin/env python3
"""Test tools API directly."""

import os
import sys

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "src")
sys.path.insert(0, os.path.join(current_dir, "..", "..", "..", ".."))


try:
    import asyncio

    from haive.dataflow.api.routes.tools_routes import list_tools

    async def test_tools():
        response = await list_tools()
        for _tool in response.tools:
            pass

    asyncio.run(test_tools())

except Exception:
    import traceback

    traceback.print_exc()
