#!/usr/bin/env python3
"""Simple direct connection test to debug Supabase."""

import asyncio

import asyncpg


async def test():
    # Try different connection options

    # Option 1: zkssazqhwcetsnbiuqik with direct connection
    uri1 = "postgresql://postgres.zkssazqhwcetsnbiuqik:ITfz5B0wU6ehVXI1@db.zkssazqhwcetsnbiuqik.supabase.co:5432/postgres"

    try:
        conn = await asyncpg.connect(uri1)

        # Test query
        await conn.fetchval("SELECT current_database()")

        # Check schemas
        await conn.fetch(
            "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name"
        )

        await conn.close()
    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
