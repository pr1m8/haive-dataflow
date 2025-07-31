"""Tests for the games router."""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from haive.dataflow.api.routers.games import (
    create_games_router,
    create_games_websocket_router,
    get_game_api,
)


class TestGamesRouter:
    """Test the games router functionality."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create a test FastAPI app."""
        return FastAPI()

    @pytest.fixture
    def mock_games_available(self):
        """Mock the GAMES_AVAILABLE flag."""
        with patch("haive.dataflow.api.routers.games.GAMES_AVAILABLE", True):
            yield

    @pytest.fixture
    def mock_games_not_available(self):
        """Mock games not being available."""
        with patch("haive.dataflow.api.routers.games.GAMES_AVAILABLE", False):
            yield

    def test_create_router_games_not_available(
        self, app: FastAPI, mock_games_not_available
    ):
        """Test router creation when games are not available."""
        router = create_games_router()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/games/")

        assert response.status_code == 501
        assert "Games module not available" in response.json()["error"]

    def test_create_router_with_games(self, app: FastAPI, mock_games_available):
        """Test router creation with games available."""
        # Mock the game API creation
        mock_game_api = Mock()
        mock_game_api.discovered_games = {
            "chess": {"name": "Chess"},
            "connect4": {"name": "Connect 4"},
        }
        mock_game_api.exclude_games = []

        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api"
        ) as mock_create:
            mock_create.return_value = (Mock(), mock_game_api)

            router = create_games_router()
            app.include_router(router)

            # Test metadata endpoint
            client = TestClient(app)
            response = client.get("/games/meta")

            assert response.status_code == 200
            meta = response.json()
            assert meta["total_games"] == 2
            assert "chess" in meta["games"]
            assert "connect4" in meta["games"]

    def test_router_with_prefix_and_tags(self, app: FastAPI, mock_games_available):
        """Test router creation with custom prefix and tags."""
        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api"
        ) as mock_create:
            mock_create.return_value = (
                Mock(),
                Mock(discovered_games={}, exclude_games=[]),
            )

            router = create_games_router(prefix="/api/v1/games", tags=["games", "ai"])

            assert router.prefix == "/api/v1/games"
            assert router.tags == ["games", "ai"]

    def test_exclude_games(self, app: FastAPI, mock_games_available):
        """Test excluding specific games."""
        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api"
        ) as mock_create:
            create_games_router(exclude_games=["monopoly", "go"])

            # Verify create_general_game_api was called with exclude_games
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["exclude_games"] == ["monopoly", "go"]


class TestGamesWebSocketRouter:
    """Test WebSocket router functionality."""

    def test_create_websocket_router_no_games(self, mock_games_not_available):
        """Test WebSocket router when games not available."""
        router = create_games_websocket_router()

        # Should return empty router
        assert len(router.routes) == 0

    def test_create_websocket_router_with_games(self, mock_games_available):
        """Test WebSocket router with games available."""
        router = create_games_websocket_router()

        # Should have WebSocket route
        assert len(router.routes) > 0
        assert any(route.path == "/{game_id}/{thread_id}" for route in router.routes)

    @pytest.mark.asyncio
    async def test_websocket_connection(self, mock_games_available):
        """Test WebSocket connection handling."""
        app = FastAPI()

        # Mock game API
        mock_game_api = Mock()
        mock_game_api.discovered_games = {"chess": {"name": "Chess"}}

        with patch(
            "haive.dataflow.api.routers.games.get_game_api", return_value=mock_game_api
        ):
            router = create_games_websocket_router()
            app.include_router(router)

            client = TestClient(app)

            # Test valid game
            with client.websocket_connect("/ws/games/chess/test-123") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "connected"
                assert data["game_id"] == "chess"
                assert data["thread_id"] == "test-123"

            # Test invalid game
            with client.websocket_connect("/ws/games/invalid/test-123") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "error"
                assert "not found" in data["message"]


class TestGameAPIIntegration:
    """Test integration with the general game API."""

    def test_get_game_api_singleton(self, mock_games_available):
        """Test that get_game_api returns a singleton."""
        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api"
        ) as mock_create:
            mock_api = Mock()
            mock_create.return_value = (Mock(), mock_api)

            # First call creates instance
            api1 = get_game_api()
            assert api1 == mock_api

            # Second call returns same instance
            api2 = get_game_api()
            assert api2 == api1

            # Should only create once
            mock_create.assert_called_once()

    def test_router_error_handling(self, app: FastAPI, mock_games_available):
        """Test router error handling."""
        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api",
            side_effect=Exception("Test error"),
        ):
            router = create_games_router()
            app.include_router(router)

            client = TestClient(app)
            response = client.get("/games/")

            assert response.status_code == 500
            assert "Failed to initialize games" in response.json()["error"]


class TestRouterEndpoints:
    """Test individual router endpoints."""

    @pytest.fixture
    def app_with_router(self, mock_games_available) -> FastAPI:
        """Create app with games router."""
        app = FastAPI()

        mock_game_api = Mock()
        mock_game_api.discovered_games = {
            "chess": {"name": "Chess", "players": ["White", "Black"]},
            "tic_tac_toe": {"name": "Tic Tac Toe", "players": ["X", "O"]},
        }
        mock_game_api.exclude_games = []

        with patch(
            "haive.dataflow.api.routers.games.create_general_game_api"
        ) as mock_create:
            mock_create.return_value = (Mock(), mock_game_api)
            router = create_games_router()
            app.include_router(router)

        return app

    def test_list_games_endpoint(self, app_with_router: FastAPI):
        """Test listing games."""
        client = TestClient(app_with_router)

        # Note: This test is limited because we're mocking the internals
        # In a real integration test, we'd test the actual forwarding
        response = client.get("/games/meta")
        assert response.status_code == 200
        assert response.json()["total_games"] == 2

    def test_game_specific_endpoints(self, app_with_router: FastAPI):
        """Test game-specific endpoints are created."""
        client = TestClient(app_with_router)

        # Test chess endpoints
        response = client.get("/games/chess/test-thread")
        assert response.status_code == 200
        assert response.json()["game_id"] == "chess"

        # Test tic_tac_toe endpoints
        response = client.get("/games/tic_tac_toe/test-thread")
        assert response.status_code == 200
        assert response.json()["game_id"] == "tic_tac_toe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
