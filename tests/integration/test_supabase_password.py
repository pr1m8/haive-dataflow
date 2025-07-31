#!/usr/bin/env python3
"""Test PostgreSQL connection with user-provided password."""

import asyncio

import psycopg


async def test_connection():
    """Test the connection with the password provided by user."""

    # Connection with the password user provided
    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    print("Testing connection to zkssazqhwcetsnbiuqik...")
    print(f"URI: {uri[:60]}...")

    try:
        # Try to connect
        conn = await psycopg.AsyncConnection.connect(uri)

        # If successful, check what we have
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT version()")
            version = await cursor.fetchone()
            print("✓ Connected successfully!"!")
            print(f"  PostgreSQL version: {version[0][:50]}...")

            # Check for agent_state schema
            await cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = 'agent_state'
                )
            """
            )
            has_agent_state = (await cursor.fetchone())[0]
            print(f"  agent_state schema exists: {has_agent_state}")

            # Check for public.threads table
            await cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'threads'
                )
            """
            )
            has_threads = (await cursor.fetchone())[0]
            print(f"  public.threads table exists: {has_threads}")

            # If we have the tables, this is the right database!
            if has_agent_state and has_threads:
                print("\n✓ This is the correct Supabase instance with our migrations!")
                print("\nNow updating .env file with the correct connection string...")

        await conn.close()
        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_connection())
