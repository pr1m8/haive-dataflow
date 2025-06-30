#!/usr/bin/env python
"""Simple WebSocket server for streaming chess game state."""

import logging

import chess
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chess-ws")

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active connections and games
active_connections: set[WebSocket] = set()
active_games: dict[str, dict] = {}

# HTML CLIENT
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chess WebSocket Client</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .chessboard {
                width: 400px;
                height: 400px;
                border: 1px solid #000;
                display: grid;
                grid-template-columns: repeat(8, 1fr);
                grid-template-rows: repeat(8, 1fr);
            }
            .square {
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 30px;
            }
            .white {
                background-color: #f0d9b5;
            }
            .black {
                background-color: #b58863;
            }
            .log {
                height: 200px;
                overflow-y: auto;
                border: 1px solid #ccc;
                padding: 10px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Chess WebSocket Client</h1>
        
        <div>
            <label for="gameId">Game ID:</label>
            <input type="text" id="gameId" value="test123">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        
        <div style="display: flex; margin-top: 20px;">
            <div>
                <div class="chessboard" id="board"></div>
                <div style="margin-top: 10px;">
                    <button onclick="getState()">Get State</button>
                    <button onclick="aiMove()">AI Move</button>
                </div>
            </div>
            
            <div style="margin-left: 20px; flex: 1;">
                <h3>Game Info</h3>
                <div id="gameInfo">
                    <p>Status: <span id="status">Disconnected</span></p>
                    <p>Turn: <span id="turn">-</span></p>
                    <p>Game Status: <span id="gameStatus">-</span></p>
                </div>
                
                <h3>Log</h3>
                <div class="log" id="log"></div>
            </div>
        </div>
        
        <script>
            // Game data
            let ws = null;
            let gameState = null;
            let boardElement = document.getElementById('board');
            let statusElement = document.getElementById('status');
            let turnElement = document.getElementById('turn');
            let gameStatusElement = document.getElementById('gameStatus');
            let logElement = document.getElementById('log');
            
            // Chess pieces mapping
            const pieceMap = {
                'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  // White pieces
                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   // Black pieces
            };
            
            // Initialize the board
            function initBoard() {
                boardElement.innerHTML = '';
                for (let row = 0; row < 8; row++) {
                    for (let col = 0; col < 8; col++) {
                        const square = document.createElement('div');
                        square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
                        square.dataset.row = 7 - row;  // Flip for chess notation
                        square.dataset.col = col;
                        boardElement.appendChild(square);
                    }
                }
            }
            
            // Update board from FEN
            function updateBoard(fen) {
                if (!fen) return;
                
                const boardFen = fen.split(' ')[0];
                const rows = boardFen.split('/');
                
                for (let rowIndex = 0; rowIndex < 8; rowIndex++) {
                    let colIndex = 0;
                    const row = rows[rowIndex];
                    
                    for (let i = 0; i < row.length; i++) {
                        const char = row[i];
                        
                        if (isNaN(char)) {
                            // It's a piece
                            const square = document.querySelector(`.square[data-row="${rowIndex}"][data-col="${colIndex}"]`);
                            if (square) {
                                square.textContent = pieceMap[char] || char;
                            }
                            colIndex++;
                        } else {
                            // It's a number of empty squares
                            colIndex += parseInt(char);
                        }
                    }
                }
            }
            
            // Add to log
            function log(message) {
                const entry = document.createElement('div');
                entry.textContent = message;
                logElement.appendChild(entry);
                logElement.scrollTop = logElement.scrollHeight;
            }
            
            // Connect WebSocket
            function connect() {
                const gameId = document.getElementById('gameId').value || 'test123';
                const wsUrl = `ws://${window.location.host}/ws/chess/${gameId}`;
                
                if (ws) {
                    ws.close();
                }
                
                log(`Connecting to ${wsUrl}...`);
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    statusElement.textContent = 'Connected';
                    log('Connection established');
                    getState();
                };
                
                ws.onmessage = function(event) {
                    log(`Received: ${event.data}`);
                    
                    try {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'state_update') {
                            gameState = data.state;
                            updateBoard(gameState.board_fen);
                            turnElement.textContent = gameState.current_player || '-';
                            gameStatusElement.textContent = gameState.game_status || '-';
                        } else if (data.type === 'error') {
                            log(`Error: ${data.message}`);
                        }
                    } catch (e) {
                        log(`Error parsing message: ${e.message}`);
                    }
                };
                
                ws.onclose = function(event) {
                    statusElement.textContent = 'Disconnected';
                    log('Connection closed');
                };
                
                ws.onerror = function(event) {
                    statusElement.textContent = 'Error';
                    log('WebSocket error');
                };
            }
            
            // Disconnect WebSocket
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            // Get game state
            function getState() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'get_state'
                    };
                    ws.send(JSON.stringify(message));
                    log(`Sent: ${JSON.stringify(message)}`);
                } else {
                    log('WebSocket not connected');
                }
            }
            
            // Request AI move
            function aiMove() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'ai_move'
                    };
                    ws.send(JSON.stringify(message));
                    log(`Sent: ${JSON.stringify(message)}`);
                } else {
                    log('WebSocket not connected');
                }
            }
            
            // Initialize
            initBoard();
        </script>
    </body>
