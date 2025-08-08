"""Debug Tools - Debug Tools module.

TODO: Add comprehensive description of debug tools functionality.

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
"""Debug tools discovery."""

import os
import sys

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
haive_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
sys.path.insert(0, "src")
sys.path.insert(0, haive_root)


try:
    from haive.dataflow.api.routes.tools_routes import discover_tools

    tools = discover_tools()
    for _tool in tools:
        pass
except Exception:
    import traceback

    traceback.print_exc()
