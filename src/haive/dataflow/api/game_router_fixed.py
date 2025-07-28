"""Game_Router_Fixed core module.

This module provides game router fixed functionality for the Haive framework.

Classes:
    state_name: state_name implementation.
    game_modules: game_modules implementation.

Functions:
    discover_game_agents: Discover Game Agents functionality.
    create_game_instance: Create Game Instance functionality.
    get_game_instance: Get Game Instance functionality.
"""

#!/usr/bin/env python
"""Game API router for Haive games using the discovery system.

This module discovers and loads game agents from haive-games package
using the centralized discovery system, creating routes for each available game.
It provides WebSocket endpoints for streaming game state and interacting with game agents.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Set

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import discovery system
from haive.core.utils.haive_discovery import (
    HaiveComponentDiscovery,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("game-routef")

# Active connections and games
active_connections: Dict[str, Set[WebSocket]] = {}  # game_type -> {websockets}
active_games: Dict[str, Dict[str, Any]] = {}  # game_id -> game_state

# Game agent registry
game_agents = {}


def discover_game_agents():
    """Discover game agents using the unified discovery system."""
    try:
        logger.info(
            "🔍 Starting game agent discovery using haive-core discovery system..."
        )

        # Get haive root from current location
        current_file = Path(__file__)
        haive_root = current_file.parents[6]  # Navigate up to haive root

        # Create discovery instance
        discovery = HaiveComponentDiscovery(str(haive_root))

        # Discover from games package
        games_path = haive_root / "packages" / "haive-games" / "src" / "haive" / "games"

        if not games_path.exists():
            logger.warning(f"Games path does not exist: {games_path}")
            return

        # Discover all components in the games package
        game_components = discovery.discover_from_directory(
            games_path, "haive.games", create_tools=False
        )

        logger.info(f"Found {len(game_components)} components in games package")

        # Filter for agent classes
        for component in game_components:
            if component.name.endswith("Agent") and component.class_obj is not None:
                # Extract game name
                game_name = component.name.replace("Agent", "").lower()

                # Skip base classes
                if game_name in ["base", "generic", "game"]:
                    continue

                game_agents[game_name] = {
                    "name": game_name,
                    "agent_class": component.class_obj,
                    "module": component.module_path,
                    "component_info": component,
                }

                # Try to find corresponding state class
                state_name = f"{game_name.title()}State"
                state_components = [c for c in game_components if c.name == state_name]
                if state_components:
                    game_agents[game_name]["state_class"] = state_components[
                        0
                    ].class_obj

                logger.info(
                    f"✅ Registered game agent: {game_name} from {component.module_path}"
                )

        # Also try to discover using pattern matching
        # Look for modules that have both an agent and state class
        game_modules = {}
        for component in game_components:
            # Group by module
            module_name = (
                component.module_path.split(".")[-2]
                if "." in component.module_path
                else None
            )
            if module_name and module_name not in ["base", "framework", "core"]:
                if module_name not in game_modules:
                    game_modules[module_name] = {}

                if component.name.endswith("Agent"):
                    game_modules[module_name]["agent"] = component
                elif component.name.endswith("State"):
                    game_modules[module_name]["state"] = component

        # Add complete game modules
        for game_name, components in game_modules.items():
            if "agent" in components and game_name not in game_agents:
                game_agents[game_name] = {
                    "name": game_name,
                    "agent_class": components["agent"].class_obj,
                    "module": components["agent"].module_path,
                    "component_info": components["agent"],
                }
                if "state" in components:
                    game_agents[game_name]["state_class"] = components[
                        "state"
                    ].class_obj

                logger.info(f"✅ Registered game module: {game_name}")

        logger.info(f"📊 Total game agents discovered: {len(game_agents)}")
        logger.info(f"🎮 Available games: {list(game_agents.keys())}")

    except Exception as e:
        logger.error(f"❌ Error discovering game agents: {e}", exc_info=True)


def create_game_instance(game_type: str, game_id: str) -> Dict[str, Any]:
    """Create or get a game instance."""
    if game_type not in game_agents:
        raise ValueError(f"Unknown game type: {game_type}")

    # Create unique key for this game
    game_key = f"{game_type}:{game_id}"

    if game_key not in active_games:
        try:
            # Get agent info
            agent_info = game_agents[game_type]
            agent_class = agent_info["agent_class"]

            # Create agent instance
            # Try different initialization patterns
            agent = None

            # Pattern 1: Config-based initialization
            if hasattr(agent_class, "get_config_class"):
                try:
                    config_class = agent_class.get_config_class()
                    config = config_class(
                        name=f"{game_type}_{game_id}",
                        runnable_config={"configurable": {"thread_id": game_id}},
                    )
                    agent = agent_class(config=config)
                    logger.info(f"Created agent with config pattern for {game_type}")
                except Exception as e:
                    logger.debug(f"Config pattern failed: {e}")

            # Pattern 2: Direct initialization with name
            if agent is None:
                try:
                    agent = agent_class(name=f"{game_type}_{game_id}")
                    logger.info(f"Created agent with name pattern for {game_type}")
                except Exception as e:
                    logger.debug(f"Name pattern failed: {e}")

            # Pattern 3: No arguments
            if agent is None:
                try:
                    agent = agent_class()
                    logger.info(f"Created agent with no-args pattern for {game_type}")
                except Exception as e:
                    logger.debug(f"No-args pattern failed: {e}")

            if agent is None:
                raise RuntimeError(f"Failed to create agent instance for {game_type}")

            # Store in active games
            active_games[game_key] = {
                "agent": agent,
                "game_id": game_id,
                "game_type": game_type,
                "created_at": asyncio.get_event_loop().time(),
                "agent_info": agent_info,
            }

            logger.info(f"✅ Created new game instance: {game_type}:{game_id}")

        except Exception as e:
            logger.error(
                f"❌ Error creating game instance {game_type}:{game_id}: {e}",
                exc_info=True,
            )
            raise

    return active_games[game_key]


def get_game_instance(game_type: str, game_id: str) -> Dict[str, Any]:
    """Get an existing game instance."""
    game_key = f"{game_type}:{game_id}"
    return active_games.get(game_key)


def create_game_router(game_type: str) -> APIRouter:
    """Create a router for a specific game type."""
    if game_type not in game_agents:
        raise ValueError(f"Unknown game type: {game_type}")

    router = APIRouter(tags=[f"{game_type} Game"])
    agent_info = game_agents[game_type]
    component_info = agent_info.get("component_info")

    # Register WebSocket endpoint
    @router.websocket(f"/ws/{game_type}/{{game_id}}")
    async def game_websocket(websocket: WebSocket, game_id: str):
        """WebSocket endpoint for game state streaming."""
        try:
            await websocket.accept()
            logger.info(
                f"🔌 WebSocket connection accepted for {game_type} game: {game_id}"
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
                    {
                        "type": "error",
                        "message": f"Failed to create game: {str(e)}",
                        "game_type": game_type,
                    }
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
                        "metadata": {
                            "description": (
                                component_info.description if component_info else None
                            ),
                            "module": agent_info["module"],
                        },
                    }
                )
            except Exception as e:
                logger.error(f"Failed to get initial state: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Failed to get initial state: {str(e)}",
                    }
                )

            # Main WebSocket loop
            while True:
                try:
                    # Receive message
                    data = await websocket.receive_json()
                    message_type = data.get("type", "")
                    logger.info(
                        f"📨 Received message for {game_type}:{game_id}: {message_type}"
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
                                    "message": f"Failed to get state: {str(e)}",
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
                                    "message": f"Failed to make move: {str(e)}",
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
                                    "message": f"Failed to make AI move: {str(e)}",
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
                                "message": f"Error processing message: {str(e)}",
                            }
                        )
                    except:
                        # Connection might be closed
                        break

        except WebSocketDisconnect:
            # Handle disconnection
            logger.info(f"🔌 WebSocket disconnected for {game_type} game: {game_id}")
        except Exception as e:
            # Handle other errors
            logger.error(
                f"❌ WebSocket error for {game_type}:{game_id}: {e}", exc_info=True
            )
            try:
                await websocket.send_json(
                    {"type": "error", "message": f"Server error: {str(e)}"}
                )
            except:
                # Connection might be closed, ignore send error
                pass
        finally:
            # Always clean up connection
            if game_type in active_connections:
                active_connections[game_type].discard(websocket)
            logger.info(f"🧹 Cleaned up WebSocket connection for {game_type}:{game_id}")

    # Register REST endpoint to create a new game
    @router.post(f"/{game_type}/games", tags=[f"{game_type}"])
    async def create_game():
        """Create a new game."""
        import uuid

        game_id = f"{game_type}_{uuid.uuid4().hex[:8]}"
        create_game_instance(game_type, game_id)

        return {
            "game_type": game_type,
            "game_id": game_id,
            "ws_url": f"/ws/{game_type}/{game_id}",
            "metadata": {
                "description": component_info.description if component_info else None,
                "module": agent_info["module"],
            },
        }

    return router


# HTML for the main index page
def get_index_html():
    """Generate HTML for the index page with links to all games."""
    game_links = []
    for game_type in sorted(game_agents.keys()):
        agent_info = game_agents[game_type]
        component_info = agent_info.get("component_info")
        description = (
            component_info.description
            if component_info
            else f"{game_type.title()} game"
        )

        game_links.append(
            f"<li>"
            f'<a href="/games/{game_type}">{game_type.title()}</a>'
            f" - {description}"
            f"</li>"
        )

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
                a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
                a:hover {{ text-decoration: underline; }}
                .discovery-info {{ margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 4px; }}
                .discovery-info h3 {{ margin-top: 0; }}
            </style>
        </head>
        <body>
            <h1>🎮 Haive Games</h1>
            <p>Select a game to play:</p>
            <ul>
                {"".join(game_links) if game_links else '<li>No games discovered. Check server logs.</li>'}
            </ul>
            
            <div class="discovery-info">
                <h3>📊 Discovery Information</h3>
                <p>Games discovered: {len(game_agents)}</p>
                <p>Discovery method: haive-core unified discovery system</p>
                <p>Available games: {", ".join(sorted(game_agents.keys())) if game_agents else "None"}</p>
            </div>
        </body>
    </html>
    """


