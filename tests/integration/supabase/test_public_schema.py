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

    try:
        supabase = create_client(url, key)

        # Test 1: Check threads table structure
        result = supabase.table("threads").select("*").limit(1).execute()

        if result.data:
            for key in result.data[0]:
                pass
        else:
            # Try to get table info via RPC or raw query
            pass

        # Test 2: Insert a test thread
        test_thread = {
            "user_id": "00000000-0000-0000-0000-000000000001",  # Test user ID
            "agent_name": "TestAgent",
            "name": f"Test Thread {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "metadata": {"test": True, "source": "test_public_schema.py"},
        }

        insert_result = supabase.table("threads").insert(test_thread).execute()
        if insert_result.data:
            thread_id = insert_result.data[0]["id"]

            # Test 3: Check checkpoints table
            (
                supabase.table("checkpoints")
                .select("*")
                .eq("thread_id", thread_id)
                .execute()
            )

            # Test 4: Clean up
            (supabase.table("threads").delete().eq("id", thread_id).execute())

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
