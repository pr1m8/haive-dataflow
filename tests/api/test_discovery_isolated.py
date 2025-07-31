"""Test discovery with isolated imports to avoid circular dependencies."""

import sys
from pathlib import Path

# Add paths
haive_root = Path(__file__).parents[4]
sys.path.insert(0, str(haive_root / "packages" / "haive-core" / "src"))
sys.path.insert(0, str(haive_root / "packages" / "haive-dataflow" / "src"))


# Import only the specific discovery classes we need
import contextlib

from haive.core.utils.haive_discovery.haive_discovery import HaiveComponentDiscovery


def test_discovery_directly():
    """Test discovery system directly without circular imports."""
    discovery = HaiveComponentDiscovery(str(haive_root))

    # Test 1: Discover tools
    tools_path = (
        haive_root / "packages" / "haive-tools" / "src" / "haive" / "tools" / "tools"
    )
    if tools_path.exists():
        tool_components = discovery.discover_from_directory(
            tools_path, "haive.tools.tools", create_tools=False
        )
        for comp in tool_components[:5]:  # Show first 5
            pass

    # Test 2: Discover agents
    agents_path = haive_root / "packages" / "haive-agents" / "src" / "haive" / "agents"
    if agents_path.exists():
        agent_components = discovery.discover_from_directory(
            agents_path, "haive.agents", create_tools=False
        )
        # Filter for actual agents
        agents = [c for c in agent_components if c.name.endswith("Agent")]
        for comp in agents[:5]:  # Show first 5
            pass

    # Test 3: Discover games
    games_path = haive_root / "packages" / "haive-games" / "src" / "haive" / "games"
    if games_path.exists():
        game_components = discovery.discover_from_directory(
            games_path, "haive.games", create_tools=False
        )
        # Filter for game agents
        game_agents = [
            c
            for c in game_components
            if c.name.endswith("Agent") and "games" in c.module_path
        ]
        for comp in game_agents[:5]:  # Show first 5
            comp.name.replace("Agent", "").lower()


def test_fixed_api_logic():
    """Test the logic from our fixed APIs without full imports."""
    discovery = HaiveComponentDiscovery(str(haive_root))

    # Test component_to_tool_info logic
    tools_path = (
        haive_root / "packages" / "haive-tools" / "src" / "haive" / "tools" / "tools"
    )
    if tools_path.exists():
        components = discovery.discover_from_directory(
            tools_path, "haive.tools.tools", create_tools=False
        )
        if components:
            comp = components[0]
            # Simulate component_to_tool_info
            "toolkit" if "toolkit" in comp.module_path.lower() else "tool"
            if (
                "search" in comp.module_path.lower()
                or "database" in comp.module_path.lower()
            ):
                pass

    # Test agent type detection logic
    # Test v1 agent path

    # Test game discovery pattern
    test_names = [
        "ChessAgent",
        "TicTacToeAgent",
        "BaseAgent",
        "GenericAgent",
        "PokerAgent",
    ]
    for name in test_names:
        name.replace("Agent", "").lower()


def test_path_resolution():
    """Test path resolution logic."""
    # Test the path resolution from our fixed APIs
    from pathlib import Path

    # Simulate the path resolution in our fixed APIs
    current_file = Path(__file__)
    calculated_root = current_file.parents[4]  # Should go to haive root

    # Test discovery instance creation
    with contextlib.suppress(Exception):
        HaiveComponentDiscovery(str(calculated_root))


if __name__ == "__main__":

    try:
        test_discovery_directly()
        test_fixed_api_logic()
        test_path_resolution()

    except Exception:
        import traceback

        traceback.print_exc()
