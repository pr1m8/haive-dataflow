# haive_dataflow/main.py
import logging
import os

import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configure rich logging
console = Console()
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(message)s",
    datefmt="[%X]",
)

logger = logging.getLogger("haive.dataflow")

# Import fastapi app
from haive.dataflow.api.app import app
from haive.dataflow.config.settings import get_settings

settings = get_settings()


def display_startup_info():
    """Display rich startup information."""
    env_table = Table(box=box.ROUNDED)
    env_table.add_column("Setting", style="cyan")
    env_table.add_column("Value", style="green")

    env_table.add_row("Environment", settings.environment)
    env_table.add_row("Debug Mode", str(settings.api.debug))
    env_table.add_row("Log Level", LOG_LEVEL)
    env_table.add_row("Host", os.getenv("HOST", "0.0.0.0"))
    env_table.add_row("Port", os.getenv("PORT", "8000"))

    console.print(
        Panel(
            env_table,
            title="[bold blue]Haive Dataflow API[/bold blue]",
            subtitle="[italic]Server Configuration[/italic]",
        )
    )


def main():
    """Run the application server."""
    display_startup_info()

    # Get log level
    log_level = "info" if not settings.api.debug else "debug"

    # Run with uvicorn directly - no auto-reload
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        workers=1,
        reload_dirs=["haive/dataflow"],
    )


if __name__ == "__main__":
    main()
