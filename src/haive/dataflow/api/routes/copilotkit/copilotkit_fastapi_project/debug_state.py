#!/usr/bin/env python3
"""Debug script to inspect SimpleAgent's auto-generated state schema."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../../../.."))

from haive.agents.simple.agent import SimpleAgent
from pydantic import BaseModel
import inspect

def debug_simple_agent_state():
    """Debug the SimpleAgent's auto-generated state schema."""
    
    print("🔍 Creating SimpleAgent...")
    agent = SimpleAgent(persistence=False)
    
    print("🔍 Compiling agent...")
    compiled_graph = agent.compile()
    
    print("🔍 Getting state schema...")
    # Access the state schema from the graph
    if hasattr(compiled_graph, 'graph') and hasattr(compiled_graph.graph, 'schema'):
        state_schema = compiled_graph.graph.schema
    elif hasattr(compiled_graph, '_state_schema'):
        state_schema = compiled_graph._state_schema
    elif hasattr(compiled_graph, 'state_schema'):
        state_schema = compiled_graph.state_schema
    elif hasattr(agent, 'state_schema'):
        state_schema = agent.state_schema
    else:
        print("❌ Cannot find state schema")
        return None, compiled_graph
    
    print(f"\n📋 State Schema Class: {state_schema}")
    print(f"📋 State Schema Name: {state_schema.__name__}")
    print(f"📋 State Schema Module: {state_schema.__module__}")
    print(f"📋 State Schema MRO: {[cls.__name__ for cls in state_schema.__mro__]}")
    
    print(f"\n🔍 State Schema Fields:")
    if hasattr(state_schema, 'model_fields'):
        for field_name, field_info in state_schema.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation} = {field_info.default}")
    
    print(f"\n🔍 State Schema Annotations:")
    if hasattr(state_schema, '__annotations__'):
        for field_name, field_type in state_schema.__annotations__.items():
            print(f"  - {field_name}: {field_type}")
    
    print(f"\n🔍 State Schema Dir:")
    schema_attrs = [attr for attr in dir(state_schema) if not attr.startswith('_')]
    for attr in schema_attrs:
        try:
            value = getattr(state_schema, attr)
            if not callable(value):
                print(f"  - {attr}: {value}")
        except:
            print(f"  - {attr}: <error accessing>")
    
    print(f"\n🔍 Creating state instance...")
    try:
        state_instance = state_schema()
        print(f"✅ State instance created: {type(state_instance)}")
        print(f"🔍 State instance fields:")
        
        if hasattr(state_instance, 'model_dump'):
            state_dict = state_instance.model_dump()
            for key, value in state_dict.items():
                print(f"  - {key}: {value} ({type(value).__name__})")
        else:
            for attr in dir(state_instance):
                if not attr.startswith('_') and not callable(getattr(state_instance, attr)):
                    try:
                        value = getattr(state_instance, attr)
                        print(f"  - {attr}: {value} ({type(value).__name__})")
                    except:
                        print(f"  - {attr}: <error accessing>")
                        
    except Exception as e:
        print(f"❌ Error creating state instance: {e}")
    
    print(f"\n🔍 Checking for token-related fields...")
    token_fields = []
    for attr in dir(state_schema):
        if 'token' in attr.lower() or 'usage' in attr.lower():
            token_fields.append(attr)
    
    if token_fields:
        print(f"🔍 Found token-related fields: {token_fields}")
    else:
        print("❌ No token-related fields found!")
    
    return state_schema, compiled_graph

if __name__ == "__main__":
    debug_simple_agent_state()