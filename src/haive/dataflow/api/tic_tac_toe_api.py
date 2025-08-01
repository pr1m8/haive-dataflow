import asyncio
import logging
import platform
import uuid
from datetime import datetime
from typing import Any, Literal

import uvicorn
from fastapi import HTTPException
from haive_games.tic_tac_toe.agent import TicTacToeAgent
from haive_games.tic_tac_toe.config import TicTacToeConfig
from haive_games.tic_tac_toe.state import TicTacToeState
from haive_games.tic_tac_toe.state_manager import TicTacToeStateManager
from pydantic import BaseModel, Field

from haive.dataflow.api.api.game_agent import AgentResponseBase, GenericAgentAPI

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tictactoe-api")


class TicTacToeMoveRequest(BaseModel):
    row: int = Field(..., description="Row index (0-2) for the move")
    col: int = Field(..., description="Column index (0-2) for the move")
    explanation: str | None = Field(
        None, description="Optional explanation for the move"
    )


class TicTacToeRequest(BaseModel):
    thread_id: str | None = None
    persistence_type: str = "postgres"
    config_overrides: dict[str, Any] | None = None
    first_player: Literal["X", "O"] = "X"
    enable_analysis: bool = True


class TicTacToeResponse(AgentResponseBase):
    board: list[list[str | None]]
    turn: str
    winner: str | None
    game_status: str
    move_history: list[dict[str, Any]]
    player1_analysis: list[dict[str, Any]] | None
    player2_analysis: list[dict[str, Any]] | None
    error_message: str | None


class TicTacToeAPI(GenericAgentAPI[TicTacToeAgent, TicTacToeConfig]):
    def __init__(self):
        super().__init__(
            app_name="TicTacToe",
            agent_class=TicTacToeAgent,
            config_class=TicTacToeConfig,
            state_schema=TicTacToeState,
            response_model=TicTacToeResponse,
            default_persistence="postgres",
        )
        self._register_tictactoe_routes()

    def _register_tictactoe_routes(self):
        app = self.app

        @app.post("/games/", response_model=TicTacToeResponse)
        async def create_game(request: TicTacToeRequest):
            """Create a new Tic Tac Toe game."""
            try:
                thread_id = request.thread_id or f"tictactoe_{uuid.uuid4().hex[:8]}"

                agent = self.agent_manager.get_or_create_agent(
                    thread_id=thread_id,
                    config_overrides={
                        "first_player": request.first_player,
                        "enable_analysis": request.enable_analysis,
                        **(request.config_overrides or {}),
                    },
                )

                initial_state = TicTacToeStateManager.initialize(
                    first_player=request.first_player,
                    player_X="player1",
                    player_O="player2",
                ).model_dump()

                state = agent.run(initial_state, thread_id=thread_id)

                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                    **state,
                }

            except Exception as e:
                logger.error(f"Error creating Tic Tac Toe game: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, detail=f"Error creating game: {e!s}"
                )

        @app.post("/games/{thread_id}/move", response_model=TicTacToeResponse)
        async def make_move(thread_id: str, move: TicTacToeMoveRequest):
            """Make a move in a Tic Tac Toe game."""
            try:
                agent = self.agent_manager.get_or_create_agent(thread_id)

                move_data = {
                    "move": {
                        "row": move.row,
                        "col": move.col,
                        "explanation": move.explanation,
                    }
                }

                state = agent.run(move_data, thread_id=thread_id)

                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                    **state,
                }

            except Exception as e:
                logger.error(f"Error making move: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error making move: {e!s}")

        @app.get("/games/{thread_id}/ai-move", response_model=TicTacToeResponse)
        async def ai_move(thread_id: str):
            """Let AI make a move."""
            try:
                agent = self.agent_manager.get_or_create_agent(thread_id)
                state = agent.run({}, thread_id=thread_id)

                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                    **state,
                }

            except Exception as e:
                logger.error(f"Error making AI move: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"AI move error: {e!s}")

        @app.get("/games/{thread_id}", response_model=TicTacToeResponse)
        async def get_game(thread_id: str):
            """Get current game state."""
            try:
                agent = self.agent_manager.get_or_create_agent(thread_id)
                state = agent.run({}, thread_id=thread_id)

                return {
                    "thread_id": thread_id,
                    "state": state,
                    "timestamp": datetime.now(),
                    **state,
                }

            except Exception as e:
                logger.error(f"Error fetching game state: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Get game error: {e!s}")


# =============================================
# Main Entry Point
# =============================================

tictactoe_api = TicTacToeAPI()


def run():
    """Run the Tic Tac Toe API server."""
    if __name__ == "__main__":
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(tictactoe_api.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
