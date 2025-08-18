"""WebSocket server for game state streaming with Supabase integration.

This module provides a general-purpose WebSocket server that can stream game state
for any agent-based game in the Haive framework. It supports:
    - Real-time state updates
    - Supabase persistence integration with RLS
    - Player move submissions
    - AI move requests
    - Multiple game types
    - Authentication and user management

The WebSocket server can be integrated with any game agent implementation
that follows the standard Haive agent interface.
"""

import asyncio
import contextlib
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from haive.core.engine.agent.agent import Agent
from haive.core.schema.state_schema import StateSchema
from haive.games.connect4.agent import Connect4Agent
from haive.games.connect4.state import Connect4State
from haive.games.tic_tac_toe.agent import TicTacToeAgent
from haive.games.tic_tac_toe.state import TicTacToeState

# Fix imports for local development


module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if module_path not in sys.path:
    sys.path.append(module_path)

# Now import the modules


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("game-socket")


class GameSocketServer:
    """General-purpose WebSocket server for game state streaming.

    This class provides a WebSocket server that can be integrated with
    any game agent implementation to stream game state updates in real-time.
    It handles connection management, message routing, and state updates.

    Attributes:
        app (FastAPI): The FastAPI application to add routes to
        agent_class (Type[Agent]): The agent class for the game
        state_schema (Type[StateSchema]): The state schema for the game
        active_connections (Set[WebSocket]): Set of active WebSocket connections
        connection_thread_map (Dict[WebSocket, str]): Map of connections to thread IDs
        agents (Dict[str, Agent]): Map of thread IDs to agent instances
    """

    def __init__(
        self,
        app: FastAPI,
        agent_class: type[Agent],
        state_schema: type[StateSchema],
        route_prefix: str = "/ws/games",
    ):
        """Initialize the game socket server.

        Args:
            app: The FastAPI application to add routes to
            agent_class: The agent class for the game
            state_schema: The state schema for the game
            route_prefix: The URL prefix for WebSocket routes
        """
        self.app = app
        self.agent_class = agent_class
        self.state_schema = state_schema
        self.route_prefix = route_prefix
        self.active_connections: set[WebSocket] = set()
        self.connection_thread_map: dict[WebSocket, str] = {}
        self.agents: dict[str, Agent] = {}

        # Register WebSocket route
        self._register_routes()

    def _register_routes(self):
        """Register WebSocket routes with the FastAPI application."""

        @self.app.websocket(f"{self.route_prefix}/{{thread_id}}")
        async def game_websocket(websocket: WebSocket, thread_id: str):
            """WebSocket endpoint for game state streaming."""
            await websocket.accept()

            try:
                # Register connection
                self.register_connection(websocket, thread_id)

                # Get or create agent
                agent = self.get_or_create_agent(thread_id)

                # Send initial state
                state = agent.run({}, thread_id=thread_id)
                await websocket.send_json(
                    {
                        "type": "state_update",
                        "thread_id": thread_id,
                        "state": state,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Main WebSocket loop
                while True:
                    # Wait for messages
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    message_type = message.get("type", "")

                    # Process message based on type
                    if message_type == "make_move":
                        await self._handle_make_move(websocket, thread_id, message)

                    elif message_type == "ai_move":
                        await self._handle_ai_move(websocket, thread_id)

                    elif message_type == "get_state":
                        await self._handle_get_state(websocket, thread_id)

                    elif message_type == "register_user":
                        await self._handle_register_user(websocket, thread_id, message)

                    else:
                        # Custom message handling
                        await self._handle_custom_message(websocket, thread_id, message)

            except WebSocketDisconnect:
                # Handle disconnection
                self.unregister_connection(websocket)
                logger.info(f"Client disconnected from game {thread_id}")

            except Exception as e:
                # Handle other errors
                self.unregister_connection(websocket)
                logger.error(f"WebSocket error: {e}", exc_info=True)

                # Try to send error message
                with contextlib.suppress(BaseException):
                    await websocket.send_json(
                        {
                            "type": "error",
                            "thread_id": thread_id,
                            "message": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

    async def _handle_make_move(
        self, websocket: WebSocket, thread_id: str, message: dict[str, Any]
    ):
        """Handle a make_move message."""
        agent = self.get_or_create_agent(thread_id)
        move_data = message.get("move", {})

        # Format the move data based on the expected input format
        input_data = {"move": move_data}

        # Make the move
        state = agent.run(input_data, thread_id=thread_id)

        # Send updated state
        await websocket.send_json(
            {
                "type": "state_update",
                "thread_id": thread_id,
                "state": state,
                "timestamp": datetime.now().isoformat(),
                "last_action": "player_move",
                "move": move_data,
            }
        )

        # If auto-response is requested and game is ongoing, make AI move
        if message.get("auto_response", True) and self._is_game_ongoing(state):
            await asyncio.sleep(1)  # Small delay for better UX
            await self._handle_ai_move(websocket, thread_id)

    async def _handle_ai_move(self, websocket: WebSocket, thread_id: str):
        """Handle an ai_move message."""
        agent = self.get_or_create_agent(thread_id)

        # AI makes a move (empty input triggers AI move)
        state = agent.run({}, thread_id=thread_id)

        # Send updated state
        await websocket.send_json(
            {
                "type": "state_update",
                "thread_id": thread_id,
                "state": state,
                "timestamp": datetime.now().isoformat(),
                "last_action": "ai_move",
            }
        )

    async def _handle_get_state(self, websocket: WebSocket, thread_id: str):
        """Handle a get_state message."""
        agent = self.get_or_create_agent(thread_id)

        # Get current state
        state = agent.run({}, thread_id=thread_id)

        # Send state
        await websocket.send_json(
            {
                "type": "state_update",
                "thread_id": thread_id,
                "state": state,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _handle_register_user(
        self, websocket: WebSocket, thread_id: str, message: dict[str, Any]
    ):
        """Handle a register_user message for Supabase integration."""
        user_id = message.get("user_id")
        if not user_id:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Missing user_id in register_user message",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return

        agent = self.get_or_create_agent(thread_id)

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
                try:
                    persistence_config.register_thread(thread_id)
                    await websocket.send_json(
                        {
                            "type": "user_registered",
                            "thread_id": thread_id,
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Error registering thread: {e!s}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            else:
                await websocket.send_json(
                    {
                        "type": "warning",
                        "message": "Agent is not using Supabase persistence",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    async def _handle_custom_message(
        self, websocket: WebSocket, thread_id: str, message: dict[str, Any]
    ):
        """Handle custom message types specific to different games."""
        # Default implementation just echoes the message type
        await websocket.send_json(
            {
                "type": "info",
                "message": f"Received message of type: {message.get('type')}",
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _is_game_ongoing(self, state: dict[str, Any]) -> bool:
        """Check if the game is still ongoing based on state.

        This is a generic implementation that works with most game state
        schemas. Games with different state structures can override this
        method.
        """
        # Common game status fields
        if "game_status" in state:
            return state["game_status"] == "ongoing"

        if "status" in state:
            return state["status"] == "ongoing" or state["status"] == "in_progress"

        if "winner" in state:
            return state["winner"] is None

        # Default to True if we can't determine
        return True

    def register_connection(self, websocket: WebSocket, thread_id: str):
        """Register a WebSocket connection."""
        self.active_connections.add(websocket)
        self.connection_thread_map[websocket] = thread_id

    def unregister_connection(self, websocket: WebSocket):
        """Unregister a WebSocket connection."""
        self.active_connections.discard(websocket)
        if websocket in self.connection_thread_map:
            del self.connection_thread_map[websocket]

    def get_or_create_agent(
        self, thread_id: str, config_overrides: dict[str, Any] | None = None
    ) -> Agent:
        """Get or create an agent for a thread ID."""
        if thread_id in self.agents:
            return self.agents[thread_id]

        # Default config
        config_kwargs = {
            "name": f"agent_{thread_id[:8]}",
            "runnable_config": {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 100,
            },
        }

        # Apply any additional config overrides
        if config_overrides:
            for key, value in config_overrides.items():
                config_kwargs[key] = value

        # Create agent config and agent
        config_class = self.agent_class.get_config_class()
        config = config_class(**config_kwargs)
        agent = self.agent_class(config=config)

        # Cache agent
        self.agents[thread_id] = agent

        return agent

    async def broadcast_to_thread(self, thread_id: str, message: dict[str, Any]):
        """Broadcast a message to all connections for a thread."""
        for websocket, tid in self.connection_thread_map.items():
            if tid == thread_id:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.exception(f"Error broadcasting to {thread_id}: {e}")

    def cleanup(self, thread_id: str | None = None):
        """Clean up resources."""
        if thread_id:
            # Clean up specific thread
            if thread_id in self.agents:
                agent = self.agents[thread_id]
                if hasattr(agent, "checkpointer") and hasattr(
                    agent.checkpointer, "conn"
                ):
                    with contextlib.suppress(BaseException):
                        agent.checkpointer.conn.close()
                del self.agents[thread_id]
        else:
            # Clean up all
            for agent in self.agents.values():
                if hasattr(agent, "checkpointer") and hasattr(
                    agent.checkpointer, "conn"
                ):
                    with contextlib.suppress(BaseException):
                        agent.checkpointer.conn.close()
            self.agents = {}


class GameSocketFactory:
    """Factory for creating game-specific socket servers.

    This class creates specialized socket servers for different game types,
    with appropriate message handling and state management for each game.

    Examples:
                # Create a chess socket server
                chess_socket = GameSocketFactory.create_chess_socket(app)

                # Or create a custom socket server
                custom_socket = GameSocketFactory.create_socket(
                    app,
                    agent_class=ChessAgent,
                    state_schema=ChessState,
                    route_prefix="/ws/chess"
                )
    """

    @staticmethod
    def create_socket(
        app: FastAPI,
        agent_class: type[Agent],
        state_schema: type[StateSchema],
        route_prefix: str = "/ws/games",
    ) -> GameSocketServer:
        """Create a game socket server for any agent and state schema.

        Args:
            app: The FastAPI application
            agent_class: The agent class for the game
            state_schema: The state schema for the game
            route_prefix: The URL prefix for WebSocket routes

        Returns:
            A configured GameSocketServer instance
        """
        return GameSocketServer(
            app=app,
            agent_class=agent_class,
            state_schema=state_schema,
            route_prefix=route_prefix,
        )

    @staticmethod
    def create_chess_socket(app: FastAPI) -> GameSocketServer:
        """Create a chess-specific socket server.

        Args:
            app: The FastAPI application

        Returns:
            A configured GameSocketServer instance for chess
        """
        # Fix imports for packages directory structure

        packages_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../..")
        )
        if packages_path not in sys.path:
            sys.path.append(packages_path)

        from haive.games.chess.agent import ChessAgent
        from haive.games.chess.state import ChessState

        return GameSocketFactory.create_socket(
            app=app,
            agent_class=ChessAgent,
            state_schema=ChessState,
            route_prefix="/ws/chess",
        )

    @staticmethod
    def create_connect4_socket(app: FastAPI) -> GameSocketServer:
        """Create a Connect4-specific socket server.

        Args:
            app: The FastAPI application

        Returns:
            A configured GameSocketServer instance for Connect4
        """
        # Import here to avoid circular imports

        return GameSocketFactory.create_socket(
            app=app,
            agent_class=Connect4Agent,
            state_schema=Connect4State,
            route_prefix="/ws/connect4",
        )

    @staticmethod
    def create_tic_tac_toe_socket(app: FastAPI) -> GameSocketServer:
        """Create a Tic Tac Toe-specific socket server.

        Args:
            app: The FastAPI application

        Returns:
            A configured GameSocketServer instance for Tic Tac Toe
        """
        # Import here to avoid circular imports

        return GameSocketFactory.create_socket(
            app=app,
            agent_class=TicTacToeAgent,
            state_schema=TicTacToeState,
            route_prefix="/ws/tictactoe",
        )


# Example usage
if __name__ == "__main__":
    app = FastAPI()

    try:
        # Create chess socket server
        chess_socket = GameSocketFactory.create_chess_socket(app)
    except ImportError:
        pass

    try:
        # Create Connect4 socket server
        connect4_socket = GameSocketFactory.create_connect4_socket(app)
    except ImportError:
        pass

    try:
        # Create Tic Tac Toe socket server
        tictactoe_socket = GameSocketFactory.create_tic_tac_toe_socket(app)
    except ImportError:
        pass

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
