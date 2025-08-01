# end_to_end_test.py

import uuid

from haive.dataflow.registry.registry.core import registry_system
from haive.dataflow.registry.registry.models import EntityType
from haive.dataflow.registry.registry.providers.agent_provider import agent_provider

# Generate a session ID for tracking imports
session_id = str(uuid.uuid4())

# Discover agents
agent_ids = agent_provider.discover()

# Get all agents
agents = registry_system.list_entities(EntityType.AGENT)

# For each agent, print its dependencies and configurations
for agent in agents:

    # Get dependencies
    deps = registry_system.get_dependencies(agent.id)
    for dep in deps:
        dependent = registry_system.get_entity(dep.dependent_id)

    # Get configurations
    configs = registry_system.get_configurations(agent.id)
    for _config in configs:
        pass

# Check import logs
import_logs = registry_system._import_logs
for _log in import_logs:
    pass
