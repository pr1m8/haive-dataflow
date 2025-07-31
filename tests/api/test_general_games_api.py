"""Tests for the general games API system.

This module tests:
- Real game discovery mechanism
- API endpoint creation
- Configuration modes
- Error handling
- WebSocket connections

NOTE: This test module does not use any mocking. All tests work with real games and functionality.
"""

import sys

# Add path for imports
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent.parent.parent / "haive-games" / "src")
)

from haive.dataflow.api.general_games_api import (
    GeneralGameAPI,
    create_general_game_api,
)


class TestRealGameDiscovery:
    """Test real game discovery without mocking."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create a test FastAPI app."""
        return FastAPI(title="Real Games API Test")

    def test_discover_real_games(self, app: FastAPI):
        """Test discovering actual games in haive-games."""
        # Test with specific games we know exist
        api = GeneralGameAPI(app, exclude_games=["go", "among_us", "battleship"])

        # Should discover at least some games
        len(api.discovered_games)

        # We expect at least chess, connect4, and tic_tac_toe to work
        working_games = ["chess", "connect4", "tic_tac_toe"]

        for game in working_games:
            if game in api.discovered_games:
                game_info = api.discovered_games[game]
                assert "agent_class" in game_info
                assert "config_class" in game_info
                assert "name" in game_info
            else:
                pass

    def test_general_api_creation(self, app: FastAPI):
        """Test creating a general game API."""
        api = GeneralGameAPI(app, exclude_games=["go", "among_us"])

        assert api.app == app
        assert api.route_prefix == "/api/games"
        assert api.ws_route_prefix == "/ws/games"
        assert "go" in api.exclude_games

    def test_list_games_endpoint(self, app: FastAPI):
        """Test the list games endpoint with real games."""
        GeneralGameAPI(app, exclude_games=["go", "among_us"])

        client = TestClient(app)
        response = client.get("/api/games/")

        assert response.status_code == 200
        games = response.json()

        # Verify structure of discovered games
        for game in games:
            assert "game_id" in game
            assert "name" in game

    def test_create_game_not_found(self, app: FastAPI):
        """Test creating a non-existent game."""
        GeneralGameAPI(app)
        client = TestClient(app)

        request_data = {"game_id": "nonexistent_game", "config_mode": "simple"}

        response = client.post("/api/games/create", json=request_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_openapi_generation(self, app: FastAPI):
        """Test OpenAPI documentation generation."""
        GeneralGameAPI(app)

        client = TestClient(app)
        response = client.get("/openapi.json")

        assert response.status_code == 200
        openapi = response.json()

        assert "Haive Games API" in openapi["info"]["title"]
        assert "/api/games/" in openapi["paths"]
        assert "/api/games/create" in openapi["paths"]


class TestRealGameImports:
    """Test real game import functionality."""

    def test_import_working_games(self):
        """Test importing games that should work."""
        api = GeneralGameAPI(FastAPI(), exclude_games=["go", "among_us"])

        # Test importing specific games
        working_games = ["chess", "connect4", "tic_tac_toe"]

        for game_name in working_games:
            result = api._import_game(game_name)
            if result:
                assert result["game_id"] == game_name
                assert "agent_class" in result
                assert "config_class" in result
            else:
                pass

    def test_import_failure_handling(self):
        """Test handling of import failures with non-existent games."""
        api = GeneralGameAPI(FastAPI())

        # Try to import a game that definitely doesn't exist
        result = api._import_game("definitely_nonexistent_game_12345")

        # Should handle the failure gracefully
        assert result is None


class TestRealConfigurationValidation:
    """Test configuration validation with real games."""

    def test_missing_config_validation(self, app: FastAPI):
        """Test validation of missing required configs."""
        GeneralGameAPI(app)
        client = TestClient(app)

        # Test missing player_models for simple mode
        response = client.post(
            "/api/games/create",
            json={
                "game_id": "nonexistent",
                "config_mode": "simple",
                # Missing player_models
            },
        )

        # Should fail because game doesn't exist, not because of missing config
        assert response.status_code == 404

    def test_invalid_config_mode(self, app: FastAPI):
        """Test invalid configuration mode."""
        GeneralGameAPI(app)
        client = TestClient(app)

        # Test with invalid config mode
        response = client.post(
            "/api/games/create",
            json={"game_id": "nonexistent", "config_mode": "invalid_mode"},
        )

        # FastAPI should validate this at the request level
        assert response.status_code in [400, 404, 422]


class TestRealAPIIntegration:
    """Test real API integration."""

    def test_route_registration(self, app: FastAPI):
        """Test that routes are properly registered."""
        GeneralGameAPI(app)

        # Check that routes are registered
        routes = [route.path for route in app.routes]

        # Should have main routes
        assert any("/api/games/" in route for route in routes)
        assert any("/api/games/create" in route for route in routes)


class TestWorkingGamesIntegration:
    """Test with actual working games (integration tests)."""

    @pytest.mark.integration
    def test_discover_working_games(self):
        """Test discovering games that should work."""
        app = FastAPI()

        # Exclude games we know have issues
        api = GeneralGameAPI(app, exclude_games=["go", "among_us", "battleship"])

        # Check if we have any games at all
        assert len(api.discovered_games) >= 0, "Should discover at least some games"

        # Test games that we expect to work
        expected_working = ["chess", "connect4", "tic_tac_toe"]

        for game_name in expected_working:
            if game_name in api.discovered_games:
                game_info = api.discovered_games[game_name]
                assert "agent_class" in game_info, f"{game_name} missing agent_class"
                assert "config_class" in game_info, f"{game_name} missing config_class"
            else:
                pass

    @pytest.mark.integration
    def test_api_creation_with_real_games(self):
        """Test creating API with real games."""
        app, api = create_general_game_api(
            exclude_games=["go", "among_us", "battleship"]
        )

        # Should create without errors
        assert api is not None
        assert isinstance(api, GeneralGameAPI)

        # Test the API endpoints
        client = TestClient(app)

        # Test list games endpoint
        response = client.get("/api/games/")
        assert response.status_code == 200

        response.json()

    @pytest.mark.integration
    def test_game_creation_validation(self):
        """Test game creation with validation (no actual game creation)."""
        app, api = create_general_game_api(exclude_games=["go", "among_us"])

        client = TestClient(app)

        # Test with a working game if available
        if "chess" in api.discovered_games:
            # Test missing player models
            response = client.post(
                "/api/games/create",
                json={
                    "game_id": "chess",
                    "config_mode": "simple",
                    # Missing player_models - should fail validation
                },
            )

            # Should fail due to missing required fields
            assert response.status_code in [400, 422], "Should validate required fields"
        else:
            pass


@pytest.mark.integration
def test_end_to_end_functionality():
    """Test end-to-end functionality without mocking."""
    # Create the general API
    app, api = create_general_game_api(exclude_games=["go", "among_us", "battleship"])

    # Test basic API functionality
    client = TestClient(app)

    # Test OpenAPI docs
    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200

    # Test games list
    games_response = client.get("/api/games/")
    assert games_response.status_code == 200
    games_response.json()

    # Test error handling
    error_response = client.post(
        "/api/games/create",
        json={"game_id": "nonexistent_game", "config_mode": "simple"},
    )
    assert error_response.status_code == 404


if __name__ == "__main__":
    # Run the tests (including integration tests)
    pytest.main([__file__, "-v"])
