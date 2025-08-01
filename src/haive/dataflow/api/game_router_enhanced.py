#!/usr/bin/env python
"""Enhanced Game Discovery and WebSocket API for Haive Games.

This module provides a comprehensive game discovery and management system using
haive-core's unified discovery infrastructure. It creates WebSocket endpoints
for real-time game state streaming and REST endpoints for game management.

Key Features:
    - Automatic discovery of game agents using haive-core
    - WebSocket-based real-time game state streaming
    - REST API for game creation and management
    - HTML client generation for browser-based gameplay
    - Support for multiple concurrent game sessions
    - Flexible agent initialization patterns

Architecture:
    - Uses HaiveComponentDiscovery for finding game agents
    - Creates dynamic routes for each discovered game
    - Maintains active game sessions in memory
    - Provides WebSocket connections for real-time updates

Example:
    ```python
    # Run as standalone server
    python game_router_enhanced.py

    # Or integrate into existing FastAPI app
    from haive.dataflow.api.game_router_enhanced import get_router

    app = FastAPI()
    games_router = get_router()
    app.include_router(games_router, prefix="/games")
    ```

Note:
    This implementation fixes the circular import issue and uses the
    unified discovery system from haive-core for consistency.
"""

import contextlib
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from haive.dataflow.api.utils.haive_discovery import (
    ComponentInfo,
    HaiveComponentDiscovery,
)

# Import discovery system


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("game-router")

# Module-level registries
active_connections: dict[str, set[WebSocket]] = {}  # game_type -> {websockets}
active_games: dict[str, dict[str, Any]] = {}  # game_id -> game_state
game_agents: dict[str, dict[str, Any]] = {}  # game_type -> agent_info

# Get haive root path
HAIVE_ROOT = Path(__file__).parents[6]


def discover_game_agents() -> None:
    """Discover game agents using the unified discovery system.

    This function scans the haive-games package for agent classes and
    their corresponding state classes, registering them for use.

    Discovery Process:
        1. Uses HaiveComponentDiscovery to find all components
        2. Filters for classes ending with 'Agent'
        3. Associates state classes with their agents
        4. Groups by game module for complete game discovery

    Side Effects:
        Updates the global game_agents registry with discovered games.

    Note:
        Skips base classes like 'BaseAgent', 'GenericAgent', etc.
    """
    try:
        logger.info(
            "Starting game agent discovery using haive-core discovery system..."
        )

        # Create discovery instance
        discovery = HaiveComponentDiscovery(str(HAIVE_ROOT))

        # Discover from games package
        games_path = HAIVE_ROOT / "packages" / "haive-games" / "src" / "haive" / "games"

        if not games_path.exists():
            logger.warning(f"Games path does not exist: {games_path}")
            return

        # Discover all components in the games package
        game_components = discovery.discover_from_directory(
            games_path, "haive.games", create_tools=False
        )

        logger.info(f"Found {len(game_components)} components in games package")

        # Process discovered components
        _process_game_components(game_components)

        logger.info(f"Total game agents discovered: {len(game_agents)}")
        logger.info(f"Available games: {list(game_agents.keys())}")

    except Exception as e:
        logger.error(f"Error discovering game agents: {e}", exc_info=True)


def _process_game_components(components: list[ComponentInfo]) -> None:
    """Process discovered components to identify game agents.

    Args:
        components: List of discovered components from the games package.

    Note:
        This function populates the global game_agents registry.
    """
    # First pass: Find agent classes
    for component in components:
        if component.name.endswith("Agent") and component.class_obj is not None:
            # Extract game name
            game_name = component.name.replace("Agent", "").lower()

            # Skip base classes
            if game_name in ["base", "generic", "game", ""]:
                continue

            game_agents[game_name] = {
                "name": game_name,
                "agent_class": component.class_obj,
                "module": component.module_path,
                "component_info": component,
                "discovered_at": datetime.now().isoformat(),
            }

            logger.info(
                f"Registered game agent: {game_name} from {component.module_path}"
            )

    # Second pass: Find state classes
    for component in components:
        if component.name.endswith("State"):
            # Find corresponding agent
            game_name = component.name.replace("State", "").lower()
            if game_name in game_agents:
                game_agents[game_name]["state_class"] = component.class_obj
                logger.info(f"Associated state class for {game_name}")

    # Third pass: Module-based discovery
    _discover_by_module_pattern(components)


