#!/bin/bash
# Script to kill any processes running on port 8000

echo "🔍 Looking for processes on port 8000..."
PIDS=$(lsof -ti:8000)

if [ -z "$PIDS" ]; then
    echo "✅ No processes found on port 8000"
else
    echo "🎯 Found processes: $PIDS"
    echo "💀 Killing processes..."
    kill -9 $PIDS
    echo "✅ Processes killed"
fi 