</html>
"""


# Helper functions for chess game
def get_empty_board():
    """Create a new chess board in starting position."""
    return chess.Board()


def make_random_move(board):
    """Make a random legal move."""
    legal_moves = list(board.legal_moves)
    if legal_moves:
        move = legal_moves[0]
        board.push(move)
        return move.uci()
    return None


def get_game_state(game_id):
    """Get the current game state."""
    if game_id not in active_games:
        board = get_empty_board()
        active_games[game_id] = {"board": board, "move_history": []}

    game = active_games[game_id]
    board = game["board"]

    return {
        "board_fen": board.fen(),
        "current_player": "white" if board.turn else "black",
        "game_status": (
            "checkmate"
            if board.is_checkmate()
            else (
                "stalemate"
                if board.is_stalemate()
                else (
                    "check"
                    if board.is_check()
                    else "draw" if board.is_insufficient_material() else "ongoing"
                )
            )
        ),
        "move_history": game["move_history"],
    }


# FastAPI routes
@app.get("/", response_class=HTMLResponse)
async def get_html():
    """Serve the HTML client."""
    return html


@app.websocket("/ws/chess/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for chess games."""
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for game: {game_id}")

    # Register connection
    active_connections.add(websocket)

    try:
        # Send initial state
        state = get_game_state(game_id)
        await websocket.send_json(
            {"type": "state_update", "game_id": game_id, "state": state}
        )

        # Main WebSocket loop
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type", "")
            logger.info(f"Received message: {data}")

            # Handle message
            if message_type == "get_state":
                # Get current state
                state = get_game_state(game_id)
                await websocket.send_json(
                    {"type": "state_update", "game_id": game_id, "state": state}
                )

            elif message_type == "ai_move":
                # Make AI move
                game = active_games.get(game_id)
                if game and game["board"].turn:  # Only if it's AI's turn
                    move = make_random_move(game["board"])
                    if move:
                        game["move_history"].append(move)

                        # Send updated state
                        state = get_game_state(game_id)
                        await websocket.send_json(
                            {
                                "type": "state_update",
                                "game_id": game_id,
                                "state": state,
                                "last_move": move,
                            }
                        )

    except WebSocketDisconnect:
        # Handle disconnection
        logger.info(f"WebSocket disconnected for game: {game_id}")
        active_connections.discard(websocket)

    except Exception as e:
        # Handle other errors
        logger.error(f"WebSocket error: {e}", exc_info=True)
        active_connections.discard(websocket)


def main():
    """Run the WebSocket server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
