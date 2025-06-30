#!/usr/bin/env python3
"""Check actual table structure in Supabase."""

import os

from supabase import create_client


def test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    supabase = create_client(url, key)
    print("Connected to Supabase\n")

    # Try to insert minimal data to see what columns exist
    print("Testing minimal thread insert...")

    # Try with just id
    try:
        result = supabase.table("threads").insert({}).execute()
        print(f"✓ Empty insert worked: {result.data}")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Empty insert failed: {error_msg}")

        # Extract required columns from error
        if "null value in column" in error_msg:
            import re

            match = re.search(r'null value in column "([^"]+)"', error_msg)
            if match:
                print(f"  Required column: {match.group(1)}")

    # Try to get any existing data
    print("\nChecking for any existing threads...")
    try:
        result = supabase.table("threads").select("*").execute()
        print(f"Found {len(result.data)} threads")
        if result.data:
            print("Sample thread structure:")
            print(result.data[0])
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test()
