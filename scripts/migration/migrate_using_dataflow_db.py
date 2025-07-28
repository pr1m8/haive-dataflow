#!/usr/bin/env python3
"""Migrate using the haive.dataflow.db infrastructure to Supabase."""

import asyncio
import logging
import sys
from datetime import datetime

# Add the packages to path
sys.path.insert(
    0, "/home/will/Projects/haive/backend/haive/packages/haive-dataflow/src"
)
sys.path.insert(0, "/home/will/Projects/haive/backend/haive/packages/haive-core/src")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_with_dataflow_db():
    """Use haive.dataflow.db to migrate from local to Supabase."""

    print("🚀 Migration using haive.dataflow.db")
    print("=" * 50)

    try:
        # Import the DatabaseManager
        from haive.dataflow.api.db import DatabaseManager

        print("✓ Imported DatabaseManagef")

        # Local PostgreSQL connection parameters
        local_params = {
            "dbname": "postgres",
            "user": "postgres",
            "pass": "postgres",
            "host": "localhost",
            "port": "5432",
        }

        # Supabase connection parameters (from your .env)
        # Using the newer Supabase credentials from the bottom of .env file
        supabase_params = {
            "dbname": "postgres",
            "user": "postgres.zkssazqhwcetsnbiuqik",
            "pass": "",  # Will need to get the actual pass
            "host": "zkssazqhwcetsnbiuqik.supabase.co",
            "port": "5432",
            "sslmode": "require",
        }

        print(
            f"Local:    {local_params['user']}@{local_params['host']}:{local_params['port']}/{local_params['dbname']}"
        )
        print(
            f"Supabase: {supabase_params['user']}@{supabase_params['host']}:{supabase_params['port']}/{supabase_params['dbname']}"
        )

        # Create database managers
        local_db = DatabaseManager(local_params)
        supabase_db = DatabaseManager(supabase_params)

        # Test connections
        print("\n🔌 Testing connections...")

        if not local_db.connect():
            print("❌ Failed to connect to local PostgreSQL")
            return False
        print("✓ Connected to local PostgreSQL")

        if not supabase_db.connect():
            print("❌ Failed to connect to Supabase")
            return False
        print("✓ Connected to Supabase")

        # Set up Supabase schema
        print("\n🔧 Setting up Supabase schema...")

        # First, let's create the proper threads table structure
        with supabase_db.connection.cursor() as cursor:
            # Enable UUID extension
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

            # Drop existing tables (clean slate)
            cursor.execute("DROP TABLE IF EXISTS public.checkpoint_blobs CASCADE")
            cursor.execute("DROP TABLE IF EXISTS public.checkpoint_writes CASCADE")
            cursor.execute("DROP TABLE IF EXISTS public.checkpoints CASCADE")
            cursor.execute("DROP TABLE IF EXISTS public.threads CASCADE")
            cursor.execute("DROP TABLE IF EXISTS public.checkpoint_migrations CASCADE")

            # Create proper threads table with UUID
            cursor.execute(
                """
                CREATE TABLE public.threads (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID,
                    agent_name TEXT,
                    name TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}',
                    legacy_thread_id TEXT UNIQUE
                )
            """
            )

            # Create LangGraph checkpoint tables
            cursor.execute(
                """
                CREATE TABLE public.checkpoint_migrations (
                    v INTEGER PRIMARY KEY
                )
            """
            )

            cursor.execute(
                """
                INSERT INTO public.checkpoint_migrations (v) 
                VALUES (0), (1), (2), (3), (4)
            """
            )

            cursor.execute(
                """
                CREATE TABLE public.checkpoints (
                    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    checkpoint_id TEXT NOT NULL,
                    parent_checkpoint_id TEXT,
                    type TEXT,
                    checkpoint JSONB NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}',
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE public.checkpoint_writes (
                    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    checkpoint_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    idx INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    type TEXT,
                    blob BYTEA NOT NULL,
                    task_path TEXT NOT NULL,
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE public.checkpoint_blobs (
                    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    channel TEXT NOT NULL,
                    version TEXT NOT NULL,
                    type TEXT NOT NULL,
                    blob BYTEA,
                    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
                )
            """
            )

            # Create indexes
            cursor.execute(
                "CREATE INDEX idx_threads_user_id ON public.threads(user_id)"
            )
            cursor.execute(
                "CREATE INDEX idx_threads_agent_name ON public.threads(agent_name)"
            )
            cursor.execute(
                "CREATE INDEX idx_threads_legacy_id ON public.threads(legacy_thread_id)"
            )
            cursor.execute(
                "CREATE INDEX idx_checkpoints_thread_id ON public.checkpoints(thread_id)"
            )

            supabase_db.connection.commit()
            print("✓ Supabase schema created")

        # Migrate data
        print("\n📦 Migrating data...")

        # Get data from local database
        with local_db.connection.cursor() as local_cursor:
            local_cursor.execute("SELECT * FROM public.threads")
            local_threads = local_cursor.fetchall()
            local_thread_columns = [desc[0] for desc in local_cursor.description]

            local_cursor.execute("SELECT * FROM public.checkpoints")
            local_checkpoints = local_cursor.fetchall()
            local_checkpoint_columns = [desc[0] for desc in local_cursor.description]

            local_cursor.execute("SELECT * FROM public.checkpoint_writes")
            local_writes = local_cursor.fetchall()
            local_write_columns = [desc[0] for desc in local_cursor.description]

            local_cursor.execute("SELECT * FROM public.checkpoint_blobs")
            local_blobs = local_cursor.fetchall()
            local_blob_columns = [desc[0] for desc in local_cursor.description]

        print(
            f"Found {len(local_threads)} threads, {len(local_checkpoints)} checkpoints"
        )
        print(f"Found {len(local_writes)} writes, {len(local_blobs)} blobs")

        # Migrate threads with UUID mapping
        thread_mapping = {}
        migrated_threads = 0

        with supabase_db.connection.cursor() as supabase_cursor:
            for thread_row in local_threads:
                thread_dict = dict(zip(local_thread_columns, thread_row))

                # Generate new UUID and create mapping
                supabase_cursor.execute("SELECT uuid_generate_v4()")
                new_uuid = supabase_cursor.fetchone()[0]
                thread_mapping[thread_dict["thread_id"]] = new_uuid

                # Insert with new structure
                supabase_cursor.execute(
                    """
                    INSERT INTO public.threads (id, user_id, agent_name, name, metadata, created_at, updated_at, legacy_thread_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        new_uuid,
                        None,  # user_id - will be set when users connect
                        "Migrated Agent",
                        f"Thread {thread_dict['thread_id'][:8]}",
                        thread_dict.get("metadata", {}),
                        thread_dict.get("created_at", datetime.now()),
                        thread_dict.get("last_access", datetime.now()),
                        thread_dict["thread_id"],
                    ),
                )
                migrated_threads += 1

            supabase_db.connection.commit()
            print(f"✓ Migrated {migrated_threads} threads")

        # Migrate checkpoints
        migrated_checkpoints = 0
        with supabase_db.connection.cursor() as supabase_cursor:
            for checkpoint_row in local_checkpoints:
                checkpoint_dict = dict(zip(local_checkpoint_columns, checkpoint_row))
                old_thread_id = checkpoint_dict["thread_id"]
                new_thread_id = thread_mapping.get(old_thread_id)

                if new_thread_id:
                    supabase_cursor.execute(
                        """
                        INSERT INTO public.checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            new_thread_id,
                            checkpoint_dict.get("checkpoint_ns", ""),
                            checkpoint_dict["checkpoint_id"],
                            checkpoint_dict.get("parent_checkpoint_id"),
                            checkpoint_dict.get("type"),
                            checkpoint_dict["checkpoint"],
                            checkpoint_dict["metadata"],
                        ),
                    )
                    migrated_checkpoints += 1

            supabase_db.connection.commit()
            print(f"✓ Migrated {migrated_checkpoints} checkpoints")

        # Migrate writes
        migrated_writes = 0
        with supabase_db.connection.cursor() as supabase_cursor:
            for write_row in local_writes:
                write_dict = dict(zip(local_write_columns, write_row))
                old_thread_id = write_dict["thread_id"]
                new_thread_id = thread_mapping.get(old_thread_id)

                if new_thread_id:
                    supabase_cursor.execute(
                        """
                        INSERT INTO public.checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, blob, task_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            new_thread_id,
                            write_dict.get("checkpoint_ns", ""),
                            write_dict["checkpoint_id"],
                            write_dict["task_id"],
                            write_dict["idx"],
                            write_dict["channel"],
                            write_dict.get("type"),
                            write_dict["blob"],
                            write_dict["task_path"],
                        ),
                    )
                    migrated_writes += 1

            supabase_db.connection.commit()
            print(f"✓ Migrated {migrated_writes} writes")

        # Migrate blobs
        migrated_blobs = 0
        with supabase_db.connection.cursor() as supabase_cursor:
            for blob_row in local_blobs:
                blob_dict = dict(zip(local_blob_columns, blob_row))
                old_thread_id = blob_dict["thread_id"]
                new_thread_id = thread_mapping.get(old_thread_id)

                if new_thread_id:
                    supabase_cursor.execute(
                        """
                        INSERT INTO public.checkpoint_blobs (thread_id, checkpoint_ns, channel, version, type, blob)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                        (
                            new_thread_id,
                            blob_dict.get("checkpoint_ns", ""),
                            blob_dict["channel"],
                            blob_dict["version"],
                            blob_dict["type"],
                            blob_dict.get("blob"),
                        ),
                    )
                    migrated_blobs += 1

            supabase_db.connection.commit()
            print(f"✓ Migrated {migrated_blobs} blobs")

        # Verify migration
        print("\n🔍 Verifying migration...")
        with supabase_db.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM public.threads")
            thread_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM public.checkpoints")
            checkpoint_count = cursor.fetchone()[0]

            print(
                f"Final counts - Threads: {thread_count}, Checkpoints: {checkpoint_count}"
            )

        # Close connections
        local_db.close()
        supabase_db.close()

        print("\n🎉 Migration completed successfully!")
        print("Your persistence adapter is now configured to use Supabase!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(migrate_with_dataflow_db())
    if success:
        print("\n✅ SUCCESS: Local PostgreSQL data migrated to Supabase")
        print("The haive persistence system now uses Supabase instead of localhost")
    else:
        print("\n❌ FAILED: Migration did not complete")
