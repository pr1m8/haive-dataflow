"""Games router for the Haive API.

This module provides API routes for the general games system,
integrating with the haive-games package.
"""

import logging

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from haive.games.api import GameInfo, GameSelectionRequest, create_general_game_api

# Import games API
try:
    GAMES_AVAILABLE = True
except ImportError:
    GAMES_AVAILABLE = False
    GameInfo = None
    GameSelectionRequest = None

logger = logging.getLogger(__name__)


def create_games_router(
    prefix: str = "/games",
    tags: list[str] | None = None,
    exclude_games: list[str] | None = None,
) -> APIRouter:
    """Create a router for the games API.

    Args:
        prefix: URL prefix for the router
        tags: OpenAPI tags for the routes
        exclude_games: List of games to exclude

    Returns:
        APIRouter with games endpoints
    """
    router = APIRouter(
        prefix=prefix,
        tags=tags or ["games"],
        responses={
            404: {"description": "Game not found"},
            400: {"description": "Invalid request"},
        },
    )

    if not GAMES_AVAILABLE:

        @router.get("/")
        async def games_not_available():
            """Games Not Available.
"""
            return JSONResponse(
                status_code=501,
                content={
                    "error": "Games module not available",
                    "message": "Please install haive-games package",
                },
            )

        return router

    # Create a sub-app for games

    games_app = FastAPI()

    # Initialize the general games API
    try:
        _, game_api = create_general_game_api(
            app=games_app, exclude_games=exclude_games
        )

        # Mount the games app routes
        @router.get("/", response_model=list[GameInfo])
        async def list_games():
            """List all available games."""
            # Forward to the games API
            return await games_app.router.routes[0].endpoint()

        @router.post("/create")
        async def create_game(request: GameSelectionRequest):
            """Create a new game with the specified configuration."""
            # Forward to the games API
            for route in games_app.router.routes:
                if route.path == "/api/games/create" and route.methods == {"POST"}:
                    return await route.endpoint(request)

            raise HTTPException(status_code=500, detail="Create endpoint not found")

        # Add game-specific sub-routers
        for game_id in game_api.discovered_games:
            game_router = APIRouter(prefix=f"/{game_id}", tags=[f"game:{game_id}"])

            @game_router.get("/{thread_id}")
            async def get_game_state(thread_id: str, game_id: str = game_id):
                """Get the current state of a game."""
                # This would forward to the game-specific API
                return {
                    "game_id": game_id,
                    "thread_id": thread_id,
                    "message": f"Game state for {game_id}",
                }

            @game_router.post("/{thread_id}/move")
            async def make_move(
                thread_id: str, move_data: dict, game_id: str = game_id
            ):
                """Make a move in the game."""
                return {
                    "game_id": game_id,
                    "thread_id": thread_id,
                    "move": move_data,
                    "message": f"Move made in {game_id}",
                }

            @game_router.get("/{thread_id}/ai-move")
            async def ai_move(thread_id: str, game_id: str = game_id):
                """Let the AI make a move."""
                return {
                    "game_id": game_id,
                    "thread_id": thread_id,
                    "message": f"AI move in {game_id}",
                }

            router.include_router(game_router)

        # Add metadata endpoint
        @router.get("/meta")
        async def get_games_metadata():
            """Get metadata about available games."""
            return {
                "total_games": len(game_api.discovered_games),
                "games": list(game_api.discovered_games.keys()),
                "excluded_games": game_api.exclude_games,
                "api_version": "1.0.0",
            }

        logger.info(
            f"Games router initialized with {len(game_api.discovered_games)} games"
        )

    except Exception as e:
        logger.exception(f"Failed to initialize games API: {e}")
        error_message = str(e)

        @router.get("/")
        async def games_error():
            """Games Error.
"""
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to initialize games",
                    "message": error_message,
                },
            )

    return router


# Dependency for getting game API instance
_game_api_instance = None


def get_game_api():
    """Get the game API instance (singleton)."""
    global _game_api_instance

    if _game_api_instance is None and GAMES_AVAILABLE:
        app = FastAPI()
        _, _game_api_instance = create_general_game_api(app)

    return _game_api_instance


# WebSocket router for games
def create_games_websocket_router(prefix: str = "/ws/games") -> APIRouter:
    """Create WebSocket routes for games.

    Args:
        prefix: URL prefix for WebSocket routes

    Returns:
        APIRouter with WebSocket endpoints
    """
    router = APIRouter(prefix=prefix)

    if not GAMES_AVAILABLE:
        return router

    @router.websocket("/{game_id}/{thread_id}")
    async def game_websocket(websocket: WebSocket, game_id: str, thread_id: str):
        """WebSocket endpoint for real-time game updates."""
        await websocket.accept()

        try:
            # Get game API
            game_api = get_game_api()

            if game_api and game_id in game_api.discovered_games:
                # Forward to game-specific WebSocket handler
                await websocket.send_json(
                    {
                        "type": "connected",
                        "game_id": game_id,
                        "thread_id": thread_id,
                        "message": f"Connected to {game_id} game",
                    }
                )

                # Handle messages
                while True:
                    data = await websocket.receive_json()

                    # Process game commands
                    if data.get("type") == "move":
                        await websocket.send_json(
                            {
                                "type": "move_response",
                                "status": "processing",
                                "move": data.get("move"),
                            }
                        )
                    elif data.get("type") == "ai_move":
                        await websocket.send_json(
                            {"type": "ai_thinking", "status": "processing"}
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": f"Unknown command: {data.get('type')}",
                            }
                        )
            else:
                await websocket.send_json(
                    {"type": "error", "message": f"Game '{game_id}' not found"}
                )
                await websocket.close()

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for {game_id}/{thread_id}")
        except Exception as e:
            logger.exception(f"WebSocket error: {e}")
            await websocket.close()

    return router
