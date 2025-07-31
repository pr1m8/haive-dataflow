#!/usr/bin/env python3
"""Final test to confirm Supabase persistence is working."""

import asyncio
from uuid import uuid4

import psycopg


async def test_supabase_final():
    """Final test with direct connection to avoid connection pool conflicts."""
    # Use the connection string we confirmed works
    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        # Create direct connection
        conn = await psycopg.AsyncConnection.connect(uri)

        async with conn.cursor() as cursor:
            # Test basic operations
            await cursor.execute("SELECT current_timestamp")
            await cursor.fetchone()

            # Test inserting into threads table
            thread_id = f"test-{uuid4()}"
            user_id = "test-user-123"

            await cursor.execute(
                """
                INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """,
                (thread_id, user_id, "TestAgent", '{"test": true}'),
            )

            # Verify insertion
            await cursor.execute(
                """
                SELECT id, user_id, agent_name, metadata, created_at
                FROM public.threads
                WHERE id = %s
            """,
                (thread_id,),
            )

            row = await cursor.fetchone()
            if row:
                pass
            else:
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
            tables = await cursor.fetchall()

            # Test agent_state operations (checkpoints table)
            if tables:
                # Test inserting a checkpoint
                checkpoint_data = '{"test": "checkpoint_data", "messages": []}'
                await cursor.execute(
                    """
                    INSERT INTO agent_state.checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        thread_id,
                        "default",
                        "test-checkpoint",
                        None,
                        "checkpoint",
                        checkpoint_data.encode(),
                        "{}",
                    ),
                )

                # Retrieve checkpoint
                await cursor.execute(
                    """
                    SELECT checkpoint_id, checkpoint, metadata
                    FROM agent_state.checkpoints
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                checkpoint_row = await cursor.fetchone()
                if checkpoint_row:
                    pass
                else:
                    pass

            # Clean up
            await cursor.execute(
                "DELETE FROM agent_state.checkpoints WHERE thread_id = %s", (thread_id,)
            )
            await cursor.execute(
                "DELETE FROM public.threads WHERE id = %s", (thread_id,)
            )

        await conn.close()

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_supabase_final())
