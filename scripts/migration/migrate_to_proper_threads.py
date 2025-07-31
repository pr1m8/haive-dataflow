#!/usr/bin/env python3
"""Migrate existing threads table to use proper id structure."""

import asyncio

import asyncpg


async def migrate_threads_structure():
    """Migrate threads table to use proper UUID id instead of thread_id."""
    # Get connection info
    db_config = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }

    try:
        conn = await asyncpg.connect(**db_config)

        # 1. Check current structure
        columns = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'threads'
            ORDER BY ordinal_position
        """
        )

        for col in columns:
            "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            (f" DEFAULT {col['column_default']}" if col["column_default"] else "")

        # 2. Backup existing data
        existing_threads = await conn.fetch("SELECT * FROM public.threads")

        # 3. Drop foreign key constraints temporarily

        # Get existing foreign keys that reference threads.thread_id
        fk_constraints = await conn.fetch(
            """
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'threads'
            AND ccu.column_name = 'thread_id'
        """
        )

        dropped_constraints = []
        for fk in fk_constraints:
            constraint_name = fk["constraint_name"]
            table_name = fk["table_name"]

            await conn.execute(
                f"ALTER TABLE public.{table_name} DROP CONSTRAINT {constraint_name}"
            )
            dropped_constraints.append(fk)

        # 4. Create new threads table with proper structure

        await conn.execute("DROP TABLE IF EXISTS public.threads_new")
        await conn.execute(
            """
            CREATE TABLE public.threads_new (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                agent_name TEXT,
                name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}',

                -- Keep old thread_id as a unique reference for migration
                legacy_thread_id TEXT UNIQUE
            )
        """
        )

        # 5. Migrate existing data

        for thread in existing_threads:
            # Convert thread_id to UUID for id, keep original as legacy_thread_id
            await conn.execute(
                """
                INSERT INTO public.threads_new (
                    legacy_thread_id, user_id, agent_name, created_at, updated_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
                thread["thread_id"],
                thread["user_id"],
                None,  # agent_name - extract from metadata if needed
                thread["created_at"] or "NOW()",
                thread["last_access"] or "NOW()",
                thread["metadata"] or {},
            )

        # 6. Replace old table with new one
        await conn.execute("DROP TABLE public.threads")
        await conn.execute("ALTER TABLE public.threads_new RENAME TO threads")

        # 7. Update foreign key relationships

        # First, add a mapping table to help with the migration
        await conn.execute(
            """
            CREATE TEMPORARY TABLE thread_id_mapping AS
            SELECT legacy_thread_id, id
            FROM public.threads
            WHERE legacy_thread_id IS NOT NULL
        """
        )

        # Update checkpoints table
        await conn.execute(
            """
            ALTER TABLE public.checkpoints
            ADD COLUMN thread_uuid UUID
        """
        )

        await conn.execute(
            """
            UPDATE public.checkpoints
            SET thread_uuid = mapping.id
            FROM thread_id_mapping mapping
            WHERE checkpoints.thread_id = mapping.legacy_thread_id
        """
        )

        # Update checkpoint_writes table
        await conn.execute(
            """
            ALTER TABLE public.checkpoint_writes
            ADD COLUMN thread_uuid UUID
        """
        )

        await conn.execute(
            """
            UPDATE public.checkpoint_writes
            SET thread_uuid = mapping.id
            FROM thread_id_mapping mapping
            WHERE checkpoint_writes.thread_id = mapping.legacy_thread_id
        """
        )

        # Update checkpoint_blobs table
        await conn.execute(
            """
            ALTER TABLE public.checkpoint_blobs
            ADD COLUMN thread_uuid UUID
        """
        )

        await conn.execute(
            """
            UPDATE public.checkpoint_blobs
            SET thread_uuid = mapping.id
            FROM thread_id_mapping mapping
            WHERE checkpoint_blobs.thread_id = mapping.legacy_thread_id
        """
        )

        # 8. Drop old columns and rename new ones

        await conn.execute("ALTER TABLE public.checkpoints DROP COLUMN thread_id")
        await conn.execute(
            "ALTER TABLE public.checkpoints RENAME COLUMN thread_uuid TO thread_id"
        )

        await conn.execute("ALTER TABLE public.checkpoint_writes DROP COLUMN thread_id")
        await conn.execute(
            "ALTER TABLE public.checkpoint_writes RENAME COLUMN thread_uuid TO thread_id"
        )

        await conn.execute("ALTER TABLE public.checkpoint_blobs DROP COLUMN thread_id")
        await conn.execute(
            "ALTER TABLE public.checkpoint_blobs RENAME COLUMN thread_uuid TO thread_id"
        )

        # 9. Recreate foreign key constraints

        await conn.execute(
            """
            ALTER TABLE public.checkpoints
            ADD CONSTRAINT checkpoints_thread_id_fkey
            FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE
        """
        )

        await conn.execute(
            """
            ALTER TABLE public.checkpoint_writes
            ADD CONSTRAINT checkpoint_writes_thread_id_fkey
            FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE
        """
        )

        await conn.execute(
            """
            ALTER TABLE public.checkpoint_blobs
            ADD CONSTRAINT checkpoint_blobs_thread_id_fkey
            FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE
        """
        )

        # 10. Clean up legacy column
        await conn.execute("ALTER TABLE public.threads DROP COLUMN legacy_thread_id")

        # 11. Create indexes
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_user_id ON public.threads(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_agent_name ON public.threads(agent_name)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON public.checkpoints(thread_id)"
        )

        # 12. Set up RLS policies
        await conn.execute("ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY")

        await conn.execute(
            """
            CREATE POLICY "Users can manage their own threads"
            ON public.threads
            FOR ALL
            USING (auth.uid() = user_id)
        """
        )

        await conn.close()

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def verify_migration():
    """Verify the migration was successful."""
    db_config = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }

    try:
        conn = await asyncpg.connect(**db_config)

        # Check new structure
        columns = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'threads'
            ORDER BY ordinal_position
        """
        )

        for col in columns:
            "NULL" if col["is_nullable"] == "YES" else "NOT NULL"

        # Check foreign keys
        fks = await conn.fetch(
            """
            SELECT
                tc.table_name as table_from,
                kcu.column_name as column_from,
                ccu.table_name AS table_to,
                ccu.column_name AS column_to
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'threads'
            AND tc.table_schema = 'public'
        """
        )

        for _fk in fks:
            pass

        # Count migrated data
        await conn.fetchval("SELECT COUNT(*) FROM public.threads")
        await conn.fetchval("SELECT COUNT(*) FROM public.checkpoints")

        await conn.close()
        return True

    except Exception:
        return False


async def main():
    """Run the migration."""
    # Run migration
    migration_success = await migrate_threads_structure()

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