def _discover_by_module_pattern(components: list[ComponentInfo]) -> None:
    """Discover games by module organization pattern.

    Args:
        components: List of all discovered components.

    Note:
        This catches games that might have non-standard naming
        but follow the module organization pattern.
    """
    game_modules = {}

    for component in components:
        # Extract module name
        module_parts = component.module_path.split(".")
        if len(module_parts) < 2:
            continue

        module_name = module_parts[-2]

        # Skip framework modules
        if module_name in ["base", "framework", "core", "common"]:
            continue

        if module_name not in game_modules:
            game_modules[module_name] = {}

        if component.name.endswith("Agent"):
            game_modules[module_name]["agent"] = component
        elif component.name.endswith("State"):
            game_modules[module_name]["state"] = component

    # Add complete game modules not already discovered
    for game_name, components in game_modules.items():
        if "agent" in components and game_name not in game_agents:
            game_agents[game_name] = {
                "name": game_name,
                "agent_class": components["agent"].class_obj,
                "module": components["agent"].module_path,
                "component_info": components["agent"],
                "discovered_at": datetime.now().isoformat(),
            }

            if "state" in components:
                game_agents[game_name]["state_class"] = components["state"].class_obj

            logger.info(f"Registered game module: {game_name}")


def create_game_instance(game_type: str, game_id: str) -> dict[str, Any]:
    """Create or retrieve a game instance.

    Args:
        game_type: Type of game to create (e.g., 'chess', 'checkers').
        game_id: Unique identifier for the game session.

    Returns:
        Dict[str, Any]: Game instance information including:
            - agent: The instantiated game agent
            - game_id: Unique game identifier
            - game_type: Type of game
            - created_at: Creation timestamp
            - agent_info: Metadata about the agent

    Raises:
        ValueError: If game_type is not recognized.
        RuntimeError: If agent instantiation fails.

    Note:
        Tries multiple initialization patterns to accommodate
        different agent implementations.
    """
    if game_type not in game_agents:
        raise TypeError(f"Unknown game type: {game_type}")

    # Create unique key for this game
    game_key = f"{game_type}:{game_id}"

    if game_key not in active_games:
        agent_info = game_agents[game_type]
        agent = _instantiate_agent(agent_info, game_type, game_id)

        # Store in active games
        active_games[game_key] = {
            "agent": agent,
            "game_id": game_id,
            "game_type": game_type,
            "created_at": datetime.now().isoformat(),
            "agent_info": agent_info,
        }

        logger.info(f"Created new game instance: {game_type}:{game_id}")

    return active_games[game_key]


def _instantiate_agent(agent_info: dict[str, Any], game_type: str, game_id: str) -> Any:
    """Instantiate a game agent with appropriate initialization.

    Args:
        agent_info: Agent metadata and class information.
        game_type: Type of game.
        game_id: Unique game identifier.

    Returns:
        Any: Instantiated agent object.

    Raises:
        RuntimeError: If all initialization patterns fail.
    """
    agent_class = agent_info["agent_class"]
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
            return agent
        except Exception as e:
            logger.debug(f"Config pattern failed: {e}")

    # Pattern 2: Direct initialization with name
    try:
        agent = agent_class(name=f"{game_type}_{game_id}")
        logger.info(f"Created agent with name pattern for {game_type}")
        return agent
    except Exception as e:
        logger.debug(f"Name pattern failed: {e}")

    # Pattern 3: No arguments
    try:
        agent = agent_class()
        logger.info(f"Created agent with no-args pattern for {game_type}")
        return agent
    except Exception as e:
        logger.debug(f"No-args pattern failed: {e}")

    raise RuntimeError(f"Failed to create agent instance for {game_type}")


def get_game_instance(game_type: str, game_id: str) -> dict[str, Any] | None:
    """Retrieve an existing game instance.

    Args:
        game_type: Type of game.
        game_id: Unique game identifier.

    Returns:
        Optional[Dict[str, Any]]: Game instance if found, None otherwise.
    """
    game_key = f"{game_type}:{game_id}"
    return active_games.get(game_key)


