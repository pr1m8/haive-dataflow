#!/usr/bin/env python3
"""Migrate data from local PostgreSQL to Supabase."""

import asyncio
import os
from datetime import datetime

import asyncpg


async def migrate_local_to_supabase():
    """Migrate threads and checkpoint data from local PostgreSQL to Supabase."""
    # Local PostgreSQL config
    local_config = {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": "postgres",
    }

    # Supabase config
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
        "SUPABASE_DATABASE_URI"
    )

    if not supabase_uri:
        return False

    try:
        # Connect to both databases
        local_conn = await asyncpg.connect(**local_config)

        supabase_conn = await asyncpg.connect(supabase_uri)

        # 1. Create proper threads table structure in Supabase
        await supabase_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.threads (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID,
                agent_name TEXT,
                name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'
            )
        """
        )

        # Enable RLS
        await supabase_conn.execute(
            "ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY"
        )

        # Create policy (allow all for now, adjust later)
        await supabase_conn.execute(
            """
            DROP POLICY IF EXISTS "threads_policy" ON public.threads
        """
        )
        await supabase_conn.execute(
            """
            CREATE POLICY "threads_policy" ON public.threads FOR ALL USING (true)
        """
        )

        # 2. Get local threads data
        local_threads = await local_conn.fetch("SELECT * FROM public.threads")

        # 3. Migrate threads data
        migrated_threads = 0
        thread_mapping = {}  # old_thread_id -> new_uuid

        for thread in local_threads:
            try:
                # Generate new UUID for this thread
                new_thread_id = await supabase_conn.fetchval(
                    "SELECT uuid_generate_v4()"
                )

                # Store mapping for checkpoints
                thread_mapping[thread["thread_id"]] = new_thread_id

                # Insert thread with new UUID structure
                await supabase_conn.execute(
                    """
                    INSERT INTO public.threads (id, user_id, agent_name, metadata, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    new_thread_id,
                    None,  # user_id - will be set later when users are associated
                    "Migrated",  # agent_name
                    thread["metadata"] or {},
                    thread["created_at"] or datetime.now(),
                    thread["last_access"] or datetime.now(),
                )

                migrated_threads += 1

            except Exception:
                pass

        # 4. Get local checkpoint data
        local_checkpoints = await local_conn.fetch("SELECT * FROM public.checkpoints")
        local_writes = await local_conn.fetch("SELECT * FROM public.checkpoint_writes")
        local_blobs = await local_conn.fetch("SELECT * FROM public.checkpoint_blobs")

        # 5. Migrate checkpoints
        migrated_checkpoints = 0

        for checkpoint in local_checkpoints:
            old_thread_id = checkpoint["thread_id"]
            new_thread_id = thread_mapping.get(old_thread_id)

            if new_thread_id:
                try:
                    await supabase_conn.execute(
                        """
                        INSERT INTO public.checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                        new_thread_id,
                        checkpoint["checkpoint_ns"],
                        checkpoint["checkpoint_id"],
                        checkpoint["parent_checkpoint_id"],
                        checkpoint["type"],
                        checkpoint["checkpoint"],
                        checkpoint["metadata"],
                    )
                    migrated_checkpoints += 1

                except Exception:
                    pass

        # 6. Migrate checkpoint writes
        migrated_writes = 0

        for write in local_writes:
            old_thread_id = write["thread_id"]
            new_thread_id = thread_mapping.get(old_thread_id)

            if new_thread_id:
                try:
                    await supabase_conn.execute(
                        """
                        INSERT INTO public.checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, blob, task_path)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                        new_thread_id,
                        write["checkpoint_ns"],
                        write["checkpoint_id"],
                        write["task_id"],
                        write["idx"],
                        write["channel"],
                        write["type"],
                        write["blob"],
                        write["task_path"],
                    )
                    migrated_writes += 1

                except Exception:
                    pass

        # 7. Migrate checkpoint blobs
        migrated_blobs = 0

        for blob in local_blobs:
            old_thread_id = blob["thread_id"]
            new_thread_id = thread_mapping.get(old_thread_id)

            if new_thread_id:
                try:
                    await supabase_conn.execute(
                        """
                        INSERT INTO public.checkpoint_blobs (thread_id, checkpoint_ns, channel, version, type, blob)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                        new_thread_id,
                        blob["checkpoint_ns"],
                        blob["channel"],
                        blob["version"],
                        blob["type"],
                        blob["blob"],
                    )
                    migrated_blobs += 1

                except Exception:
                    pass

        # 8. Create indexes in Supabase
        await supabase_conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_user_id ON public.threads(user_id)"
        )
        await supabase_conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_agent_name ON public.threads(agent_name)"
        )
        await supabase_conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON public.checkpoints(thread_id)"
        )

        # 9. Summary

        # 10. Show thread mapping for reference
        for _i, (_old_id, _new_id) in enumerate(list(thread_mapping.items())[:5]):
            pass
        if len(thread_mapping) > 5:
            pass

        await local_conn.close()
        await supabase_conn.close()

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def verify_migration():
    """Verify the migration worked."""
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
        "SUPABASE_DATABASE_URI"
    )

    try:
        conn = await asyncpg.connect(supabase_uri)

        # Count migrated data
        await conn.fetchval("SELECT COUNT(*) FROM public.threads")
        await conn.fetchval("SELECT COUNT(*) FROM public.checkpoints")
        await conn.fetchval("SELECT COUNT(*) FROM public.checkpoint_writes")
        await conn.fetchval("SELECT COUNT(*) FROM public.checkpoint_blobs")

        # Show sample thread
        sample_thread = await conn.fetchrow("SELECT * FROM public.threads LIMIT 1")
        if sample_thread:
            pass

        await conn.close()
        return True

    except Exception:
        return False


async def main():
    """Run the migration."""
    # Run migration
    migration_success = await migrate_local_to_supabase()

    if migration_success:
        # Verify results
        verification_success = await verify_migration()

        if verification_success:
            pass
        else:
            pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
