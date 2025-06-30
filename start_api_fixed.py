#!/usr/bin/env python3
"""Start API server with fixed tools route."""

import os
import sys

# Add paths like the main app does
sys.path.insert(0, "src")

# Import the app
from haive.dataflow.api.app import app

if __name__ == "__main__":
    import uvicorn

    print("Starting API server with fixed tools discovery...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