def create_game_router(game_type: str) -> APIRouter:
    """Create a router for a specific game type.

    Args:
        game_type: Type of game to create routes for.

    Returns:
        APIRouter: Configured router with WebSocket and REST endpoints.

    Raises:
        ValueError: If game_type is not recognized.

    Note:
        Creates the following endpoints:
        - WebSocket: /ws/{game_type}/{game_id}
        - POST: /{game_type}/games - Create new game
    """
    if game_type not in game_agents:
        raise TypeError(f"Unknown game type: {game_type}")

    router = APIRouter(tags=[f"{game_type} Game"])
    agent_info = game_agents[game_type]
    component_info = agent_info.get("component_info")

    # Register WebSocket endpoint
    @router.websocket(f"/ws/{game_type}/{{game_id}}")
    async def game_websocket(websocket: WebSocket, game_id: str):
        """WebSocket endpoint for real-time game state streaming.

        Args:
            websocket: WebSocket connection object.
            game_id: Unique identifier for the game session.

        WebSocket Protocol:
            Incoming Messages:
                - {"type": "get_state"}: Request current game state
                - {"type": "make_move", "move": {...}}: Make a player move
                - {"type": "ai_move"}: Request AI to make a move

            Outgoing Messages:
                - {"type": "state_update", "state": {...}}: Game state update
                - {"type": "error", "message": "..."}: Error notification
        """
        await _handle_game_websocket(websocket, game_type, game_id, agent_info)

    # Register REST endpoint to create a new game
    @router.post(f"/{game_type}/games", tags=[f"{game_type}"])
    async def create_game():
        """Create a new game session.

        Returns:
            Dict containing:
                - game_type: Type of game created
                - game_id: Unique game identifier
                - ws_url: WebSocket URL for connecting
                - metadata: Additional game information
        """
        game_id = f"{game_type}_{uuid.uuid4().hex[:8]}"
        create_game_instance(game_type, game_id)

        return {
            "game_type": game_type,
            "game_id": game_id,
            "ws_url": f"/ws/{game_type}/{game_id}",
            "metadata": {
                "description": component_info.description if component_info else None,
                "module": agent_info["module"],
                "discovered_at": agent_info.get("discovered_at"),
            },
        }

    return router


async def _handle_game_websocket(
    websocket: WebSocket, game_type: str, game_id: str, agent_info: dict[str, Any]
) -> None:
    """Handle WebSocket connection for a game session.

    Args:
        websocket: WebSocket connection object.
        game_type: Type of game.
        game_id: Unique game identifier.
        agent_info: Agent metadata.

    Note:
        This function manages the entire WebSocket lifecycle including
        connection, message handling, and cleanup.
    """
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {game_type} game: {game_id}")
    except Exception as e:
        logger.exception(f"Failed to accept WebSocket connection: {e}")
        return

    # Register connection
    if game_type not in active_connections:
        active_connections[game_type] = set()
    active_connections[game_type].add(websocket)

    try:
        # Initialize game
        game = await _initialize_game_session(websocket, game_type, game_id, agent_info)
        if not game:
            return

        agent = game["agent"]

        # Main message loop
        await _handle_game_messages(websocket, agent, game_type, game_id)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {game_type} game: {game_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {game_type}:{game_id}: {e}", exc_info=True)
        with contextlib.suppress(BaseException):
            await websocket.send_json(
                {"type": "error", "message": f"Server error: {e!s}"}
            )
    finally:
        # Clean up connection
        if game_type in active_connections:
            active_connections[game_type].discard(websocket)
        logger.info(f"Cleaned up WebSocket connection for {game_type}:{game_id}")


async def _initialize_game_session(
    websocket: WebSocket, game_type: str, game_id: str, agent_info: dict[str, Any]
) -> dict[str, Any] | None:
    """Initialize a game session and send initial state.

    Args:
        websocket: WebSocket connection.
        game_type: Type of game.
        game_id: Game identifier.
        agent_info: Agent metadata.

    Returns:
        Optional[Dict[str, Any]]: Game instance or None if initialization fails.
    """
    try:
        game = create_game_instance(game_type, game_id)
        agent = game["agent"]

        # Send initial state
        initial_state = {}
        state = agent.run(initial_state, thread_id=game_id)

        component_info = agent_info.get("component_info")
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

        return game

    except Exception as e:
        logger.exception(f"Failed to initialize game: {e}")
        await websocket.send_json(
            {
                "type": "error",
                "message": f"Failed to initialize game: {e!s}",
                "game_type": game_type,
            }
        )
        return None


async def _handle_game_messages(
    websocket: WebSocket, agent: Any, game_type: str, game_id: str
) -> None:
    """Handle incoming WebSocket messages for a game.

    Args:
        websocket: WebSocket connection.
        agent: Game agent instance.
        game_type: Type of game.
        game_id: Game identifier.
    """
    while True:
        try:
            data = await websocket.receive_json()
            message_type = data.get("type", "")
            logger.info(f"Received message for {game_type}:{game_id}: {message_type}")

            if message_type == "get_state":
                await _handle_get_state(websocket, agent, game_type, game_id)
            elif message_type == "make_move":
                await _handle_make_move(websocket, agent, game_type, game_id, data)
            elif message_type == "ai_move":
                await _handle_ai_move(websocket, agent, game_type, game_id)
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                )

        except Exception as e:
            logger.exception(f"Error processing WebSocket message: {e}")
            try:
                await websocket.send_json(
                    {"type": "error", "message": f"Error processing message: {e!s}"}
                )
            except BaseException:
                break


