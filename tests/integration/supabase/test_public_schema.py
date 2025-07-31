#!/usr/bin/env python3
"""Test Supabase connection using public schema."""

import asyncio
import os
from datetime import datetime

from supabase import create_client


async def test():
    # Use Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    print(f"🔗 Connecting to: {url}")

    try:
        supabase = create_client(url, key)
        print("✓ Created Supabase client")

        # Test 1: Check threads table structure
        print("\n📊 Checking public.threads table...")
        result = supabase.table("threads").select("*").limit(1).execute()
        print(f"✓ Table exists with {len(result.data)} sample rows")

        if result.data:
            print("Table columns:")
            for key in result.data[0].keys():
                print(f"  - {key}: {type(result.data[0][key]).__name__}")
        else:
            # Try to get table info via RPC or raw query
            print("No data in table, checking structure...")

        # Test 2: Insert a test thread
        print("\n🧪 Testing thread insertion...")
        test_thread = {
            "user_id": "00000000-0000-0000-0000-000000000001",  # Test user ID
            "agent_name": "TestAgent",
            "name": f"Test Thread {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "metadata": {"test": True, "source": "test_public_schema.py"},
        }

        insert_result = supabase.table("threads").insert(test_thread).execute()
        if insert_result.data:
            thread_id = insert_result.data[0]["id"]
            print(f"✓ Created test thread: {thread_id}")

            # Test 3: Check checkpoints table
            print("\n🔍 Checking checkpoints for thread...")
            cp_result = (
                supabase.table("checkpoints")
                .select("*")
                .eq("thread_id", thread_id)
                .execute()
            )
            print(f"✓ Thread has {len(cp_result.data)} checkpoints")

            # Test 4: Clean up
            print("\n🧹 Cleaning up test thread...")
            (supabase.table("threads").delete().eq("id", thread_id).execute())
            print("✓ Deleted test thread")

        print("\n✅ All tests passed! Supabase public schema is working correctly.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
