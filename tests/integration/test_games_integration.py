"""Integration tests for the games API system.

These tests verify the full integration between haive-dataflow
and haive-games, including actual game discovery and API functionality.
"""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add games path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent.parent.parent / "haive-games" / "src")
)

# Try to import games - mark tests as skipped if not available
try:
    from haive.games.api import create_general_game_api

    from haive.dataflow.api.routers.games import (
        create_games_router,
        create_games_websocket_router,
    )

    GAMES_AVAILABLE = True
except ImportError:
    GAMES_AVAILABLE = False

# Skip all tests if games not available
pytestmark = pytest.mark.skipif(not GAMES_AVAILABLE, reason="haive-games not available")


class TestGamesIntegration:
    """Test full integration with haive-games."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create FastAPI app with games router."""
        app = FastAPI(title="Test Games Integration")

        # Add games router
        games_router = create_games_router(exclude_games=["go", "among_us", "monopoly"])
        app.include_router(games_router)

        # Add WebSocket router
        ws_router = create_games_websocket_router()
        app.include_router(ws_router)

        return app

    def test_discover_real_games(self, app: FastAPI):
        """Test that real games are discovered."""
        client = TestClient(app)

        response = client.get("/games/meta")
        assert response.status_code == 200

        meta = response.json()
        assert meta["total_games"] >= 3  # At least chess, connect4, tic_tac_toe

        games = meta["games"]
        assert "chess" in games
        assert "connect4" in games
        assert "tic_tac_toe" in games

        # Excluded games should not be present
        assert "go" not in games
        assert "among_us" not in games

    def test_list_games_with_details(self, app: FastAPI):
        """Test listing games with full details."""
        # Create a direct game API to test
        games_app, game_api = create_general_game_api(exclude_games=["go", "among_us"])

        client = TestClient(games_app)
        response = client.get("/api/games/")

        assert response.status_code == 200
        games = response.json()

        # Find chess
        chess = next((g for g in games if g["game_id"] == "chess"), None)
        assert chess is not None
        assert chess["name"] in ["Chess", "ChessGame", "Chess Game"]
        assert len(chess["players"]) >= 2
        assert "api_endpoints" in chess
        assert chess["api_endpoints"]["create"] == "/api/games/chess/create"

    def test_create_chess_game(self, app: FastAPI):
        """Test creating a chess game."""
        # Use direct API for this test
        games_app, game_api = create_general_game_api(exclude_games=["go", "among_us"])

        client = TestClient(games_app)

        # Create chess game
        response = client.post(
            "/api/games/create",
            json={
                "game_id": "chess",
                "config_mode": "simple",
                "player_models": {
                    "player1": "gpt-3.5-turbo",
                    "player2": "gpt-3.5-turbo",
                },
                "game_settings": {"max_moves": 10, "enable_analysis": False},
            },
        )

        assert response.status_code == 200
        result = response.json()

        assert result["game_id"] == "chess"
        assert "thread_id" in result
        assert result["config"]["max_moves"] == 10
        assert (
            result["endpoints"]["move"]
            == f"/api/games/chess/{result['thread_id']}/move"
        )

    def test_create_game_with_example_config(self, app: FastAPI):
        """Test creating a game with example configuration."""
        games_app, game_api = create_general_game_api(exclude_games=["go", "among_us"])

        client = TestClient(games_app)

        # First, check what example configs are available for tic-tac-toe
        games_list = client.get("/api/games/").json()
        ttt = next((g for g in games_list if g["game_id"] == "tic_tac_toe"), None)

        if ttt and ttt.get("example_configs"):
            # Use first available example
            example_name = ttt["example_configs"][0]

            response = client.post(
                "/api/games/create",
                json={
                    "game_id": "tic_tac_toe",
                    "config_mode": "example",
                    "example_config": example_name,
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert result["game_id"] == "tic_tac_toe"

    def test_invalid_game_creation(self, app: FastAPI):
        """Test error handling for invalid game creation."""
        games_app, game_api = create_general_game_api(exclude_games=["go", "among_us"])

        client = TestClient(games_app)

        # Non-existent game
        response = client.post(
            "/api/games/create",
            json={"game_id": "nonexistent_game", "config_mode": "simple"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Missing required config
        response = client.post(
            "/api/games/create",
            json={
                "game_id": "chess",
                "config_mode": "example",
                # Missing example_config
            },
        )

        assert response.status_code == 400
        assert "example_config required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_websocket_connection(self, app: FastAPI):
        """Test WebSocket connection to a game."""
        # This is a basic test - full WebSocket testing would require
        # actual game agent instantiation
        client = TestClient(app)

        with client.websocket_connect("/ws/games/chess/test-thread-123") as websocket:
            data = websocket.receive_json()

            # Should get connection confirmation or error
            assert "type" in data
            assert data["type"] in ["connected", "error"]

            if data["type"] == "connected":
                assert data["game_id"] == "chess"
                assert data["thread_id"] == "test-thread-123"


class TestGameSpecificAPIs:
    """Test game-specific API functionality."""

    @pytest.fixture
    def games_api(self):
        """Create games API instance."""
        app, api = create_general_game_api(exclude_games=["go", "among_us", "monopoly"])
        return app, api

    def test_chess_api_endpoints(self, games_api):
        """Test chess-specific endpoints."""
        app, api = games_api
        TestClient(app)

        # Verify chess is available
        assert "chess" in api.discovered_games

        # Check that chess routes exist
        routes = [r.path for r in app.routes]
        assert any("/api/games/chess/" in r for r in routes)

    def test_multiple_game_types(self, games_api):
        """Test creating different types of games."""
        app, api = games_api
        client = TestClient(app)

        game_configs = [
            {
                "game_id": "chess",
                "config_mode": "simple",
                "player_models": {
                    "player1": "gpt-3.5-turbo",
                    "player2": "gpt-3.5-turbo",
                },
            },
            {
                "game_id": "connect4",
                "config_mode": "simple",
                "player_models": {
                    "player1": "gpt-3.5-turbo",
                    "player2": "gpt-3.5-turbo",
                },
            },
            {
                "game_id": "tic_tac_toe",
                "config_mode": "simple",
                "player_models": {
                    "player1": "gpt-3.5-turbo",
                    "player2": "gpt-3.5-turbo",
                },
            },
        ]

        created_games = []

        for config in game_configs:
            response = client.post("/api/games/create", json=config)

            if response.status_code == 200:
                result = response.json()
                created_games.append(result)
                assert result["game_id"] == config["game_id"]
                assert "thread_id" in result

        # Should create at least 2 games successfully
        assert len(created_games) >= 2


class TestConfigurationModes:
    """Test different configuration modes in integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app, _ = create_general_game_api(exclude_games=["go", "among_us"])
        return TestClient(app)

    def test_simple_mode_with_canonical_names(self, client: TestClient):
        """Test simple mode with canonical model names."""
        response = client.post(
            "/api/games/create",
            json={
                "game_id": "chess",
                "config_mode": "simple",
                "player_models": {
                    "player1": "openai:gpt-3.5-turbo",
                    "player2": "openai:gpt-3.5-turbo",
                },
            },
        )

        # Should handle canonical names
        assert response.status_code == 200

    def test_advanced_mode_with_player_configs(self, client: TestClient):
        """Test advanced mode with full player configurations."""
        response = client.post(
            "/api/games/create",
            json={
                "game_id": "tic_tac_toe",
                "config_mode": "advanced",
                "player_configs": {
                    "X_player": {
                        "llm_config": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "player_name": "Strategic X",
                    },
                    "O_player": {
                        "llm_config": "gpt-3.5-turbo",
                        "temperature": 0.3,
                        "player_name": "Defensive O",
                    },
                },
            },
        )

        # Note: This might fail if tic_tac_toe doesn't support advanced mode
        # but we're testing the API accepts the request
        assert response.status_code in [200, 400]


class TestOpenAPIDocumentation:
    """Test OpenAPI documentation generation."""

    def test_openapi_schema(self):
        """Test that OpenAPI schema is generated correctly."""
        app, _ = create_general_game_api()
        client = TestClient(app)

        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "Haive Games API" in schema["info"]["title"]
        assert "/api/games/" in schema["paths"]
        assert "/api/games/create" in schema["paths"]

        # Check for game selection request schema
        create_path = schema["paths"]["/api/games/create"]
        assert "post" in create_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
