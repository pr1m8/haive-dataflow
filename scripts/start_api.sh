#!/bin/bash
# Start the Haive API server with proper environment loading

echo "=== Starting Haive API Server ==="

# Change to the haive root directory
cd /home/will/Projects/haive/backend/haive || exit

# Load environment variables from .env file
if [[ -f .env ]]; then
	echo "Loading environment variables from .env..."
	set -a
	source .env
	set +a
	echo "Loaded environment variables"
else
	echo "Warning: .env file not found!"
fi

# Verify critical environment variables
echo -e "\nChecking critical environment variables:"
if [[ -z "${SUPABASE_JWT_SECRET}" ]]; then
	echo "✗ SUPABASE_JWT_SECRET is not set!"
else
	echo "✓ SUPABASE_JWT_SECRET is set (${SUPABASE_JWT_SECRET:0:3}...${SUPABASE_JWT_SECRET: -3})"
fi

if [[ -z "${SUPABASE_URL}" ]]; then
	echo "✗ SUPABASE_URL is not set!"
else
	echo "✓ SUPABASE_URL${ $SUPABASE_U}RL"
fi

# Change to dataflow package
cd packages/haive-dataflow || exit

echo -e "\n=== Starting API Server ==="
echo "URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo -e "\nPress Ctrl+C to stop the server\n"

# Start the server with poetry - need to add src to Python path
export PYTHONPATH="${PYTHONPATH}:src"
poetry run uvicorn haive.dataflow.api.app:app --reload --host 0.0.0.0 --port 8000