# HTML template for game client pages
def get_game_client_html(game_type: str):
    """Generate HTML for a specific game client."""
    agent_info = game_agents.get(game_type, {})
    component_info = agent_info.get("component_info")

    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{game_type.title()} Game</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .container {{ display: flex; gap: 20px; }}
                .game-area {{ flex: 2; }}
                .controls {{ flex: 1; padding: 20px; background-color: #f8f9fa; border-radius: 8px; }}
                .log {{ height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 10px; font-family: monospace; font-size: 12px; }}
                .game-info {{ margin-top: 10px; }}
                button {{ padding: 8px 12px; margin: 5px; cursor: pointer; }}
                button:hover {{ background-color: #e9ecef; }}
                .game-board {{ min-height: 400px; border: 1px solid #ccc; padding: 10px; background-color: #fff; }}
                .metadata {{ margin-top: 20px; padding: 10px; background-color: #e9ecef; border-radius: 4px; font-size: 14px; }}
                .status-connected {{ color: green; font-weight: bold; }}
                .status-disconnected {{ color: red; font-weight: bold; }}
                .error-message {{ color: red; padding: 10px; margin: 10px 0; background-color: #fee; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>🎮 {game_type.title()} Game</h1>
            
            <div class="container">
                <div class="game-area">
                    <div id="gameBoard" class="game-board">
                        <p>Game board will appear here after connection.</p>
                    </div>
                    
                    <div class="metadata">
                        <strong>Game Information:</strong><br>
                        Module: {agent_info.get('module', 'Unknown')}<br>
                        {f"Description: {component_info.description}" if component_info and component_info.description else ""}
                    </div>
                </div>
                
                <div class="controls">
                    <h3>🎯 Game Controls</h3>
                    <div>
                        <label for="gameId">Game ID:</label>
                        <input type="text" id="gameId" value="{game_type}_test123">
                        <button onclick="connect()">Connect</button>
                        <button onclick="disconnect()">Disconnect</button>
                    </div>
                    
                    <div class="game-info">
                        <p>Status: <span id="status" class="status-disconnected">Disconnected</span></p>
                        <p>Turn: <span id="turn">-</span></p>
                        <p>Game Status: <span id="gameStatus">-</span></p>
                    </div>
                    
                    <div>
                        <button onclick="getState()">Get State</button>
                        <button onclick="aiMove()">AI Move</button>
                    </div>
                    
                    <h3>📋 Log</h3>
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
                function log(message, type = 'info') {{
                    const entry = document.createElement('div');
                    const timestamp = new Date().toLocaleTimeString();
                    entry.textContent = `[${{timestamp}}] ${{message}}`;
                    if (type === 'error') {{
                        entry.style.color = 'red';
                    }} else if (type === 'success') {{
                        entry.style.color = 'green';
                    }}
                    logElement.appendChild(entry);
                    logElement.scrollTop = logElement.scrollHeight;
                }}
                
                // Connect to WebSocket
                function connect() {{
                    const gameId = document.getElementById('gameId').value;
                    
                    if (!gameId) {{
                        log('Please enter a game ID', 'error');
                        return;
                    }}
                    
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${{protocol}}//${{window.location.host}}/ws/{game_type}/${{gameId}}`;
                    
                    if (ws) {{
                        ws.close();
                    }}
                    
                    log(`Connecting to ${{wsUrl}}...`);
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function(event) {{
                        statusElement.textContent = 'Connected';
                        statusElement.className = 'status-connected';
                        log('Connection established', 'success');
                    }};
                    
                    ws.onmessage = function(event) {{
                        try {{
                            const data = JSON.parse(event.data);
                            log(`Received: ${{data.type}}`);
                            
                            if (data.type === 'state_update') {{
                                gameState = data.state;
                                
                                // Update UI
                                updateBoardDisplay(gameState);
                                turnElement.textContent = gameState.current_player || gameState.turn || '-';
                                gameStatusElement.textContent = gameState.game_status || gameState.status || 'Active';
                                
                                if (data.last_action) {{
                                    log(`Last action: ${{data.last_action}}`, 'success');
                                }}
                            }} else if (data.type === 'error') {{
                                log(`Error: ${{data.message}}`, 'error');
                                showError(data.message);
                            }}
                        }} catch (e) {{
                            log(`Error parsing message: ${{e.message}}`, 'error');
                        }}
                    }};
                    
                    ws.onclose = function(event) {{
                        statusElement.textContent = 'Disconnected';
                        statusElement.className = 'status-disconnected';
                        log('Connection closed');
                    }};
                    
                    ws.onerror = function(event) {{
                        statusElement.textContent = 'Error';
                        statusElement.className = 'status-disconnected';
                        log('WebSocket error', 'error');
                    }};
                }}
                
                // Disconnect WebSocket
                function disconnect() {{
                    if (ws) {{
                        ws.close();
                        ws = null;
                        log('Disconnected');
                    }}
                }}
                
                // Get game state
                function getState() {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        const message = {{
                            type: 'get_state'
                        }};
                        ws.send(JSON.stringify(message));
                        log('Sent: get_state');
                    }} else {{
                        log('WebSocket not connected', 'error');
                    }}
                }}
                
                // Request AI move
                function aiMove() {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        const message = {{
                            type: 'ai_move'
                        }};
                        ws.send(JSON.stringify(message));
                        log('Sent: ai_move');
                    }} else {{
                        log('WebSocket not connected', 'error');
                    }}
                }}
                
                // Show error message
                function showError(message) {{
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = message;
                    boardElement.insertBefore(errorDiv, boardElement.firstChild);
                    
                    // Remove after 5 seconds
                    setTimeout(() => {{
                        errorDiv.remove();
                    }}, 5000);
                }}
                
                // Update board display based on game state
                function updateBoardDisplay(state) {{
                    // Clear previous errors
                    const errors = boardElement.querySelectorAll('.error-message');
                    errors.forEach(e => e.remove());
                    
                    // Simple display of game state as JSON
                    boardElement.innerHTML = `<pre>${{JSON.stringify(state, null, 2)}}</pre>`;
                    
                    // TODO: Implement game-specific visualization
                    // This would be customized per game type
                }}
                
                // Auto-connect on page load
                window.addEventListener('load', () => {{
                    log('Page loaded. Click Connect to start.');
                }});
            </script>
        </body>
    </html>
    """


def get_router():
    """Get a router with all game routes configured."""
    # Discover game agents using the discovery system
    discover_game_agents()

    # Create main router
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
                status_code=404, detail=f"Game type '{game_type}' not found"
            )

        return get_game_client_html(game_type)

    # Add routes for each discovered game type
    for game_type in game_agents:
        try:
            game_router = create_game_router(game_type)
            router.include_router(game_router, prefix=f"/{game_type}")
            logger.info(f"✅ Registered routes for {game_type}")
        except Exception as e:
            logger.error(f"❌ Error creating router for {game_type}: {e}")

    return router


def create_game_router_app():
    """Create a standalone FastAPI app for game routes."""
    # Create FastAPI app
    app = FastAPI(
        title="Haive Games API",
        description="API for Haive game agents with unified discovery system",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Get the router with all game routes
    games_router = get_router()

    # Include the router
    app.include_router(games_router, prefix="/games")

    # Add root redirect
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Redirect to games index."""
        return """
        <html>
            <head>
                <meta http-equiv="refresh" content="0; url=/games">
            </head>
            <body>
                <p>Redirecting to <a href="/games">games</a>...</p>
            </body>
        </html>
        """

    # Add health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "available_games": list(game_agents.keys()),
            "game_count": len(game_agents),
            "discovery_method": "haive-core unified discovery",
        }

    return app


def main():
    """Run the API server as standalone."""
    import uvicorn

    # Create app
    app = create_game_router_app()

    # Run server
    logger.info("🚀 Starting Games API server on http://localhost:8005")
    logger.info("📍 Access the game list at http://localhost:8005/games")
    uvicorn.run(app, host="0.0.0.0", port=8005)


if __name__ == "__main__":
    main()
