#!/bin/bash
# Run the Haive API with uvicorn
# This script runs the main app.py file directly with uvicorn

# Get the directory where this script is located
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Set working directory to src
cd "${SCRIPT_DIR}/../../../" || exit

# Start uvicorn with the app
echo "Starting Haive API with game routes on http://localhost:8000"
uvicorn haive.dataflow.api.app:app --host 0.0.0.0 --port 8000 --reload
