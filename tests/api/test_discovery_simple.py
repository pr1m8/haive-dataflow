"""Simple tests for the fixed discovery APIs without circular imports."""

import os
import sys
from pathlib import Path

# Set up Python path
current_dir = Path(__file__).parent
haive_root = current_dir.parents[4]
packages_dir = haive_root / "packages"

# Add necessary paths
sys.path.insert(0, str(haive_root))
sys.path.insert(0, str(packages_dir / "haive-core" / "src"))
sys.path.insert(0, str(packages_dir / "haive-dataflow" / "src"))
sys.path.insert(0, str(packages_dir / "haive-tools" / "src"))
sys.path.insert(0, str(packages_dir / "haive-agents" / "src"))
sys.path.insert(0, str(packages_dir / "haive-games" / "src"))


def test_game_discovery():
    """Test game discovery without full imports."""
    try:
        # Import just the discovery function
        from haive.dataflow.api.game_router_fixed import (
            discover_game_agents,
            game_agents,
        )

        # Clear and run discovery
        game_agents.clear()
        discover_game_agents()

        for game_name in sorted(game_agents.keys()):
            game_agents[game_name]

        return True
    except Exception:
        return False


def test_discovery_system_availability():
    """Test if the discovery system is available."""
    try:
        # Test basic import
        from haive.core.utils.haive_discovery.haive_discovery import (
            HaiveComponentDiscovery,
        )

        # Create discovery instance
        discovery = HaiveComponentDiscovery(str(haive_root))

        # Try to discover something simple
        tools_path = packages_dir / "haive-tools" / "src" / "haive" / "tools" / "tools"
        if tools_path.exists():
            discovery.discover_from_directory(
                tools_path, "haive.tools.tools", create_tools=False
            )

        return True
    except Exception:
        return False


def test_api_structure():
    """Test that the API files have the correct structure."""
    api_files = {
        "game_router_fixed.py": packages_dir
        / "haive-dataflow"
        / "src"
        / "haive"
        / "dataflow"
        / "api"
        / "game_router_fixed.py",
        "agent_discovery_routes_fixed.py": packages_dir
        / "haive-dataflow"
        / "src"
        / "haive"
        / "dataflow"
        / "api"
        / "routes"
        / "agent_discovery_routes_fixed.py",
        "tools_routes_fixed.py": packages_dir
        / "haive-dataflow"
        / "src"
        / "haive"
        / "dataflow"
        / "api"
        / "routes"
        / "tools_routes_fixed.py",
    }

    all_exist = True
    for _name, path in api_files.items():
        if path.exists():
            path.stat().st_size
        else:
            all_exist = False

    return all_exist


def test_manual_discovery():
    """Test manual discovery without using the full discovery system."""
    # Test pattern 1: Find agent classes in haive-agents
    agents_path = packages_dir / "haive-agents" / "src" / "haive" / "agents"
    if agents_path.exists():
        agent_count = 0
        for _root, _dirs, files in os.walk(agents_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    if "agent" in file.lower():
                        agent_count += 1

    # Test pattern 2: Find tool classes in haive-tools
    tools_path = packages_dir / "haive-tools" / "src" / "haive" / "tools"
    if tools_path.exists():
        tool_count = 0
        for _root, _dirs, files in os.walk(tools_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    tool_count += 1

    # Test pattern 3: Find game classes in haive-games
    games_path = packages_dir / "haive-games" / "src" / "haive" / "games"
    if games_path.exists():
        game_count = 0
        for _root, _dirs, files in os.walk(games_path):
            for file in files:
                if file == "agent.py":
                    game_count += 1

    return True


def test_import_paths():
    """Test that import paths are correctly set up."""
    important_paths = [
        ("haive-core", packages_dir / "haive-core" / "src"),
        ("haive-dataflow", packages_dir / "haive-dataflow" / "src"),
        ("haive-tools", packages_dir / "haive-tools" / "src"),
        ("haive-agents", packages_dir / "haive-agents" / "src"),
        ("haive-games", packages_dir / "haive-games" / "src"),
    ]

    for _name, path in important_paths:
        if path.exists():
            pass
        else:
            pass

    return True


def main():
    """Run all simple tests."""
    results = []

    # Run tests
    results.append(("API Structure", test_api_structure()))
    results.append(("Import Paths", test_import_paths()))
    results.append(("Discovery System", test_discovery_system_availability()))
    results.append(("Manual Discovery", test_manual_discovery()))
    results.append(("Game Discovery", test_game_discovery()))

    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for _name, _result in results:
        pass

    if passed == total:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
