#!/usr/bin/env python3
"""Check what's in the public schema and create proper thread tables if needed."""

import asyncio
import contextlib
import os

import asyncpg


async def check_public_schema():
    """Check existing tables in public schema."""
    # Get connection string
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
        "SUPABASE_DATABASE_URI"
    )

    if not supabase_uri:
        return False

    try:
        conn = await asyncpg.connect(supabase_uri)

        # Check public schema tables
        public_tables = await conn.fetch(
            """
            SELECT table_name,
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        )

        for table in public_tables:
            table_name = table["table_name"]
            table["column_count"]

            # Get row count
            with contextlib.suppress(Exception):
                await conn.fetchval(f"SELECT COUNT(*) FROM public.{table_name}")

        # Check for threads table specifically
        threads_table = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'threads'
            ORDER BY ordinal_position
        """
        )

        if threads_table:
            for col in threads_table:
                "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
        else:
            pass

        # Check foreign key relationships
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
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """
        )

        if fks:
            for _fk in fks:
                pass
        else:
            pass

        await conn.close()
        return True

    except Exception:
        return False


async def create_public_thread_tables():
    """Create proper thread tables in public schema."""
    supabase_uri = os.getenv("SUPABASE_DATABASE_URI_SSL") or os.getenv(
        "SUPABASE_DATABASE_URI"
    )

    try:
        conn = await asyncpg.connect(supabase_uri)

        # Create threads table in public schema with proper relationships
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.threads (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL,
                agent_name TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}',
                CONSTRAINT threads_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
            );
        """
        )

        # Create thread_messages table for conversation history
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.thread_messages (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                thread_id UUID NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}',
                CONSTRAINT thread_messages_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE
            );
        """
        )

        # Create thread_checkpoints for LangGraph state
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.thread_checkpoints (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                thread_id UUID NOT NULL,
                checkpoint_id TEXT NOT NULL,
                parent_checkpoint_id TEXT,
                type TEXT DEFAULT 'standard',
                checkpoint JSONB NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT thread_checkpoints_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE,
                UNIQUE(thread_id, checkpoint_id)
            );
        """
        )

        # Create indexes for performance
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_user_id ON public.threads(user_id);"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_threads_agent_name ON public.threads(agent_name);"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_thread_messages_thread_id ON public.thread_messages(thread_id);"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_thread_checkpoints_thread_id ON public.thread_checkpoints(thread_id);"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_thread_checkpoints_checkpoint_id ON public.thread_checkpoints(checkpoint_id);"
        )

        # Set up RLS policies
        await conn.execute("ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;")
        await conn.execute(
            "ALTER TABLE public.thread_messages ENABLE ROW LEVEL SECURITY;"
        )
        await conn.execute(
            "ALTER TABLE public.thread_checkpoints ENABLE ROW LEVEL SECURITY;"
        )

        # Threads policy
        await conn.execute(
            """
            CREATE POLICY IF NOT EXISTS "Users can manage their own threads"
            ON public.threads
            FOR ALL
            USING (auth.uid() = user_id);
        """
        )

        # Messages policy
        await conn.execute(
            """
            CREATE POLICY IF NOT EXISTS "Users can manage messages in their threads"
            ON public.thread_messages
            FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.threads
                WHERE id = thread_messages.thread_id
                AND user_id = auth.uid()
            ));
        """
        )

        # Checkpoints policy
        await conn.execute(
            """
            CREATE POLICY IF NOT EXISTS "Users can manage checkpoints in their threads"
            ON public.thread_checkpoints
            FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.threads
                WHERE id = thread_checkpoints.thread_id
                AND user_id = auth.uid()
            ));
        """
        )

        await conn.close()
        return True

    except Exception:
        return False


async def main():
    """Check schema and create tables if needed."""
    # Check current state
    check_success = await check_public_schema()

    if check_success:
        # Create/update tables
        create_success = await create_public_thread_tables()

        if create_success:
            # Check again to show final state
            await check_public_schema()


if __name__ == "__main__":
    asyncio.run(main())
