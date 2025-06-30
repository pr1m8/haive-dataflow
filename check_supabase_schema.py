#!/usr/bin/env python3
"""Check the actual schema in Supabase."""

import asyncio

import psycopg


async def check_schema():
    """Check what tables and columns actually exist."""
    print("Checking Supabase schema...")

    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)
        print("✓ Connected to Supabase")

        async with conn.cursor() as cursor:
            # Check public schema tables
            print("\n=== PUBLIC SCHEMA TABLES ===")
            await cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
            public_tables = await cursor.fetchall()
            for table in public_tables:
                print(f"  {table[0]}")

            # Check threads table structure if it exists
            if any("threads" in str(table) for table in public_tables):
                print("\n=== THREADS TABLE COLUMNS ===")
                await cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = 'threads'
                    ORDER BY ordinal_position
                """
                )
                columns = await cursor.fetchall()
                for col in columns:
                    print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")

            # Check agent_state schema
            print("\n=== AGENT_STATE SCHEMA TABLES ===")
            await cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'agent_state'
                ORDER BY table_name
            """
            )
            agent_tables = await cursor.fetchall()
            for table in agent_tables:
                print(f"  {table[0]}")

            # Check checkpoints table structure if it exists
            if any("checkpoints" in str(table) for table in agent_tables):
                print("\n=== CHECKPOINTS TABLE COLUMNS ===")
                await cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'agent_state' AND table_name = 'checkpoints'
                    ORDER BY ordinal_position
                """
                )
                columns = await cursor.fetchall()
                for col in columns:
                    print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")

        await conn.close()

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_schema())
