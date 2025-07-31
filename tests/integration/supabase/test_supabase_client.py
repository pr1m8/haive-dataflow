#!/usr/bin/env python3
"""Test Supabase client connection."""

import contextlib
import os

from supabase import create_client


def test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    try:
        supabase = create_client(url, key)

        # Test query to check connection
        supabase.table("threads").select("*").limit(1).execute()

        # Check if agent_state schema tables exist
        for table in ["threads", "checkpoints", "conversations"]:
            with contextlib.suppress(Exception):
                (
                    supabase.schema("agent_state")
                    .table(table)
                    .select("*")
                    .limit(1)
                    .execute()
                )

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test()
