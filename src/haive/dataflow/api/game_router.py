"""Game_Router core module.

This module provides game router functionality for the Haive framework.

Classes:
    agent_module_name: agent_module_name implementation.
    in: in implementation.
    agent: agent implementation.

Functions:
    discover_game_agents: Discover Game Agents functionality.
    create_game_instance: Create Game Instance functionality.
    get_game_instance: Get Game Instance functionality.
"""

#!/usr/bin/env python
"""Game API router for Haive games.

This module discovers and loads game agents from haive-games package,
creating routes for each available game. It provides WebSocket endpoints
for streaming game state and interacting with game agents.
"""

import asyncio
import importlib
import inspect
import logging
import os
import pkgutil
import sys
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Add package paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
haive_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
packages_dir = os.path.join(haive_root, "packages")
haive_games_path = os.path.join(packages_dir, "haive-games/src")

# Add paths to sys.path for imports to work
for path in [haive_root, packages_dir, haive_games_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("game-routef")

# Active connections and games
active_connections: dict[str, set[WebSocket]] = {}  # game_type -> {websockets}
active_games: dict[str, dict[str, Any]] = {}  # game_id -> game_state

# Game agent registry
game_agents = {}


def discover_game_agents():
    """Discover game agents from haive-games package."""
    try:
        # Log current sys.path for debugging
        logger.info(f"sys.path: {sys.path}")

        # Try different import strategies to find haive.games
        import_paths = [
            ("haive.games", "direct import"),
            ("packages.haive_games.src.haive.games", "package path import"),
            ("haive_games.src.haive.games", "modified package path"),
        ]

        base_module = None
        for import_path, strategy in import_paths:
            try:
                logger.info(f"Trying {strategy}: {import_path}")
                base_module = importlib.import_module(import_path)
                logger.info(f"Successfully imported {import_path}")
                games_pkg = import_path
                break
            except ImportError as e:
                logger.warning(f"Failed to import {import_path}: {e}")
            except SyntaxError as e:
                logger.error(f"Syntax error in {import_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error importing {import_path}: {e}")
                continue

        if not base_module:
            # Try direct file path approach
            logger.info("Trying direct file path approach")
            if os.path.exists(haive_games_path):
                # Add specific directory to path
                games_dir = os.path.join(haive_games_path, "haive", "games")
                if games_dir not in sys.path:
                    sys.path.insert(0, games_dir)

                try:
                    # Try with direct path
                    base_module = importlib.import_module("base")
                    games_pkg = (
                        ""  # Empty prefix since we're already in the games directory
                    )
                    logger.info("Successfully imported using direct path")
                except Exception as e:
                    logger.error(f"Failed to import using direct path: {e}")
                    raise ImportError(
                        f"Could not import haive-games even with direct path: {e}"
                    )
            else:
                raise ImportError(
                    f"Could not find haive-games path: {haive_games_path}"
                )

        # Get the package directory
        games_dir = os.path.dirname(base_module.__file__)
        logger.info(f"Games directory: {games_dir}")

        # Find game modules (directories with __init__.py)
        game_modules = []
        for _, name, is_pkg in pkgutil.iter_modules([games_dir]):
            if is_pkg and name not in ["base", "framework", "core", "__pycache__"]:
                game_modules.append(name)

        logger.info(f"Discovered game modules: {game_modules}")

        # Import each game module and find agents
        for game_name in game_modules:
            try:
                # Import the game module
                game_module_name = (
                    f"{games_pkg}.{game_name}" if games_pkg else game_name
                )
                importlib.import_module(game_module_name)
                logger.info(f"Successfully imported {game_module_name}")

                # Try to find the agent class
                agent_module_name = (
                    f"{game_module_name}.agent" if games_pkg else f"{game_name}.agent"
                )
                try:
                    agent_module = importlib.import_module(agent_module_name)

                    # Find agent class in the module
                    for name, obj in inspect.getmembers(agent_module):
                        if (
                            inspect.isclass(obj)
                            and name.endswith("Agent")
                            and hasattr(obj, "run")
                        ):

                            # Add to registry
                            game_agents[game_name] = {
                                "name": game_name,
                                "agent_class": obj,
                                "module": agent_module_name,
                            }

                            # Try to get state schema
                            try:
                                state_module_name = (
                                    f"{game_module_name}.state"
                                    if games_pkg
                                    else f"{game_name}.state"
                                )
                                state_module = importlib.import_module(
                                    state_module_name
                                )
                                for state_name, state_obj in inspect.getmembers(
                                    state_module
                                ):
                                    if inspect.isclass(
                                        state_obj
                                    ) and state_name.endswith("State"):
                                        game_agents[game_name][
                                            "state_class"
                                        ] = state_obj
                                        break
                            except (ImportError, AttributeError) as e:
                                logger.warning(
                                    f"Could not import state schema for {game_name}: {e}"
                                )

                            logger.info(f"Found agent {name} in {agent_module_name}")
                            break

                except (ImportError, AttributeError) as e:
                    logger.warning(f"Could not import agent for {game_name}: {e}")

            except Exception as e:
                logger.error(
                    f"Error processing game module {game_name}: {e}", exc_info=True
                )

        logger.info(f"Registered game agents: {list(game_agents.keys())}")

    except Exception as e:
        logger.error(f"Error discovering game agents: {e}", exc_info=True)


def create_game_instance(game_type, game_id):
    """Create or get a game instance."""
    if game_type not in game_agents:
        raise ValueError(f"Unknown game type: {game_type}")

    # Create unique key for this game
    game_key = f"{game_type}:{game_id}"

    if game_key not in active_games:
        try:
            # Create new game instance
            agent_class = game_agents[game_type]["agent_class"]

            # Get config class - handle different agent implementations
            if hasattr(agent_class, "get_config_class"):
                config_class = agent_class.get_config_class()

                # Create config
                config = config_class(
                    name=f"{game_type}_{game_id}",
                    runnable_config={"configurable": {"thread_id": game_id}},
                )

                # Create agent
                agent = agent_class(config=config)
            else:
                # Simpler agent initialization for agents without config class
                agent = agent_class(name=f"{game_type}_{game_id}")

            # Store in active games
            active_games[game_key] = {
                "agent": agent,
                "game_id": game_id,
                "game_type": game_type,
                "created_at": asyncio.get_event_loop().time(),
            }

            logger.info(f"Created new game instance: {game_type}:{game_id}")
        except Exception as e:
            logger.error(
                f"Error creating game instance {game_type}:{game_id}: {e}",
                exc_info=True,
            )
            raise

    return active_games[game_key]


def get_game_instance(game_type, game_id):
    """Get an existing game instance."""
    game_key = f"{game_type}:{game_id}"
    return active_games.get(game_key)


def create_game_router(game_type):
    """Create a router for a specific game type."""
    if game_type not in game_agents:
        raise ValueError(f"Unknown game type: {game_type}")

    router = APIRouter(tags=[f"{game_type} Game"])

    # Register WebSocket endpoint
    @router.websocket(f"/ws/{game_type}/{{game_id}}")
    async def game_websocket(websocket: WebSocket, game_id: str):
        """WebSocket endpoint for game state streaming."""
        try:
            await websocket.accept()
            logger.info(
                f"WebSocket connection accepted for {game_type} game: {game_id}"
            )
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}")
            return

        # Register connection
        if game_type not in active_connections:
            active_connections[game_type] = set()
        active_connections[game_type].add(websocket)

        try:
            # Get or create game instance
            try:
                game = create_game_instance(game_type, game_id)
                agent = game["agent"]
            except Exception as e:
                logger.error(f"Failed to create game instance: {e}")
                await websocket.send_json(
                    {"type": "error", "message": f"Failed to create game: {e}"}
                )
                return

            # Send initial state
            try:
                initial_state = {}
                state = agent.run(initial_state, thread_id=game_id)

                await websocket.send_json(
                    {
                        "type": "state_update",
                        "game_type": game_type,
                        "game_id": game_id,
                        "state": state,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to get initial state: {e}")
                await websocket.send_json(
                    {"type": "error", "message": f"Failed to get initial state: {e}"}
                )

            # Main WebSocket loop
            while True:
                try:
                    # Receive message
                    data = await websocket.receive_json()
                    message_type = data.get("type", "")
                    logger.info(
                        f"Received message for {game_type}:{game_id}: {message_type}"
                    )

                    # Handle message
                    if message_type == "get_state":
                        # Get current state
                        try:
                            state = agent.run({}, thread_id=game_id)
                            await websocket.send_json(
                                {
                                    "type": "state_update",
                                    "game_type": game_type,
                                    "game_id": game_id,
                                    "state": state,
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error getting state: {e}")
                            await websocket.send_json(
                                {
                                    "type": "error",
                                    "message": f"Failed to get state: {e}",
                                }
                            )

                    elif message_type == "make_move":
                        # Make a move
                        try:
                            move_data = data.get("move", {})
                            input_data = {"move": move_data}

                            state = agent.run(input_data, thread_id=game_id)
                            await websocket.send_json(
                                {
                                    "type": "state_update",
                                    "game_type": game_type,
                                    "game_id": game_id,
                                    "state": state,
                                    "last_action": "player_move",
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error making move: {e}")
                            await websocket.send_json(
                                {
                                    "type": "error",
                                    "message": f"Failed to make move: {e}",
                                }
                            )

                    elif message_type == "ai_move":
                        # Request AI move
                        try:
                            state = agent.run({}, thread_id=game_id)
                            await websocket.send_json(
                                {
                                    "type": "state_update",
                                    "game_type": game_type,
                                    "game_id": game_id,
                                    "state": state,
                                    "last_action": "ai_move",
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error making AI move: {e}")
                            await websocket.send_json(
                                {
                                    "type": "error",
                                    "message": f"Failed to make AI move: {e}",
                                }
                            )

                    else:
                        # Unknown message type
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": f"Unknown message type: {message_type}",
                            }
                        )
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    try:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": f"Error processing message: {e}",
                            }
                        )
                    except:
                        # Connection might be closed
                        break

        except WebSocketDisconnect:
            # Handle disconnection
            logger.info(f"WebSocket disconnected for {game_type} game: {game_id}")
        except Exception as e:
            # Handle other errors
            logger.error(
                f"WebSocket error for {game_type}:{game_id}: {e}", exc_info=True
            )
            try:
                await websocket.send_json(
                    {"type": "error", "message": f"Server error: {e!s}"}
                )
            except:
                # Connection might be closed, ignore send error
                pass
        finally:
            # Always clean up connection
            if game_type in active_connections:
                active_connections[game_type].discard(websocket)
            logger.info(f"Cleaned up WebSocket connection for {game_type}:{game_id}")

    # Register REST endpoint to create a new game
    @router.post(f"/{game_type}/games", tags=[f"{game_type}"])
    async def create_game():
        """Create a new game."""
        game_id = f"{game_type}_{id(asyncio.get_event_loop().time())}"
        create_game_instance(game_type, game_id)

        return {
            "game_type": game_type,
            "game_id": game_id,
            "ws_url": f"/ws/{game_type}/{game_id}",
        }

    return router


# HTML for the main index page
def get_index_html():
    """Generate HTML for the index page with links to all games."""
    game_links = []
    for game_type in sorted(game_agents.keys()):
        game_links.append(f'<li><a href="/games/{game_type}">{game_type}</a></li>')

    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Haive Games</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 4px; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Haive Games</h1>
            <p>Select a game to play:</p>
            <ul>
                {"".join(game_links)}
            </ul>
        </body>
    </html>
    """


# HTML template for game client pages
def get_game_client_html(game_type):
    """Generate HTML for a specific game client."""
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{game_type.title()} Game</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .container {{ display: flex; }}
                .game-area {{ flex: 2; }}
                .controls {{ flex: 1; padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-left: 20px; }}
                .log {{ height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 10px; }}
                .game-info {{ margin-top: 10px; }}
                button {{ padding: 8px 12px; margin: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>{game_type.title()} Game</h1>
            
            <div class="container">
                <div class="game-area">
                    <div id="gameBoard" style="min-height: 400px; border: 1px solid #ccc; padding: 10px;">
                        <p>Game board will appear here after connection.</p>
                    </div>
                </div>
                
                <div class="controls">
                    <h3>Game Controls</h3>
                    <div>
                        <label for="gameId">Game ID:</label>
                        <input type="text" id="gameId" value="{game_type}_test123">
                        <button onclick="connect()">Connect</button>
                        <button onclick="disconnect()">Disconnect</button>
                    </div>
                    
                    <div class="game-info">
                        <p>Status: <span id="status">Disconnected</span></p>
                        <p>Turn: <span id="turn">-</span></p>
                        <p>Game Status: <span id="gameStatus">-</span></p>
                    </div>
                    
                    <div>
                        <button onclick="getState()">Get State</button>
                        <button onclick="aiMove()">AI Move</button>
                    </div>
                    
                    <h3>Log</h3>
                    <div class="log" id="log"></div>
                </div>
            </div>
            
            <script>
                // Game variables
                let ws = null;
                let gameState = null;
                
                // DOM elements
                const boardElement = document.getElementById('gameBoard');
                const statusElement = document.getElementById('status');
                const turnElement = document.getElementById('turn');
                const gameStatusElement = document.getElementById('gameStatus');
                const logElement = document.getElementById('log');
                
                // Log messages
                function log(message) {{
                    const entry = document.createElement('div');
                    entry.textContent = message;
                    logElement.appendChild(entry);
                    logElement.scrollTop = logElement.scrollHeight;
                }}
                
                // Connect to WebSocket
                function connect() {{
                    const gameId = document.getElementById('gameId').value;
                    
                    if (!gameId) {{
                        log('Please enter a game ID');
                        return;
                    }}
                    
                    const wsUrl = `ws://${{window.location.host}}/ws/{game_type}/${{gameId}}`;
                    
                    if (ws) {{
                        ws.close();
                    }}
                    
                    log(`Connecting to ${{wsUrl}}...`);
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function(event) {{
                        statusElement.textContent = 'Connected';
                        log('Connection established');
                    }};
                    
                    ws.onmessage = function(event) {{
                        try {{
                            const data = JSON.parse(event.data);
                            log(`Received: ${{JSON.stringify(data).substring(0, 100)}}...`);
                            
                            if (data.type === 'state_update') {{
                                gameState = data.state;
                                
                                // Update UI
                                updateBoardDisplay(gameState);
                                turnElement.textContent = gameState.current_player || gameState.turn || '-';
                                gameStatusElement.textContent = gameState.game_status || '-';
                            }} else if (data.type === 'error') {{
                                log(`Error: ${{data.message}}`);
                            }}
                        }} catch (e) {{
                            log(`Error parsing message: ${{e.message}}`);
                        }}
                    }};
                    
                    ws.onclose = function(event) {{
                        statusElement.textContent = 'Disconnected';
                        log('Connection closed');
                    }};
                    
                    ws.onerror = function(event) {{
                        statusElement.textContent = 'Error';
                        log('WebSocket error');
                    }};
                }}
                
                // Disconnect WebSocket
                function disconnect() {{
                    if (ws) {{
                        ws.close();
                        ws = null;
                    }}
                }}
                
                // Get game state
                function getState() {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        const message = {{
                            type: 'get_state'
                        }};
                        ws.send(JSON.stringify(message));
                        log(`Sent: ${{JSON.stringify(message)}}`);
                    }} else {{
                        log('WebSocket not connected');
                    }}
                }}
                
                // Request AI move
                function aiMove() {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        const message = {{
                            type: 'ai_move'
                        }};
                        ws.send(JSON.stringify(message));
                        log(`Sent: ${{JSON.stringify(message)}}`);
                    }} else {{
                        log('WebSocket not connected');
                    }}
                }}
                
                // Update board display based on game state
                function updateBoardDisplay(state) {{
                    // Simple display of game state as JSON
                    boardElement.innerHTML = `<pre>${{JSON.stringify(state, null, 2)}}</pre>`;
                    
                    // For real implementation, create a proper game board visualization
                    // based on the specific game type
                }}
            </script>
        </body>
    </html>
    """


def create_game_router_app():
    """Create a standalone FastAPI app for game routes."""
    # Create FastAPI app
    app = FastAPI(title="Haive Games API", description="API for Haive game agents")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    @app.get("/", response_class=HTMLResponse)
    async def get_index():
        """Serve the index page."""
        return get_index_html()

    @app.get("/games/{game_type}", response_class=HTMLResponse)
    async def get_game_client(game_type: str):
        """Serve the game client page."""
        if game_type not in game_agents:
            raise HTTPException(
                status_code=404, detail=f"Game type {game_type} not found"
            )

        return get_game_client_html(game_type)

    # Discover game agents
    discover_game_agents()

    # Create routers for each game type
    for game_type in game_agents:
        try:
            router = create_game_router(game_type)
            app.include_router(router, prefix="/api", tags=[game_type])
            logger.info(f"Registered routes for {game_type}")
        except Exception as e:
            logger.error(f"Error creating router for {game_type}: {e}")

    return app


def setup_routes(app):
    """Set up routes for all discovered game agents."""
    # Create standalone app to get all the routes
    game_app = create_game_router_app()

    # Include all routes from the game app into the main app
    for route in game_app.routes:
        app.routes.append(route)

    return app


def get_router():
    """Get a router with all game routes configured."""
    # Discover game agents
    discover_game_agents()

    # Create main router (no prefix since it's added in app.py)
    router = APIRouter(tags=["Games"])

    # Add index route
    @router.get("/", response_class=HTMLResponse)
    async def get_game_index():
        """Serve the index page."""
        return get_index_html()

    @router.get("/{game_type}", response_class=HTMLResponse)
    async def get_game_client_page(game_type: str):
        """Serve the game client page."""
        if game_type not in game_agents:
            raise HTTPException(
                status_code=404, detail=f"Game type {game_type} not found"
            )

        return get_game_client_html(game_type)

    # Add routes for each game type
    for game_type in game_agents:
        try:
            game_router = create_game_router(game_type)
            router.include_router(game_router, prefix=f"/{game_type}")
            logger.info(f"Registered routes for {game_type}")
        except Exception as e:
            logger.error(f"Error creating router for {game_type}: {e}")

    return router


def main():
    """Run the API server as standalone."""
    import uvicorn

    # Create a new app
    app = create_game_router_app()

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8005)


if __name__ == "__main__":
    main()
