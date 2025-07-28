"""Generic game API with WebSocket support and Supabase integration.

This module provides a FastAPI implementation for any agent-based game
in the Haive framework, with support for:
    - REST endpoints for game state management
    - WebSocket connections for real-time updates
    - Supabase persistence for cloud storage
    - Row-Level Security (RLS) for data isolation
    - Multi-game support through factory patterns

The API supports any game that follows the standard Haive agent pattern,
allowing for easy integration of new games.
"""

import asyncio
import logging
import os

# Fix imports for local development
import sys
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, create_model

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if module_path not in sys.path:
    sys.path.append(module_path)

from .api.game_socket import GameSocketServer

# Now import the modules
from .engine.agent.agent import Agent
from .persistence.supabase_config import SupabaseCheckpointerConfig
from .schema.state_schema import StateSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("game-api")


class GameRequest(BaseModel):
    """Base request model for creating a new game."""

    thread_id: str | None = None
    persistence_type: str = "supabase"  # "postgres", "supabase", "memory"
    config_overrides: dict[str, Any] | None = None
    user_id: str | None = None  # For Supabase RLS


class GameResponseBase(BaseModel):
    """Base response model for game state."""

    thread_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    state: dict[str, Any]


class GameAPI:
    """Generic API for agent-based games with WebSocket support.

    This class provides a complete API implementation for any game
    that follows the Haive agent pattern, with both REST endpoints
    and WebSocket connections for real-time updates.

    Attributes:
        app (FastAPI): The FastAPI application
        agent_class (Type[Agent]): The agent class for the game
        state_schema (Type[StateSchema]): The state schema for the game
        socket_server (GameSocketServer): The WebSocket server
    """

    def __init__(
        self,
        app_name: str,
        agent_class: type[Agent],
        state_schema: type[StateSchema],
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        route_prefix: str = "/api/games",
        ws_route_prefix: str = "/ws/games",
    ):
        """Initialize the game API.

        Args:
            app_name: The name of the game/application
            agent_class: The agent class for the game
            state_schema: The state schema for the game
            response_model: Optional custom response model
            request_model: Optional custom request model
            route_prefix: The URL prefix for REST routes
            ws_route_prefix: The URL prefix for WebSocket routes
        """
        self.app_name = app_name
        self.agent_class = agent_class
        self.state_schema = state_schema
        self.route_prefix = route_prefix
        self.ws_route_prefix = ws_route_prefix

        # Use provided models or create defaults
        self.response_model = response_model or GameResponseBase
        self.request_model = request_model or GameRequest

        # Create FastAPI app
        self.app = FastAPI(
            title=f"{app_name} API",
            description=f"API for {app_name} game with WebSocket support",
            version="1.0.0",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Adjust for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Create WebSocket server
        self.socket_server = GameSocketServer(
            app=self.app,
            agent_class=self.agent_class,
            state_schema=self.state_schema,
            route_prefix=self.ws_route_prefix,
        )

        # Register REST routes
        self._register_routes()

    def _register_routes(self):
        """Register REST routes with the FastAPI application."""
        app = self.app

        @app.post(f"{self.route_prefix}/", response_model=self.response_model)
        async def create_game(request: GameRequest):
            """Create a new game instance."""
            try:
                # Generate thread ID if not provided
                thread_id = (
                    request.thread_id
                    or f"{self.app_name.lower()}_{uuid.uuid4().hex[:8]}"
                )

                # Prepare config overrides
                config_overrides = request.config_overrides or {}

                # Handle Supabase persistence if requested
                if request.persistence_type == "supabase":
                    # Create Supabase checkpointer config
                    supabase_config = SupabaseCheckpointerConfig(
                        user_id=request.user_id, setup_needed=True
                    )

                    # Add to config overrides
                    config_overrides["persistence"] = supabase_config

                # Add persistence type to config
                config_overrides["persistence_type"] = request.persistence_type

                # Get or create agent
                agent = self.socket_server.get_or_create_agent(
                    thread_id=thread_id, config_overrides=config_overrides
                )

                # Initialize game state
                if hasattr(self.state_schema, "initialize") and callable(
                    self.state_schema.initialize
                ):
                    # Use schema's initialize method if available
                    initial_state = self.state_schema.initialize().model_dump()
                else:
                    # Default empty state
                    initial_state = {}

                # Run agent to initialize
                state = agent.run(initial_state, thread_id=thread_id)

                # Return response
                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                }

            except Exception as e:
                logger.error(f"Error creating game: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail=f"Error creating game: {e!s}"
                )

        @app.post(
            f"{self.route_prefix}/{{thread_id}}/move",
            response_model=self.response_model,
        )
        async def make_move(thread_id: str, move_data: dict[str, Any]):
            """Make a move in a game."""
            try:
                # Get agent
                agent = self.socket_server.get_or_create_agent(thread_id)

                # Create move request (format depends on the specific game)
                move_request = {"move": move_data}

                # Make move
                state = agent.run(move_request, thread_id=thread_id)

                # Return response
                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                }

            except Exception as e:
                logger.error(f"Error making move: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error making move: {e!s}")

        @app.get(
            f"{self.route_prefix}/{{thread_id}}/ai-move",
            response_model=self.response_model,
        )
        async def make_ai_move(thread_id: str):
            """Let AI make a move."""
            try:
                # Get agent
                agent = self.socket_server.get_or_create_agent(thread_id)

                # AI makes a move (empty input triggers AI move)
                state = agent.run({}, thread_id=thread_id)

                # Return response
                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                }

            except Exception as e:
                logger.error(f"Error making AI move: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail=f"Error making AI move: {e!s}"
                )

        @app.get(
            f"{self.route_prefix}/{{thread_id}}", response_model=self.response_model
        )
        async def get_game(thread_id: str):
            """Get current game state."""
            try:
                # Get agent
                agent = self.socket_server.get_or_create_agent(thread_id)

                # Get current state
                state = agent.run({}, thread_id=thread_id)

                # Return response
                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                }

            except Exception as e:
                logger.error(f"Error getting game state: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail=f"Error getting game: {e!s}"
                )

        @app.post(f"{self.route_prefix}/{{thread_id}}/register-user")
        async def register_user(thread_id: str, user_data: dict[str, Any]):
            """Register user ID for Supabase RLS."""
            try:
                user_id = user_data.get("user_id")
                if not user_id:
                    raise HTTPException(status_code=400, detail="Missing user_id")

                # Get agent
                agent = self.socket_server.get_or_create_agent(thread_id)

                # If using Supabase, update the user_id
                if hasattr(agent, "config") and hasattr(agent.config, "persistence"):
                    persistence_config = agent.config.persistence

                    if (
                        hasattr(persistence_config, "type")
                        and persistence_config.type == "supabase"
                    ):
                        # Update user_id
                        persistence_config.user_id = user_id

                        # Register thread
                        persistence_config.register_thread(thread_id)

                        return {"status": "success", "message": "User registered"}
                    return {
                        "status": "warning",
                        "message": "Agent is not using Supabase persistence",
                    }

                return {
                    "status": "error",
                    "message": "Agent does not support user registration",
                }

            except Exception as e:
                logger.error(f"Error registering user: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail=f"Error registering user: {e!s}"
                )

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the API server."""
        import uvicorn

        # Fix for Windows asyncio issues
        if __name__ == "__main__":
            import platform

            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run server
        uvicorn.run(self.app, host=host, port=port)


class GameAPIFactory:
    """Factory for creating game-specific APIs.

    This class creates specialized API instances for different game types,
    with appropriate state schemas and agent classes for each game.

    Example:
        ```python
        # Create a chess API
        chess_api = GameAPIFactory.create_chess_api()

        # Run the server
        chess_api.run(port=8000)
        ```
    """

    @staticmethod
    def create_api(
        app_name: str,
        agent_class: type[Agent],
        state_schema: type[StateSchema],
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        route_prefix: str = "/api/games",
        ws_route_prefix: str = "/ws/games",
    ) -> GameAPI:
        """Create a game API for any agent and state schema.

        Args:
            app_name: The name of the game/application
            agent_class: The agent class for the game
            state_schema: The state schema for the game
            response_model: Optional custom response model
            request_model: Optional custom request model
            route_prefix: The URL prefix for REST routes
            ws_route_prefix: The URL prefix for WebSocket routes

        Returns:
            A configured GameAPI instance
        """
        return GameAPI(
            app_name=app_name,
            agent_class=agent_class,
            state_schema=state_schema,
            response_model=response_model,
            request_model=request_model,
            route_prefix=route_prefix,
            ws_route_prefix=ws_route_prefix,
        )

    @staticmethod
    def create_chess_api() -> GameAPI:
        """Create a chess-specific API.

        Returns:
            A configured GameAPI instance for chess
        """
        # Fix imports for packages directory structure
        import os
        import sys

        packages_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../..")
        )
        if packages_path not in sys.path:
            sys.path.append(packages_path)

        from haive.games.chess.agent import ChessAgent
        from haive.games.chess.state import ChessState

        # Create a custom response model for chess
        ChessResponse = create_model(
            "ChessResponse",
            thread_id=(str, ...),
            timestamp=(datetime, Field(default_factory=datetime.now)),
            state=(dict[str, Any], ...),
            board_fen=(str, None),
            current_player=(str, None),
            game_status=(str, None),
            game_result=(Optional[str], None),
            __base__=GameResponseBase,
        )

        return GameAPIFactory.create_api(
            app_name="Chess",
            agent_class=ChessAgent,
            state_schema=ChessState,
            response_model=ChessResponse,
            route_prefix="/api/chess",
            ws_route_prefix="/ws/chess",
        )

    @staticmethod
    def create_connect4_api() -> GameAPI:
        """Create a Connect4-specific API.

        Returns:
            A configured GameAPI instance for Connect4
        """
        from haive.games.connect4.agent import Connect4Agent
        from haive.games.connect4.state import Connect4State

        return GameAPIFactory.create_api(
            app_name="Connect4",
            agent_class=Connect4Agent,
            state_schema=Connect4State,
            route_prefix="/api/connect4",
            ws_route_prefix="/ws/connect4",
        )

    @staticmethod
    def create_tic_tac_toe_api() -> GameAPI:
        """Create a Tic Tac Toe-specific API.

        Returns:
            A configured GameAPI instance for Tic Tac Toe
        """
        from haive.games.tic_tac_toe.agent import TicTacToeAgent
        from haive.games.tic_tac_toe.state import TicTacToeState

        return GameAPIFactory.create_api(
            app_name="TicTacToe",
            agent_class=TicTacToeAgent,
            state_schema=TicTacToeState,
            route_prefix="/api/tictactoe",
            ws_route_prefix="/ws/tictactoe",
        )


# Example usage
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    # Create a combined API with multiple games
    app = FastAPI(title="Game API Hub")

    try:
        # Import chess components
        from haive.games.chess.agent import ChessAgent
        from haive.games.chess.state import ChessState

        # Create chess API routes
        chess_api = GameAPIFactory.create_api(
            app_name="Chess",
            agent_class=ChessAgent,
            state_schema=ChessState,
            route_prefix="/api/chess",
            ws_route_prefix="/ws/chess",
        )

        # Mount chess app routes to main app
        app.mount("/chess", chess_api.app)
        print("Chess API mounted successfully")
    except ImportError:
        print("Chess game not available")

    try:
        # Import Connect4 components
        from haive.games.connect4.agent import Connect4Agent
        from haive.games.connect4.state import Connect4State

        # Create Connect4 API routes
        connect4_api = GameAPIFactory.create_api(
            app_name="Connect4",
            agent_class=Connect4Agent,
            state_schema=Connect4State,
            route_prefix="/api/connect4",
            ws_route_prefix="/ws/connect4",
        )

        # Mount Connect4 app routes to main app
        app.mount("/connect4", connect4_api.app)
        print("Connect4 API mounted successfully")
    except ImportError:
        print("Connect4 game not available")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