async def _handle_get_state(
    websocket: WebSocket, agent: Any, game_type: str, game_id: str
) -> None:
    """Handle get_state message."""
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
        logger.exception(f"Error getting state: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"Failed to get state: {e!s}"}
        )


async def _handle_make_move(
    websocket: WebSocket, agent: Any, game_type: str, game_id: str, data: dict[str, Any]
) -> None:
    """Handle make_move message."""
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
        logger.exception(f"Error making move: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"Failed to make move: {e!s}"}
        )


async def _handle_ai_move(
    websocket: WebSocket, agent: Any, game_type: str, game_id: str
) -> None:
    """Handle ai_move message."""
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
        logger.exception(f"Error making AI move: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"Failed to make AI move: {e!s}"}
        )


def get_router() -> APIRouter:
    """Get a router with all game routes configured.

    Returns:
        APIRouter: Main router containing all game-specific routers
        and the index page.

    Note:
        This function triggers game discovery if not already done.
    """
    # Discover game agents
    discover_game_agents()

    # Create main router
    router = APIRouter(tags=["Games"])

    # Add index route
    @router.get("/", response_class=HTMLResponse)
    async def get_game_index():
        """Serve the game index page.

        Returns:
            HTMLResponse: HTML page listing all available games.
        """
        return get_index_html()

    @router.get("/{game_type}", response_class=HTMLResponse)
    async def get_game_client_page(game_type: str):
        """Serve the game client page.

        Args:
            game_type: Type of game to display.

        Returns:
            HTMLResponse: HTML game client for the specified game.

        Raises:
            HTTPException: 404 if game type not found.
        """
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
            logger.info(f"Registered routes for {game_type}")
        except Exception as e:
            logger.exception(f"Error creating router for {game_type}: {e}")

    return router


def get_index_html() -> str:
    """Generate HTML for the index page with links to all games.

    Returns:
        str: HTML content for the game index page.
    """
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
            f'<li><a href="/games/{game_type}">{game_type.title()}</a> - {description}</li>'
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
                {"".join(game_links) if game_links else "<li>No games discovered. Check server logs.</li>"}
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


