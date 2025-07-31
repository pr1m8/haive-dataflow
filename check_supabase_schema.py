"""Check Supabase Schema - Check Supabase Schema module.

TODO: Add comprehensive description of check supabase schema functionality.

This module provides core functionality for the Haive AI Agent Framework.

Key Components:
    - Core module components (see source code)

Example:
    Basic usage::

        from packages.haive-dataflow import None

        # Create instance
        instance = None(name='example')

        # Use the core functionality
        result = instance.None('input_data')

        print(f"Result: {result}")

Advanced Usage:
    TODO: Add advanced core functionality example

See Also:
    TODO: List related modules

Notes:
    TODO: Add implementation notes and caveats
"""

#!/usr/bin/env python3
"""Check the actual schema in Supabase."""

import asyncio

import psycopg


async def check_schema():
    """Check what tables and columns actually exist."""
    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)

        async with conn.cursor() as cursor:
            # Check public schema tables
            await cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
            public_tables = await cursor.fetchall()
            for _table in public_tables:
                pass

            # Check threads table structure if it exists
            if any("threads" in str(table) for table in public_tables):
                await cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'threads'
                    ORDER BY ordinal_position
                """
                )
                columns = await cursor.fetchall()
                for _col in columns:
                    pass

            # Check agent_state schema
            await cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'agent_state'
                ORDER BY table_name
            """
            )
            agent_tables = await cursor.fetchall()
            for _table in agent_tables:
                pass

            # Check checkpoints table structure if it exists
            if any("checkpoints" in str(table) for table in agent_tables):
                await cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'agent_state' AND table_name = 'checkpoints'
                    ORDER BY ordinal_position
                """
                )
                columns = await cursor.fetchall()
                for _col in columns:
                    pass

        await conn.close()

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_schema())
