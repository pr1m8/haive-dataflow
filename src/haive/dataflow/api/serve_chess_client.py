#!/usr/bin/env python3
"""
Simple HTTP server to serve the chess client HTML/JS interface.

This script starts a simple HTTP server to serve the chess client
interface that connects to the WebSocket API.

Usage:
    python serve_chess_client.py [--port PORT]

Note:
    This is for development/testing only and should not be used in production.
"""

import argparse
import http.server
import logging
import socketserver
import sys
import webbrowser
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("chess-client-server")


def get_static_dir():
    """Get the directory containing the static files."""
    # Fix imports for local development
    import sys

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    )

    # Try to find the static directory
    current_file = Path(__file__).resolve()
    static_dir = current_file.parent / "static"

    if not static_dir.exists():
        # Create the static directory if it doesn't exist
        static_dir.mkdir(exist_ok=True)
        logger.warning(f"Created static directory: {static_dir}")

    return static_dir


class ChessClientHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from the static directory."""

    def __init__(self, *args, **kwargs):
        # Set the directory to the static directory
        static_dir = get_static_dir()
        super().__init__(*args, directory=str(static_dir), **kwargs)

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(format % args)


def run_server(port=8080):
    """Run the HTTP server."""
    try:
        # Get the static directory
        static_dir = get_static_dir()

        # Check if the chess client HTML file exists
        client_file = static_dir / "chess_client.html"
        if not client_file.exists():
            logger.error(f"Chess client file not found: {client_file}")
            logger.error("Make sure to create the file first")
            sys.exit(1)

        # Create the server
        with socketserver.TCPServer(("", port), ChessClientHandler) as httpd:
            logger.info(
                f"Serving chess client at http://localhost:{port}/chess_client.html"
            )

            # Open the client in a web browser
            webbrowser.open(f"http://localhost:{port}/chess_client.html")

            # Serve until interrupted
            httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Parse arguments and run the server."""
    parser = argparse.ArgumentParser(description="Run chess client HTTP server")
    parser.add_argument(
        "--port", type=int, default=8080, help="Port to run the server on"
    )
    args = parser.parse_args()

    run_server(port=args.port)


if __name__ == "__main__":
    main()
