"""Test discovery with isolated imports to avoid circular dependencies."""

import sys
from pathlib import Path

# Add paths
haive_root = Path(__file__).parents[4]
sys.path.insert(0, str(haive_root / "packages" / "haive-core" / "src"))
sys.path.insert(0, str(haive_root / "packages" / "haive-dataflow" / "src"))

from haive.core.utils.haive_discovery.component_info import ComponentInfo

# Import only the specific discovery classes we need
from haive.core.utils.haive_discovery.haive_discovery import HaiveComponentDiscovery


def test_discovery_directly():
    """Test discovery system directly without circular imports."""
    print("🔍 Testing Direct Discovery System...\n")

    discovery = HaiveComponentDiscovery(str(haive_root))

    # Test 1: Discover tools
    print("📦 Testing Tool Discovery:")
    tools_path = (
        haive_root / "packages" / "haive-tools" / "src" / "haive" / "tools" / "tools"
    )
    if tools_path.exists():
        tool_components = discovery.discover_from_directory(
            tools_path, "haive.tools.tools", create_tools=False
        )
        print(f"  Found {len(tool_components)} tools")
        for comp in tool_components[:5]:  # Show first 5
            print(f"  - {comp.name}: {comp.module_path}")

    # Test 2: Discover agents
    print("\n🤖 Testing Agent Discovery:")
    agents_path = haive_root / "packages" / "haive-agents" / "src" / "haive" / "agents"
    if agents_path.exists():
        agent_components = discovery.discover_from_directory(
            agents_path, "haive.agents", create_tools=False
        )
        # Filter for actual agents
        agents = [c for c in agent_components if c.name.endswith("Agent")]
        print(f"  Found {len(agents)} agents")
        for comp in agents[:5]:  # Show first 5
            print(f"  - {comp.name}: {comp.module_path}")

    # Test 3: Discover games
    print("\n🎮 Testing Game Discovery:")
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
        print(f"  Found {len(game_agents)} game agents")
        for comp in game_agents[:5]:  # Show first 5
            game_name = comp.name.replace("Agent", "").lower()
            print(f"  - {game_name}: {comp.module_path}")


def test_fixed_api_logic():
    """Test the logic from our fixed APIs without full imports."""
    print("\n\n📋 Testing Fixed API Logic...\n")

    discovery = HaiveComponentDiscovery(str(haive_root))

    # Test component_to_tool_info logic
    print("🔧 Testing Tool Info Conversion:")
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
            tool_type = "toolkit" if "toolkit" in comp.module_path.lower() else "tool"
            category = "general"
            if "search" in comp.module_path.lower():
                category = "search"
            elif "database" in comp.module_path.lower():
                category = "database"

            print(f"  Component: {comp.name}")
            print(f"  Type: {tool_type}")
            print(f"  Category: {category}")
            print(f"  Module: {comp.module_path}")

    # Test agent type detection logic
    print("\n🤖 Testing Agent Type Detection:")
    # Test v1 agent path
    v1_path = "haive.core.engine.agent.config"
    v2_path = "haive.agents.conversational.chat_agent"

    print(f"  {v1_path} -> {'v1' if 'haive.core.engine.agent' in v1_path else 'v2'}")
    print(f"  {v2_path} -> {'v1' if 'haive.core.engine.agent' in v2_path else 'v2'}")

    # Test game discovery pattern
    print("\n🎮 Testing Game Pattern Matching:")
    test_names = [
        "ChessAgent",
        "TicTacToeAgent",
        "BaseAgent",
        "GenericAgent",
        "PokerAgent",
    ]
    for name in test_names:
        game_name = name.replace("Agent", "").lower()
        skip = game_name in ["base", "generic", "game"]
        print(f"  {name} -> {game_name} {'(skip)' if skip else '(include)'}")


def test_path_resolution():
    """Test path resolution logic."""
    print("\n\n📁 Testing Path Resolution...\n")

    # Test the path resolution from our fixed APIs
    from pathlib import Path

    # Simulate the path resolution in our fixed APIs
    current_file = Path(__file__)
    calculated_root = current_file.parents[4]  # Should go to haive root

    print(f"  Current file: {current_file}")
    print(f"  Calculated root: {calculated_root}")
    print(f"  Expected root: {haive_root}")
    print(f"  Match: {'✅' if calculated_root == haive_root else '❌'}")

    # Test discovery instance creation
    print("\n  Testing HaiveComponentDiscovery instantiation...")
    try:
        test_discovery = HaiveComponentDiscovery(str(calculated_root))
        print("  ✅ Discovery instance created successfully")
    except Exception as e:
        print(f"  ❌ Failed to create discovery instance: {e}")


if __name__ == "__main__":
    print("🧪 Isolated Discovery Tests")
    print("=" * 60)

    try:
        test_discovery_directly()
        test_fixed_api_logic()
        test_path_resolution()

        print("\n\n✅ All isolated tests completed!")

    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
