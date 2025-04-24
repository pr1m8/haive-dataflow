# haive_dataflow/main.py
import os
import logging
import uvicorn
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

from rich.logging import RichHandler
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # quiet down access logs
logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)   
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

# Import fastapi app
from haive.dataflow.api.app import app
from haive.dataflow.config.settings import get_settings

settings = get_settings()

def main():
    """Run the application server."""
    log_level = "info" if not settings.api.debug else "debug"
    
    # Log application startup
    logger = logging.getLogger("haive.dataflow")
    logger.info(f"Starting Haive Dataflow API in {settings.environment} environment")
    
    # Completely disable auto-reloading and run with a single worker
    uvicorn.run(
        app,  # Use the imported app directly
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=log_level,
        reload=False,  # Completely disable reload
        workers=1
    )

if __name__ == "__main__":
    main()