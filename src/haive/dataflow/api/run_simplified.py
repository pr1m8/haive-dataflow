#!/usr/bin/env python3
"""Simplified demo to launch a WebSocket server for chess games.

This is a minimal implementation that focuses on getting the WebSocket
functionality working without the full API infrastructure.
"""

import logging
import os
import traceback

import chess
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chess-ws-demo")

# Create FastAPI app
app = FastAPI(title="Chess WebSocket Demo")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state storage
active_games: dict[str, dict] = {}
active_connections: set[WebSocket] = set()
connection_game_map: dict[WebSocket, str] = {}


# Chess helpers
def get_empty_board():
    """Create an empty chess board in starting position."""
    return chess.Board()


def move_is_valid(board, move_uci):
    """Check if a move is valid."""
    try:
        move = chess.Move.from_uci(move_uci)
        return move in board.legal_moves
    except ValueError:
        return False


def make_move(board, move_uci):
    """Make a move on the board."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            return True, "Move successful"
        return False, "Illegal move"
    except ValueError:
        return False, "Invalid move format"


def get_game_status(board):
    """Get the current game status."""
    if board.is_checkmate():
        return "checkmate"
    if board.is_stalemate():
        return "stalemate"
    if board.is_check():
        return "check"
    if board.is_insufficient_material():
        return "draw"
    return "ongoing"


def get_current_player(board):
    """Get the current player."""
    return "white" if board.turn == chess.WHITE else "black"


def get_game_state(game_id):
    """Get the full game state."""
    if game_id not in active_games:
        board = get_empty_board()
        active_games[game_id] = {
            "board": board,
            "move_history": [],
            "captured_pieces": {"white": [], "black": []},
        }

    game = active_games[game_id]
    board = game["board"]

    return {
        "board_fen": board.fen(),
        "current_player": get_current_player(board),
        "game_status": get_game_status(board),
        "move_history": game["move_history"],
        "captured_pieces": game["captured_pieces"],
        "winner": (
            "white"
            if board.is_checkmate() and not board.turn
            else "black" if board.is_checkmate() and board.turn else None
        ),
    }


# WebSocket endpoint
@app.websocket("/ws/chess/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for chess games."""
    # Print all request headers for debugging
    logger.info(f"WebSocket connection request received for game: {game_id}")
    logger.info(f"Headers: {websocket.headers}")
    logger.info(f"Query params: {websocket.query_params}")
    logger.info(f"Path params: {websocket.path_params}")

    try:
        logger.info("Attempting to accept WebSocket connection...")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for game: {game_id}")

        # Register connection
        active_connections.add(websocket)
        connection_game_map[websocket] = game_id
        logger.info(
            f"Connection registered for game: {game_id}, total connections: {len(active_connections)}"
        )

        # Initialize game if needed
        if game_id not in active_games:
            active_games[game_id] = {
                "board": get_empty_board(),
                "move_history": [],
                "captured_pieces": {"white": [], "black": []},
            }

        # Send initial state
        state = get_game_state(game_id)
        await websocket.send_json(
            {"type": "state_update", "game_id": game_id, "state": state}
        )

        # Main WebSocket loop
        while True:
            logger.info(f"Waiting for message from client for game: {game_id}")
            try:
                data = await websocket.receive_json()
                logger.info(f"Received message: {data}")
                message_type = data.get("type", "")
                logger.info(f"Processing message type: {message_type}")
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                raise

            if message_type == "make_move":
                move_data = data.get("move", {})
                move_uci = move_data.get("move")

                if move_uci:
                    board = active_games[game_id]["board"]
                    success, message = make_move(board, move_uci)

                    if success:
                        # Update move history
                        player = (
                            "white" if not board.turn else "black"
                        )  # Player who just moved
                        active_games[game_id]["move_history"].append((player, move_uci))

                        # Send updated state
                        state = get_game_state(game_id)
                        await websocket.send_json(
                            {
                                "type": "state_update",
                                "game_id": game_id,
                                "state": state,
                                "last_action": "player_move",
                                "move": move_data,
                            }
                        )

                        # Make AI move if requested
                        if (
                            data.get("auto_response", True)
                            and state["game_status"] == "ongoing"
                        ):
                            await make_ai_move(websocket, game_id)
                    else:
                        await websocket.send_json({"type": "error", "message": message})

            elif message_type == "ai_move":
                await make_ai_move(websocket, game_id)

            elif message_type == "get_state":
                state = get_game_state(game_id)
                await websocket.send_json(
                    {"type": "state_update", "game_id": game_id, "state": state}
                )

    except WebSocketDisconnect as e:
        # Handle disconnection
        disconnect_code = getattr(e, "code", "unknown")
        logger.info(
            f"WebSocket disconnected for game: {game_id}, code: {disconnect_code}"
        )
        active_connections.discard(websocket)
        connection_game_map.pop(websocket, None)
        logger.info(
            f"Connection unregistered, remaining connections: {len(active_connections)}"
        )

    except Exception as e:
        error_msg = f"WebSocket error for game {game_id}: {e!s}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())  # Full traceback
        try:
            await websocket.send_json(
                {"type": "error", "message": f"Server error: {e!s}"}
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message to client: {send_error!s}")

        active_connections.discard(websocket)
        connection_game_map.pop(websocket, None)
        logger.info(
            f"Connection terminated due to error, remaining connections: {len(active_connections)}"
        )


async def make_ai_move(websocket: WebSocket, game_id: str):
    """Make a simple AI move."""
    if game_id not in active_games:
        return

    board = active_games[game_id]["board"]

    # Very simple AI: just make the first legal move
    legal_moves = list(board.legal_moves)
    if legal_moves:
        # Choose the first legal move
        move = legal_moves[0]
        move_uci = move.uci()

        # Make the move
        board.push(move)

        # Update move history
        player = "white" if not board.turn else "black"  # Player who just moved
        active_games[game_id]["move_history"].append((player, move_uci))

        # Send updated state
        state = get_game_state(game_id)
        await websocket.send_json(
            {
                "type": "state_update",
                "game_id": game_id,
                "state": state,
                "last_action": "ai_move",
                "move": {"move": move_uci},
            }
        )


# Serve HTML client
from fastapi.responses import HTMLResponse


@app.get("/", response_class=HTMLResponse)
async def get_client():
    """Serve the chess client HTML."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple WebSocket Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        #log {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-top: 10px;
        }
        
        .entry {
            margin-bottom: 5px;
        }
        
        .error {
            color: red;
        }
        
        .sent {
            color: blue;
        }
        
        .received {
            color: green;
        }
    </style>
</head>
<body>
    <h1>Simple WebSocket Test</h1>
    
    <div>
        <label for="wsUrl">WebSocket URL:</label>
        <input type="text" id="wsUrl" value="ws://localhost:8003/ws/chess/test123" style="width: 300px;">
        <button id="connectBtn">Connect</button>
        <button id="disconnectBtn" disabled>Disconnect</button>
    </div>
    
    <div style="margin-top: 10px;">
        <button id="getStateBtn" disabled>Get State</button>
        <button id="aiMoveBtn" disabled>AI Move</button>
    </div>
    
    <h3>WebSocket Log</h3>
    <div id="log"></div>
    
    <script>
        // DOM elements
        const wsUrlInput = document.getElementById('wsUrl');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        const getStateBtn = document.getElementById('getStateBtn');
        const aiMoveBtn = document.getElementById('aiMoveBtn');
        const logContainer = document.getElementById('log');
        
        // WebSocket connection
        let socket = null;
        
        // Log a message
        function log(message, type = 'info') {
            const entry = document.createElement('div');
            entry.className = `entry ${type}`;
            entry.textContent = message;
            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Connect to WebSocket
        function connect() {
            const url = wsUrlInput.value;
            
            if (socket) {
                socket.close();
                socket = null;
            }
            
            log(`Connecting to ${url}...`);
            
            try {
                socket = new WebSocket(url);
                
                socket.addEventListener('open', (event) => {
                    log('Connection established', 'received');
                    connectBtn.disabled = true;
                    disconnectBtn.disabled = false;
                    getStateBtn.disabled = false;
                    aiMoveBtn.disabled = false;
                });
                
                socket.addEventListener('message', (event) => {
                    log(`Received: ${event.data}`, 'received');
                    try {
                        const data = JSON.parse(event.data);
                        console.log('Parsed message:', data);
                    } catch (e) {
                        console.error('Error parsing message:', e);
                    }
                });
                
                socket.addEventListener('close', (event) => {
                    log('Connection closed', 'error');
                    connectBtn.disabled = false;
                    disconnectBtn.disabled = true;
                    getStateBtn.disabled = true;
                    aiMoveBtn.disabled = true;
                });
                
                socket.addEventListener('error', (event) => {
                    log('WebSocket error', 'error');
                    console.error('WebSocket error:', event);
                });
            } catch (e) {
                log(`Error creating WebSocket: ${e.message}`, 'error');
                console.error('Error creating WebSocket:', e);
            }
        }
        
        // Disconnect from WebSocket
        function disconnect() {
            if (socket) {
                log('Disconnecting...', 'sent');
                socket.close();
                socket = null;
            }
        }
        
        // Send a message to get state
        function getState() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const message = {
                    type: 'get_state'
                };
                socket.send(JSON.stringify(message));
                log(`Sent: ${JSON.stringify(message)}`, 'sent');
            } else {
                log('WebSocket not connected', 'error');
            }
        }
        
        // Send a message to request AI move
        function requestAiMove() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const message = {
                    type: 'ai_move'
                };
                socket.send(JSON.stringify(message));
                log(`Sent: ${JSON.stringify(message)}`, 'sent');
            } else {
                log('WebSocket not connected', 'error');
            }
        }
        
        // Event listeners
        connectBtn.addEventListener('click', connect);
        disconnectBtn.addEventListener('click', disconnect);
        getStateBtn.addEventListener('click', getState);
        aiMoveBtn.addEventListener('click', requestAiMove);
    </script>
</body>
</html>
    """


# Mount static files
try:
    # Get absolute path to the static directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "static")

    # Create the directory if it doesn't exist
    os.makedirs(static_dir, exist_ok=True)

    # Mount the static directory
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
except Exception as e:
    logger.warning(f"Failed to mount static files: {e}")


# Main function
def main():
    """Run the WebSocket server."""
    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    main()
