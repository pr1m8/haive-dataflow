# Haive Games API

This README explains how to run the Haive Games API with WebSocket support.

## Running the Games API

The Games API can be run in several ways:

### 1. Standalone Games API

This is the simplest way to run just the games API without any dependencies on the main Haive API:

```bash
cd /home/will/Projects/haive/backend/haive/packages/haive-dataflow/src/haive/dataflow/api
python run_games_api.py
```

This will:

- Discover all available game agents
- Create WebSocket endpoints for each game
- Start a server on port 8005
- Provide a simple HTML client for testing

You can then access:

- Game list: http://localhost:8005/games
- Individual game clients: http://localhost:8005/games/{game_type} (e.g., http://localhost:8005/games/chess)

### 2. Simplified WebSocket Server

For testing a specific game (like chess) in isolation:

```bash
cd /home/will/Projects/haive/backend/haive/packages/haive-dataflow/src/haive/dataflow/api
python run_simple.py
```

### 3. Integrated with Main API (Advanced)

To run the games API integrated with the main Haive API:

```bash
cd /home/will/Projects/haive/backend/haive/packages/haive-dataflow/src/haive/dataflow/api
python run_integrated_api.py
```

This requires proper configuration of the main API and may not work without additional setup.

## Testing Game Connections

To test WebSocket connections to a game:

```bash
cd /home/will/Projects/haive/backend/haive/packages/haive-dataflow/src/haive/dataflow/api
python test_chess_connection.py
```

## WebSocket Protocol

Connect to WebSockets at:

- Standalone mode: `ws://localhost:8005/api/ws/{game_type}/{game_id}`
- Example: `ws://localhost:8005/api/ws/chess/chess_123`

Send messages like:

```json
{"type": "get_state"}
{"type": "ai_move"}
{"type": "make_move", "move": {...}}
```

## Troubleshooting

If games aren't discovered:

- Check log output for import errors
- Verify game module structure
- Try running in simple mode first

For WebSocket connection issues:

- Verify WebSocket URL format
- Check browser console for CORS issues
- Ensure game ID format is correct

## Documentation

For detailed documentation, see:

- GAME_API.md - Comprehensive documentation on the Games API
- README.md - Main API documentation
