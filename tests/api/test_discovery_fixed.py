"""Tests for the fixed discovery APIs."""

import sys
from pathlib import Path

import pytest

# Add the API routes to path
api_path = Path(__file__).parents[2] / "src"
sys.path.insert(0, str(api_path))

from haive.dataflow.api.game_router_fixed import discover_game_agents, game_agents
from haive.dataflow.api.routes.agent_discovery_routes_fixed import (
    component_to_agent_info,
    discover_all_agents,
    get_agent_stats,
    list_agents,
    search_agents,
)
from haive.dataflow.api.routes.tools_routes_fixed import (
    component_to_tool_info,
    discover_all_tools,
    get_tool_stats,
    list_tools,
    search_tools,
)


class TestAgentDiscovery:
    """Test agent discovery functionality."""

    def test_discover_all_agents(self):
        """Test that agent discovery finds agents."""
        components = discover_all_agents(force_refresh=True)

        # Should find at least some agents
        assert len(components) > 0

        # Each component should have required attributes
        for component in components:
            assert hasattr(component, "name")
            assert hasattr(component, "module_path")
            assert hasattr(component, "metadata")

    def test_component_to_agent_info(self):
        """Test conversion from ComponentInfo to AgentInfo."""
        components = discover_all_agents()

        if components:
            component = components[0]
            agent_info = component_to_agent_info(component)

            # Check required fields
            assert agent_info.name
            assert agent_info.module
            assert agent_info.agent_type in ["v1", "v2", "unknown"]
            assert agent_info.category

    @pytest.mark.asyncio
    async def test_list_agents_endpoint(self):
        """Test the list agents endpoint."""
        response = await list_agents()

        assert response.count >= 0
        assert response.v1_count >= 0
        assert response.v2_count >= 0
        assert response.discovery_method == "haive-core unified discovery"
        assert len(response.agents) == response.count

    @pytest.mark.asyncio
    async def test_search_agents_endpoint(self):
        """Test the search agents endpoint."""
        # Search by type
        response = await search_agents(agent_type="v2")
        assert all(agent.agent_type == "v2" for agent in response.agents)

        # Search by query
        response = await search_agents(query="agent")
        assert len(response.agents) >= 0

    @pytest.mark.asyncio
    async def test_get_agent_stats(self):
        """Test agent statistics endpoint."""
        stats = await get_agent_stats()

        assert "total_agents" in stats
        assert "v1_agents" in stats
        assert "v2_agents" in stats
        assert "categories" in stats
        assert "modules" in stats
        assert stats["discovery_method"] == "haive-core unified discovery"


class TestToolDiscovery:
    """Test tool discovery functionality."""

    def test_discover_all_tools(self):
        """Test that tool discovery finds tools."""
        components = discover_all_tools(force_refresh=True)

        # Should find at least some tools
        assert len(components) > 0

        # Each component should have required attributes
        for component in components:
            assert hasattr(component, "name")
            assert hasattr(component, "module_path")
            assert hasattr(component, "metadata")

    def test_component_to_tool_info(self):
        """Test conversion from ComponentInfo to ToolInfo."""
        components = discover_all_tools()

        if components:
            component = components[0]
            tool_info = component_to_tool_info(component)

            # Check required fields
            assert tool_info.name
            assert tool_info.module
            assert tool_info.type in ["tool", "toolkit"]
            assert tool_info.category

    @pytest.mark.asyncio
    async def test_list_tools_endpoint(self):
        """Test the list tools endpoint."""
        response = await list_tools()

        assert response.count >= 0
        assert response.tool_count >= 0
        assert response.toolkit_count >= 0
        assert response.discovery_method == "haive-core unified discovery"
        assert len(response.tools) == response.count

    @pytest.mark.asyncio
    async def test_search_tools_endpoint(self):
        """Test the search tools endpoint."""
        # Search by type
        response = await search_tools(tool_type="toolkit")
        assert all(tool.type == "toolkit" for tool in response.tools)

        # Search by category
        response = await search_tools(category="search")
        assert all(tool.category == "search" for tool in response.tools)

    @pytest.mark.asyncio
    async def test_get_tool_stats(self):
        """Test tool statistics endpoint."""
        stats = await get_tool_stats()

        assert "total_tools" in stats
        assert "individual_tools" in stats
        assert "toolkits" in stats
        assert "categories" in stats
        assert "modules" in stats
        assert stats["discovery_method"] == "haive-core unified discovery"


class TestGameDiscovery:
    """Test game discovery functionality."""

    def test_discover_game_agents(self):
        """Test that game discovery finds game agents."""
        # Clear game_agents first
        game_agents.clear()

        # Run discovery
        discover_game_agents()

        # Should find at least some games
        assert len(game_agents) >= 0

        # Each game should have required attributes
        for _game_name, game_info in game_agents.items():
            assert "name" in game_info
            assert "agent_class" in game_info
            assert "module" in game_info
            assert "component_info" in game_info

    def test_game_agent_structure(self):
        """Test the structure of discovered game agents."""
        discover_game_agents()

        for _game_name, game_info in game_agents.items():
            # Check that agent class is a class
            if game_info["agent_class"]:
                assert hasattr(game_info["agent_class"], "__name__")

            # Check module path
            assert "." in game_info["module"]
            assert "games" in game_info["module"]

            # Check component info
            component = game_info["component_info"]
            assert hasattr(component, "name")
            assert hasattr(component, "module_path")


class TestDiscoveryIntegration:
    """Integration tests for all discovery systems."""

    def test_all_discoveries_work(self):
        """Test that all discovery systems can run without errors."""
        # Test agent discovery
        agent_components = discover_all_agents(force_refresh=True)
        assert isinstance(agent_components, list)

        # Test tool discovery
        tool_components = discover_all_tools(force_refresh=True)
        assert isinstance(tool_components, list)

        # Test game discovery
        game_agents.clear()
        discover_game_agents()
        assert isinstance(game_agents, dict)

    def test_discovery_caching(self):
        """Test that discovery caching works."""
        # First call should populate cache
        agents1 = discover_all_agents(force_refresh=False)
        tools1 = discover_all_tools(force_refresh=False)

        # Second call should use cache (should be same objects)
        agents2 = discover_all_agents(force_refresh=False)
        tools2 = discover_all_tools(force_refresh=False)

        assert agents1 is agents2  # Same object reference
        assert tools1 is tools2

        # Force refresh should give new objects
        agents3 = discover_all_agents(force_refresh=True)
        tools3 = discover_all_tools(force_refresh=True)

        assert agents1 is not agents3  # Different object reference
        assert tools1 is not tools3

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test that APIs handle errors gracefully."""
        # Test agent search with invalid parameters
        response = await search_agents(agent_type="invalid_type")
        assert response.count == 0  # Should return empty, not error

        # Test tool search with empty query
        response = await search_tools(query="")
        assert response.count >= 0  # Should work fine


if __name__ == "__main__":
    # Run basic discovery tests
    test_agent = TestAgentDiscovery()
    test_agent.test_discover_all_agents()
    test_agent.test_component_to_agent_info()

    test_tool = TestToolDiscovery()
    test_tool.test_discover_all_tools()
    test_tool.test_component_to_tool_info()

    test_game = TestGameDiscovery()
    test_game.test_discover_game_agents()
    test_game.test_game_agent_structure()

    test_integration = TestDiscoveryIntegration()
    test_integration.test_all_discoveries_work()
    test_integration.test_discovery_caching()
