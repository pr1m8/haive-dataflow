#!/usr/bin/env python3
"""Check actual table structure in Supabase."""

import os

from supabase import create_client


def test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    supabase = create_client(url, key)

    # Try to insert minimal data to see what columns exist

    # Try with just id
    try:
        result = supabase.table("threads").insert({}).execute()
    except Exception as e:
        error_msg = str(e)

        # Extract required columns from error
        if "null value in column" in error_msg:
            import re

            match = re.search(r'null value in column "([^"]+)"', error_msg)
            if match:
                pass

    # Try to get any existing data
    try:
        result = supabase.table("threads").select("*").execute()
        if result.data:
            pass
    except Exception:
        pass


if __name__ == "__main__":
    test()
