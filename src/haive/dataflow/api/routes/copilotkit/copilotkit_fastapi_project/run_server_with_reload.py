#!/usr/bin/env python3
"""
CopilotKit FastAPI Server Runner with Reload Support

This version uses the import string method to enable proper reload functionality.
"""

import os
import sys
from pathlib import Path

def main():
    # Get paths
    current_dir = Path(__file__).parent
    app_dir = current_dir / "app"
    logs_dir = current_dir / "logs"
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(exist_ok=True)
    
    # Add the app directory to Python path instead of changing directory
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    print("🚀 Starting CopilotKit FastAPI server with reload...")
    print(f"📁 App directory: {app_dir}")
    print(f"📝 Logs directory: {logs_dir}")
    print(f"🐍 Python path includes: {app_dir}")
    
    import uvicorn
    
    # Run with import string to enable reload
    uvicorn.run(
        "main:app",  # Import string instead of app instance
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(app_dir)],  # Watch the app directory
        reload_excludes=[str(logs_dir)],  # Exclude logs from triggering reload
        log_config=None,  # Use our custom logging setup
    )

if __name__ == "__main__":
    main() 