#!/usr/bin/env python3
"""Simple direct connection test to debug Supabase."""

import asyncio

import asyncpg


async def test():
    # Try different connection options
    print("Testing different Supabase connections...\n")

    # Option 1: zkssazqhwcetsnbiuqik with direct connection
    uri1 = "postgresql://postgres.zkssazqhwcetsnbiuqik:ITfz5B0wU6ehVXI1@db.zkssazqhwcetsnbiuqik.supabase.co:5432/postgres"
    print(f"1. Direct connection: {uri1[:80]}...")

    try:
        conn = await asyncpg.connect(uri1)
        print("✓ Connected!")

        # Test query
        result = await conn.fetchval("SELECT current_database()")
        print(f"✓ Database: {result}")

        # Check schemas
        schemas = await conn.fetch(
            "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name"
        )
        print(f"✓ Schemas: {[s['schema_name'] for s in schemas]}")

        await conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
