#!/usr/bin/env python3
"""Test script to see what happens when we generate JSON schemas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../../../.."))

from haive.agents.simple.agent import SimpleAgent

def test_schema_generation():
    """Test what happens when we try to generate JSON schemas."""
    
    print("🔍 Creating SimpleAgent...")
    agent = SimpleAgent(persistence=False)
    
    print("🔍 Compiling agent...")
    compiled_graph = agent.compile()
    
    print("🔍 Testing get_input_jsonschema...")
    try:
        input_schema = compiled_graph.get_input_jsonschema()
        print(f"✅ Input schema succeeded: {input_schema}")
        print(f"🔍 Input schema properties: {input_schema.get('properties', {}).keys()}")
    except Exception as e:
        print(f"❌ Input schema failed: {e}")
        print(f"🔍 Error type: {type(e)}")
        if "CallableSchema" in str(e):
            print("🎯 This is the CallableSchema error!")
    
    print("\n🔍 Testing get_output_jsonschema...")
    try:
        output_schema = compiled_graph.get_output_jsonschema()
        print(f"✅ Output schema succeeded: {output_schema}")
        print(f"🔍 Output schema properties: {output_schema.get('properties', {}).keys()}")
    except Exception as e:
        print(f"❌ Output schema failed: {e}")
        print(f"🔍 Error type: {type(e)}")
        if "CallableSchema" in str(e):
            print("🎯 This is the CallableSchema error!")

if __name__ == "__main__":
    test_schema_generation()