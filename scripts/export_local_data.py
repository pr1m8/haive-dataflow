#!/usr/bin/env python3
"""Export local PostgreSQL data to JSON for Supabase import."""

import asyncio
import json
import uuid
from datetime import datetime

import asyncpg


async def export_local_data():
    """Export all local PostgreSQL data to JSON files."""
    # Local PostgreSQL config
    local_config = {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": "postgres",
    }

    try:
        conn = await asyncpg.connect(**local_config)

        # 1. Export threads
        threads = await conn.fetch("SELECT * FROM public.threads")

        # Convert to proper format with UUID mapping
        threads_data = []
        thread_mapping = {}  # old_thread_id -> new_uuid

        for thread in threads:
            new_uuid = str(uuid.uuid4())
            thread_mapping[thread["thread_id"]] = new_uuid

            # Handle metadata properly (it might already be a dict)
            metadata = thread["metadata"]
            if metadata is None:
                metadata = {}
            elif isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            elif not isinstance(metadata, dict):
                metadata = {}

            threads_data.append(
                {
                    "id": new_uuid,
                    "user_id": None,  # Will be set when user associates
                    "agent_name": "Migrated Agent",
                    "name": f"Migrated Thread {thread['thread_id'][:8]}",
                    "metadata": metadata,
                    "created_at": (
                        thread["created_at"].isoformat()
                        if thread["created_at"]
                        else datetime.now().isoformat()
                    ),
                    "updated_at": (
                        thread["last_access"].isoformat()
                        if thread["last_access"]
                        else datetime.now().isoformat()
                    ),
                    "original_thread_id": thread["thread_id"],  # Keep for reference
                }
            )

        # 2. Export checkpoints
        checkpoints = await conn.fetch("SELECT * FROM public.checkpoints")

        checkpoints_data = []
        for checkpoint in checkpoints:
            new_thread_id = thread_mapping.get(checkpoint["thread_id"])
            if new_thread_id:
                # Handle checkpoint data
                checkpoint_data = checkpoint["checkpoint"]
                if checkpoint_data is None or not isinstance(checkpoint_data, dict):
                    checkpoint_data = {}

                # Handle metadata
                metadata = checkpoint["metadata"]
                if metadata is None or not isinstance(metadata, dict):
                    metadata = {}

                checkpoints_data.append(
                    {
                        "thread_id": new_thread_id,
                        "checkpoint_ns": checkpoint["checkpoint_ns"] or "",
                        "checkpoint_id": checkpoint["checkpoint_id"],
                        "parent_checkpoint_id": checkpoint["parent_checkpoint_id"],
                        "type": checkpoint["type"],
                        "checkpoint": checkpoint_data,
                        "metadata": metadata,
                    }
                )

        # 3. Export checkpoint writes
        writes = await conn.fetch("SELECT * FROM public.checkpoint_writes")

        writes_data = []
        for write in writes:
            new_thread_id = thread_mapping.get(write["thread_id"])
            if new_thread_id:
                writes_data.append(
                    {
                        "thread_id": new_thread_id,
                        "checkpoint_ns": write["checkpoint_ns"] or "",
                        "checkpoint_id": write["checkpoint_id"],
                        "task_id": write["task_id"],
                        "idx": write["idx"],
                        "channel": write["channel"],
                        "type": write["type"],
                        "blob": (
                            write["blob"].hex() if write["blob"] else None
                        ),  # Convert binary to hex
                        "task_path": write["task_path"],
                    }
                )

        # 4. Export checkpoint blobs
        blobs = await conn.fetch("SELECT * FROM public.checkpoint_blobs")

        blobs_data = []
        for blob in blobs:
            new_thread_id = thread_mapping.get(blob["thread_id"])
            if new_thread_id:
                blobs_data.append(
                    {
                        "thread_id": new_thread_id,
                        "checkpoint_ns": blob["checkpoint_ns"] or "",
                        "channel": blob["channel"],
                        "version": blob["version"],
                        "type": blob["type"],
                        "blob": (
                            blob["blob"].hex() if blob["blob"] else None
                        ),  # Convert binary to hex
                    }
                )

        # 5. Save all data to JSON files
        export_data = {
            "threads": threads_data,
            "checkpoints": checkpoints_data,
            "checkpoint_writes": writes_data,
            "checkpoint_blobs": blobs_data,
            "thread_mapping": thread_mapping,
            "export_timestamp": datetime.now().isoformat(),
            "total_records": {
                "threads": len(threads_data),
                "checkpoints": len(checkpoints_data),
                "writes": len(writes_data),
                "blobs": len(blobs_data),
            },
        }

        # Save to file
        with open("local_postgres_export.json", "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        # 6. Create individual SQL insert files for Supabase

        # Threads SQL
        with open("supabase_import_threads.sql", "w") as f:
            f.write("-- Import threads into Supabase\n")
            for thread in threads_data:
                f.write(
                    f"""
INSERT INTO public.threads (id, user_id, agent_name, name, metadata, created_at, updated_at)
VALUES (
    '{thread['id']}'::uuid,
    NULL,
    '{thread['agent_name']}',
    '{thread['name']}',
    '{json.dumps(thread['metadata'])}'::jsonb,
    '{thread['created_at']}'::timestamptz,
    '{thread['updated_at']}'::timestamptz
);
"""
                )

        # Summary

        await conn.close()
        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the export."""
    success = await export_local_data()

    if success:
        pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
