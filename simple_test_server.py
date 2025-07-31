"""Simple Test Server - Simple Test Server module.

TODO: Add comprehensive description of simple test server functionality.

This module provides core functionality for the Haive AI Agent Framework.

Key Components:
    - Core module components (see source code)

Example:
    Basic usage::

        from packages.haive-dataflow import None

        # Create instance
        instance = None(name='example')

        # Use the core functionality
        result = instance.None('input_data')

        print(f"Result: {result}")

Advanced Usage:
    TODO: Add advanced core functionality example

See Also:
    TODO: List related modules

Notes:
    TODO: Add implementation notes and caveats
"""

#!/usr/bin/env python3
"""Simple test server to check tools API."""

import sys

sys.path.insert(0, "src")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test/tools")
async def test_tools():
    try:
        from haive.dataflow.api.routes.tools_routes import simple_discover_tools

        tools = simple_discover_tools()
        return {
            "status": "success",
            "count": len(tools),
            "tools": [{"name": t.name, "description": t.description} for t in tools],
        }
    except Exception as e:
        import traceback

        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
