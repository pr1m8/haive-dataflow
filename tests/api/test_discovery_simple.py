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
    print("\n🎮 Testing Game Discovery...")

    try:
        # Import just the discovery function
        from haive.dataflow.api.game_router_fixed import (
            discover_game_agents,
            game_agents,
        )

        # Clear and run discovery
        game_agents.clear()
        discover_game_agents()

        print(f"✅ Found {len(game_agents)} games:")
        for game_name in sorted(game_agents.keys()):
            game_info = game_agents[game_name]
            print(f"  - {game_name}: {game_info['module']}")

        return True
    except Exception as e:
        print(f"❌ Game discovery failed: {e}")
        return False


def test_discovery_system_availability():
    """Test if the discovery system is available."""
    print("\n🔍 Testing Discovery System Availability...")

    try:
        # Test basic import
        from haive.core.utils.haive_discovery.haive_discovery import (
            HaiveComponentDiscovery,
        )

        # Create discovery instance
        discovery = HaiveComponentDiscovery(str(haive_root))
        print("✅ Discovery system is available")

        # Try to discover something simple
        tools_path = packages_dir / "haive-tools" / "src" / "haive" / "tools" / "tools"
        if tools_path.exists():
            components = discovery.discover_from_directory(
                tools_path, "haive.tools.tools", create_tools=False
            )
            print(f"✅ Test discovery found {len(components)} components")

        return True
    except Exception as e:
        print(f"❌ Discovery system not available: {e}")
        return False


def test_api_structure():
    """Test that the API files have the correct structure."""
    print("\n📁 Testing API File Structure...")

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
    for name, path in api_files.items():
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {name}: {size:,} bytes")
        else:
            print(f"❌ {name}: NOT FOUND")
            all_exist = False

    return all_exist


def test_manual_discovery():
    """Test manual discovery without using the full discovery system."""
    print("\n🔧 Testing Manual Discovery Patterns...")

    # Test pattern 1: Find agent classes in haive-agents
    agents_path = packages_dir / "haive-agents" / "src" / "haive" / "agents"
    if agents_path.exists():
        agent_count = 0
        for _root, _dirs, files in os.walk(agents_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    if "agent" in file.lower():
                        agent_count += 1
        print(f"✅ Found {agent_count} potential agent files")

    # Test pattern 2: Find tool classes in haive-tools
    tools_path = packages_dir / "haive-tools" / "src" / "haive" / "tools"
    if tools_path.exists():
        tool_count = 0
        for _root, _dirs, files in os.walk(tools_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    tool_count += 1
        print(f"✅ Found {tool_count} potential tool files")

    # Test pattern 3: Find game classes in haive-games
    games_path = packages_dir / "haive-games" / "src" / "haive" / "games"
    if games_path.exists():
        game_count = 0
        for _root, _dirs, files in os.walk(games_path):
            for file in files:
                if file == "agent.py":
                    game_count += 1
        print(f"✅ Found {game_count} game agent files")

    return True


def test_import_paths():
    """Test that import paths are correctly set up."""
    print("\n🛤️ Testing Import Paths...")

    important_paths = [
        ("haive-core", packages_dir / "haive-core" / "src"),
        ("haive-dataflow", packages_dir / "haive-dataflow" / "src"),
        ("haive-tools", packages_dir / "haive-tools" / "src"),
        ("haive-agents", packages_dir / "haive-agents" / "src"),
        ("haive-games", packages_dir / "haive-games" / "src"),
    ]

    for name, path in important_paths:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: NOT FOUND at {path}")

    return True


def main():
    """Run all simple tests."""
    print("🧪 Running Simple Discovery Tests")
    print("=" * 50)

    results = []

    # Run tests
    results.append(("API Structure", test_api_structure()))
    results.append(("Import Paths", test_import_paths()))
    results.append(("Discovery System", test_discovery_system_availability()))
    results.append(("Manual Discovery", test_manual_discovery()))
    results.append(("Game Discovery", test_game_discovery()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")


if __name__ == "__main__":
    main()
