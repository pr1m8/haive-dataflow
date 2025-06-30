"""Tests for the fixed discovery API routes."""

from unittest.mock import Mock, patch

import pytest
from haive.core.utils.haive_discovery import ComponentInfo


class TestAgentDiscoveryFixed:
    """Test the fixed agent discovery routes."""

    @pytest.fixture
    def mock_components(self):
        """Create mock component info objects."""
        return [
            ComponentInfo(
                name="TestAgent",
                module_path="haive.agents.test.agent",
                file_path="/test/agent.py",
                component_type="agent",
                description="Test agent",
                metadata={"version": "1.0", "category": "test"},
            ),
            ComponentInfo(
                name="ChatConfig",
                module_path="haive.core.engine.agent.config",
                file_path="/test/config.py",
                component_type="config",
                description="Chat config",
                metadata={"version": "1.0"},
            ),
        ]

    @pytest.mark.asyncio
    async def test_list_agents(self, mock_components):
        """Test listing agents endpoint."""
        with patch(
            "haive.dataflow.api.routes.agent_discovery_routes_fixed.discover_all_agents",
            return_value=mock_components,
        ):
            from haive.dataflow.api.routes.agent_discovery_routes_fixed import (
                list_agents,
            )

            response = await list_agents()

            assert response.count == 2
            assert response.v1_count == 1  # ChatConfig is v1
            assert response.v2_count == 1  # TestAgent is v2
            assert response.discovery_method == "haive-core unified discovery"
            assert len(response.agents) == 2

    @pytest.mark.asyncio
    async def test_search_agents(self, mock_components):
        """Test searching agents."""
        with patch(
            "haive.dataflow.api.routes.agent_discovery_routes_fixed.discover_all_agents",
            return_value=mock_components,
        ):
            from haive.dataflow.api.routes.agent_discovery_routes_fixed import (
                search_agents,
            )

            # Search by type
            response = await search_agents(agent_type="v2")
            assert response.count == 1
            assert response.agents[0].name == "testagent"

            # Search by query
            response = await search_agents(query="chat")
            assert response.count == 1
            assert response.agents[0].name == "chat"

    @pytest.mark.asyncio
    async def test_get_agent_stats(self, mock_components):
        """Test agent statistics endpoint."""
        with patch(
            "haive.dataflow.api.routes.agent_discovery_routes_fixed.discover_all_agents",
            return_value=mock_components,
        ):
            from haive.dataflow.api.routes.agent_discovery_routes_fixed import (
                get_agent_stats,
            )

            stats = await get_agent_stats()

            assert stats["total_agents"] == 2
            assert stats["v1_agents"] == 1
            assert stats["v2_agents"] == 1
            assert "categories" in stats
            assert stats["discovery_method"] == "haive-core unified discovery"


class TestToolDiscoveryFixed:
    """Test the fixed tool discovery routes."""

    @pytest.fixture
    def mock_tools(self):
        """Create mock tool components."""
        return [
            ComponentInfo(
                name="SearchTool",
                module_path="haive.tools.tools.search",
                file_path="/test/search.py",
                component_type="tool",
                description="Search tool",
                metadata={"category": "search", "schema": {"type": "object"}},
            ),
            ComponentInfo(
                name="DatabaseToolkit",
                module_path="haive.tools.toolkits.database",
                file_path="/test/database.py",
                component_type="toolkit",
                description="Database toolkit",
                metadata={"category": "database"},
            ),
        ]

    @pytest.mark.asyncio
    async def test_list_tools(self, mock_tools):
        """Test listing tools endpoint."""
        with patch(
            "haive.dataflow.api.routes.tools_routes_fixed.discover_all_tools",
            return_value=mock_tools,
        ):
            from haive.dataflow.api.routes.tools_routes_fixed import list_tools

            response = await list_tools()

            assert response.count == 2
            assert response.tool_count == 1
            assert response.toolkit_count == 1
            assert response.discovery_method == "haive-core unified discovery"

    @pytest.mark.asyncio
    async def test_search_tools(self, mock_tools):
        """Test searching tools."""
        with patch(
            "haive.dataflow.api.routes.tools_routes_fixed.discover_all_tools",
            return_value=mock_tools,
        ):
            from haive.dataflow.api.routes.tools_routes_fixed import search_tools

            # Search by type
            response = await search_tools(tool_type="toolkit")
            assert response.count == 1
            assert response.tools[0].name == "DatabaseToolkit"

            # Search by category
            response = await search_tools(category="search")
            assert response.count == 1
            assert response.tools[0].name == "SearchTool"

    @pytest.mark.asyncio
    async def test_get_tool_schema(self, mock_tools):
        """Test getting tool schema."""
        with patch(
            "haive.dataflow.api.routes.tools_routes_fixed.discover_all_tools",
            return_value=mock_tools,
        ):
            from haive.dataflow.api.routes.tools_routes_fixed import (
                get_tool_schema_endpoint,
            )

            schema = await get_tool_schema_endpoint("SearchTool")

            assert schema.name == "SearchTool"
            assert schema.description == "Search tool"
            assert schema.input_schema == {"type": "object"}


class TestGameDiscoveryFixed:
    """Test the fixed game discovery."""

    @pytest.fixture
    def mock_game_components(self):
        """Create mock game components."""
        chess_agent = Mock()
        chess_agent.__name__ = "ChessAgent"

        return [
            ComponentInfo(
                name="ChessAgent",
                module_path="haive.games.chess.agent",
                file_path="/test/chess.py",
                component_type="agent",
                description="Chess game agent",
                metadata={},
                class_obj=chess_agent,
            ),
            ComponentInfo(
                name="ChessState",
                module_path="haive.games.chess.state",
                file_path="/test/chess.py",
                component_type="state",
                description="Chess game state",
                metadata={},
                class_obj=Mock(),
            ),
        ]

    def test_discover_game_agents(self, mock_game_components):
        """Test game agent discovery."""
        with patch(
            "haive.dataflow.api.game_router_fixed.HaiveComponentDiscovery"
        ) as mock_discovery:
            mock_instance = Mock()
            mock_instance.discover_from_directory.return_value = mock_game_components
            mock_discovery.return_value = mock_instance

            from haive.dataflow.api.game_router_fixed import (
                discover_game_agents,
                game_agents,
            )

            game_agents.clear()
            discover_game_agents()

            assert "chess" in game_agents
            assert game_agents["chess"]["name"] == "chess"
            assert game_agents["chess"]["agent_class"] is not None
            assert game_agents["chess"]["module"] == "haive.games.chess.agent"


if __name__ == "__main__":
    # Run basic smoke tests
    print("🧪 Testing Fixed Discovery APIs\n")

    # Test imports
    print("1. Testing imports...")
    try:
        from haive.dataflow.api.game_router_fixed import discover_game_agents
        from haive.dataflow.api.routes.agent_discovery_routes_fixed import list_agents
        from haive.dataflow.api.routes.tools_routes_fixed import list_tools

        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")

    print("\n✅ Basic tests complete. Run with pytest for full test suite.")
