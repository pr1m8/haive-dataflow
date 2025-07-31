#!/usr/bin/env python3
"""Test direct PostgreSQL connection with explicit credentials."""

import asyncio

import psycopg


async def test_connections():
    """Test different connection configurations."""

    print("Testing PostgreSQL connections to Supabase...\n")

    # Connection configurations to test
    connections = [
        {
            "name": "oecoeyomphckolkywbzz (pooler)",
            "uri": "postgresql://postgres.oecoeyomphckolkywbzz:ITfz5B0wU6ehVXI1@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        },
        {
            "name": "zkssazqhwcetsnbiuqik (pooler connection)",
            "uri": "postgresql://postgres.zkssazqhwcetsnbiuqik:J89XqGf7hDkKejOK1n02TKVT78TtncD3gP0TH68N4AV1H87viAt9EhQxVp0mfUxkBNHowVCng2okkmPHYZpiKA==@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        },
        {
            "name": "zkssazqhwcetsnbiuqik (with previous password attempt)",
            "uri": "postgresql://postgres.zkssazqhwcetsnbiuqik:1f63f970091555d33f42b4df67356b7532fcbfd4@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        },
        {
            "name": "zkssazqhwcetsnbiuqik (with new password from user)",
            "uri": "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        },
        {
            "name": "zkssazqhwcetsnbiuqik (check if we need project ref in username)",
            "uri": "postgresql://postgres:J89XqGf7hDkKejOK1n02TKVT78TtncD3gP0TH68N4AV1H87viAt9EhQxVp0mfUxkBNHowVCng2okkmPHYZpiKA==@zkssazqhwcetsnbiuqik.supabase.co:5432/postgres?sslmode=require",
        },
    ]

    for config in connections:
        print(f"=== Testing: {config['name']} ===")
        try:
            # Try to connect
            conn = await psycopg.AsyncConnection.connect(config["uri"])

            # If successful, run a query
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

            await conn.close()

        except Exception as e:
            print(f"✗ Connection failed: {e}")

        print()


if __name__ == "__main__":
    asyncio.run(test_connections())
