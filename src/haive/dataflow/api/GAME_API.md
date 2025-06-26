# Haive Game API

This document describes the WebSocket-based API for streaming game agent states from the Haive Games package.

## Overview

The Game API provides:

1. Dynamic discovery of game agents from `haive-games`
2. WebSocket endpoints for real-time game state streaming
3. REST endpoints for game management
4. Integration with the main Haive API
5. Simple HTML/JS clients for testing

## Architecture

The implementation consists of several key components:

- `game_router.py`: Core implementation that discovers and loads game agents, creates routes, and handles WebSocket connections
- `integrate_games.py`: Module for integrating game routes with the main Haive API
- `run_simple.py`: Standalone runner for the game API without other Haive dependencies
- `run_integrated_api.py`: Runner for the integrated Haive API with game support
- Test scripts for verifying functionality

## Usage

### Running the Game API Standalone

To run the Game API as a standalone service:

```bash
cd /path/to/haive/packages/haive-dataflow/src/haive/dataflow/api
python run_simple.py
```

This will start a server on port 8005 with routes for all discovered game agents.

### Running the Integrated API

To run the full Haive API with game support:

```bash
cd /path/to/haive/packages/haive-dataflow/src/haive/dataflow/api
python run_integrated_api.py
```

This will start a server on port 8000 with all Haive API routes, including game routes.

### Testing WebSocket Connections

To test WebSocket connections to a game:

```bash
cd /path/to/haive/packages/haive-dataflow/src/haive/dataflow/api
python test_chess_connection.py
```

### Accessing Game Clients

When running the API, you can access game clients at:

- Standalone mode: `http://localhost:8005/`
- Integrated mode: `http://localhost:8000/api/games/`

## WebSocket Protocol

The WebSocket protocol for games uses JSON messages with the following structure:

### Client to Server

```json
{
  "type": "get_state"
}
```

```json
{
  "type": "make_move",
  "move": { ... game-specific move data ... }
}
```

```json
{
  "type": "ai_move"
}
```

### Server to Client

```json
{
  "type": "state_update",
  "game_type": "chess",
  "game_id": "chess_123",
  "state": { ... game state ... },
  "last_action": "player_move"
}
```

```json
{
  "type": "error",
  "message": "Error message"
}
```

## Supported Games

The API dynamically discovers game agents from the `haive-games` package. Any game with:

1. An agent class (name ending with "Agent")
2. A run method on the agent
3. A state schema (optional)

will be automatically discovered and exposed through the API.

## Integration with Main API

The Game API is designed to be integrated with the main Haive API. When integrated:

1. Game routes are mounted under `/api/games/`
2. Authentication and middleware from the main API are applied to game routes
3. Supabase persistence can be used for saving game states

To enable this integration, the `app.py` module includes code to dynamically discover and add game routes to the FastAPI application.

## Future Enhancements

- Supabase integration for cloud persistence
- Improved game-specific UI components
- Authentication and user management
- Custom game configuration options

## Troubleshooting

If games are not discovered:

1. Check the log output for import errors
2. Verify that the game modules have the expected structure
3. Try running in standalone mode first before integration
4. Check for any missing dependencies

If WebSocket connections fail:

1. Verify the WebSocket URL format
2. Check for CORS issues in browser console
3. Verify the game ID format
4. Check server logs for detailed error information
