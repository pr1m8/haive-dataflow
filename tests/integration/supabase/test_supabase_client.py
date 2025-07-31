#!/usr/bin/env python3
"""Test Supabase client connection."""

import os

from supabase import create_client


def test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    print(f"URL: {url}")
    print(f"Key: {key[:20]}..." if key else "No key found")

    try:
        supabase = create_client(url, key)
        print("✓ Created Supabase client")

        # Test query to check connection
        result = supabase.table("threads").select("*").limit(1).execute()
        print(f"✓ Query successful, found {len(result.data)} threads")

        # Check if agent_state schema tables exist
        for table in ["threads", "checkpoints", "conversations"]:
            try:
                result = (
                    supabase.schema("agent_state")
                    .table(table)
                    .select("*")
                    .limit(1)
                    .execute()
                )
                print(f"✓ agent_state.{table} exists")
            except Exception as e:
                print(f"❌ agent_state.{table}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test()
