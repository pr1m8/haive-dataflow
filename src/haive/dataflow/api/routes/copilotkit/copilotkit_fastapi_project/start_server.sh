#!/bin/bash
# Simple script to run the CopilotKit FastAPI server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"

echo "🚀 Starting CopilotKit FastAPI server..."
echo "📁 App directory: $APP_DIR"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Change to app directory and run the server
cd "$APP_DIR"
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "../logs/*" 