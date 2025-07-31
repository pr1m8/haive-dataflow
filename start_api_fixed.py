"""Start Api Fixed - Start Api Fixed module.

TODO: Add comprehensive description of start api fixed functionality.

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
"""Start API server with fixed tools route."""

import sys

# Add paths like the main app does
sys.path.insert(0, "src")

# Import the app
from .api.app import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