def get_game_client_html(game_type: str) -> str:
    """Generate HTML for a specific game client.

    Args:
        game_type: Type of game to generate client for.

    Returns:
        str: HTML content for the game client page.
    """
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
                        Module: {agent_info.get("module", "Unknown")}<br>
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
                // Game client JavaScript code
                {_get_game_client_javascript()}
            </script>
        </body>
    </html>
    """


def _get_game_client_javascript() -> str:
    """Get JavaScript code for the game client.

    Returns:
        str: JavaScript code for WebSocket communication and game UI.
    """
    return """
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
    function log(message, type = 'info') {
        const entry = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString();
        entry.textContent = `[${timestamp}] ${message}`;
        if (type === 'error') {
            entry.style.color = 'red';
        } else if (type === 'success') {
            entry.style.color = 'green';
        }
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
    }

    // Connect to WebSocket
    function connect() {
        const gameId = document.getElementById('gameId').value;

        if (!gameId) {
            log('Please enter a game ID', 'error');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const gameType = window.location.pathname.split('/').filter(x => x)[1];
        const wsUrl = `${protocol}//${window.location.host}/ws/${gameType}/${gameId}`;

        if (ws) {
            ws.close();
        }

        log(`Connecting to ${wsUrl}...`);
        ws = new WebSocket(wsUrl);

        ws.onopen = function(event) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status-connected';
            log('Connection established', 'success');
        };

        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                log(`Received: ${data.type}`);

                if (data.type === 'state_update') {
                    gameState = data.state;
                    updateBoardDisplay(gameState);
                    updateGameInfo(gameState);

                    if (data.last_action) {
                        log(`Last action: ${data.last_action}`, 'success');
                    }
                } else if (data.type === 'error') {
                    log(`Error: ${data.message}`, 'error');
                    showError(data.message);
                }
            } catch (e) {
                log(`Error parsing message: ${e.message}`, 'error');
            }
        };

        ws.onclose = function(event) {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status-disconnected';
            log('Connection closed');
        };

        ws.onerror = function(event) {
            statusElement.textContent = 'Error';
            statusElement.className = 'status-disconnected';
            log('WebSocket error', 'error');
        };
    }

    // Disconnect WebSocket
    function disconnect() {
        if (ws) {
            ws.close();
            ws = null;
            log('Disconnected');
        }
    }

    // Get game state
    function getState() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const message = {
                type: 'get_state'
            };
            ws.send(JSON.stringify(message));
            log('Sent: get_state');
        } else {
            log('WebSocket not connected', 'error');
        }
    }

    // Request AI move
    function aiMove() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const message = {
                type: 'ai_move'
            };
            ws.send(JSON.stringify(message));
            log('Sent: ai_move');
        } else {
            log('WebSocket not connected', 'error');
        }
    }

    // Show error message
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        boardElement.insertBefore(errorDiv, boardElement.firstChild);

        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Update game info display
    function updateGameInfo(state) {
        turnElement.textContent = state.current_player || state.turn || '-';
        gameStatusElement.textContent = state.game_status || state.status || 'Active';
    }

    // Update board display based on game state
    function updateBoardDisplay(state) {
        // Clear previous errors
        const errors = boardElement.querySelectorAll('.error-message');
        errors.forEach(e => e.remove());

        // Simple display of game state as JSON
        boardElement.innerHTML = `<pre>${JSON.stringify(state, null, 2)}</pre>`;

        // TODO: Implement game-specific visualization
        // This would be customized per game type
    }

    // Auto-connect on page load
    window.addEventListener('load', () => {
        log('Page loaded. Click Connect to start.');
    });
    """


def create_game_router_app() -> FastAPI:
    """Create a standalone FastAPI app for game routes.

    Returns:
        FastAPI: Configured FastAPI application with game routes.

    Note:
        Includes CORS middleware for browser compatibility.
    """
    # Create FastAPI app
    app = FastAPI(
        title="Haive Games API",
        description="Real-time game API using haive-core unified discovery system",
        version="2.0",
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
        """Health check endpoint.

        Returns:
            Dict containing:
                - status: Service status
                - available_games: List of discovered games
                - game_count: Number of games
                - discovery_method: Discovery method used
                - active_games: Number of active game sessions
        """
        return {
            "status": "ok",
            "available_games": list(game_agents.keys()),
            "game_count": len(game_agents),
            "discovery_method": "haive-core unified discovery",
            "active_games": len(active_games),
        }

    return app


def main():
    """Run the API server as standalone application."""
    # Create app
    app = create_game_router_app()

    # Run server
    logger.info("Starting Games API server on http://localhost:8005")
    logger.info("Access the game list at http://localhost:8005/games")
    uvicorn.run(app, host="0.0.0.0", port=8005)


if __name__ == "__main__":
    main()
