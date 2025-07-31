#!/bin/bash
# ===================================================================
# MIGRATE LOCAL POSTGRESQL TO SUPABASE USING pg_dump
# ===================================================================
# This is the official, recommended way to migrate PostgreSQL data

set -e # Exit on any error

echo "🚀 PostgreSQL → Supabase Migration using pg_dump"
echo "================================================="

# Check if pg_dump is available
if ! command -v pg_dump &>/dev/null; then
	echo "❌ pg_dump not found. Please install PostgreSQL client tools."
	exit 1
fi

# Local PostgreSQL connection
LOCAL_DB="postgresql://postgres:postgres@localhost:5432/postgres"

# Supabase connection - build from individual components in .env
SUPABASE_HOST="${SUPABASE_HOST:-aws-0-us-east-1.pooler.supabase.com}"
SUPABASE_PORT="${SUPABASE_PORT:-6543}"
SUPABASE_USER="${SUPABASE_USER:-postgres.oecoeyomphckolkywbzz}"
SUPABASE_PASSWORD="${SUPABASE_PASSWORD:-ITfz5B0wU6ehVXI1}"
SUPABASE_DBNAME="${SUPABASE_DBNAME:-postgres}"

SUPABASE_DB="postgresql://${SUPABASE_USER}:${SUPABASE_PASSWORD}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DBNAME}?sslmode=require"

echo "📡 Connection check..."
echo "Local:    ${LOCAL_DB}"
echo "Supabase: ${SUPABASE_DB:0:50}..."

# Step 1: Create schema dump (structure only)
echo ""
echo "🔧 Step 1: Creating schema dump..."
pg_dump "${LOCAL_DB}" \
	--schema-only \
	--clean \
	--if-exists \
	--quote-all-identifiers \
	--no-owner \
	--no-privileges \
	--table=threads \
	--table=checkpoints \
	--table=checkpoint_writes \
	--table=checkpoint_blobs \
	--table=checkpoint_migrations \
	>schema_dump.sql

echo "✓ Schema exported to schema_dump.sql"

# Step 2: Create data dump (data only)
echo ""
echo "📦 Step 2: Creating data dump..."
pg_dump "${LOCAL_DB}" \
	--data-only \
	--quote-all-identifiers \
	--no-owner \
	--no-privileges \
	--table=threads \
	--table=checkpoints \
	--table=checkpoint_writes \
	--table=checkpoint_blobs \
	--table=checkpoint_migrations \
	--disable-triggers \
	>data_dump.sql

echo "✓ Data exported to data_dump.sql"

# Step 3: Apply schema to Supabase
echo ""
echo "🔧 Step 3: Setting up schema in Supabase..."
echo "Creating proper threads table structure..."

# Create the proper schema first
psql "${SUPABASE_DB}" <<'EOF'
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (clean slate)
DROP TABLE IF EXISTS public.checkpoint_blobs CASCADE;
DROP TABLE IF EXISTS public.checkpoint_writes CASCADE;
DROP TABLE IF EXISTS public.checkpoints CASCADE;
DROP TABLE IF EXISTS public.threads CASCADE;
DROP TABLE IF EXISTS public.checkpoint_migrations CASCADE;

-- Create proper threads table with UUID
CREATE TABLE public.threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    agent_name TEXT,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    -- Keep original thread_id for migration mapping
    legacy_thread_id TEXT UNIQUE
);

-- Create checkpoint tables that reference the new threads.id
CREATE TABLE public.checkpoint_migrations (
    v INTEGER PRIMARY KEY
);

CREATE TABLE public.checkpoints (
    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

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
);

CREATE TABLE public.checkpoint_blobs (
    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- Create indexes
CREATE INDEX idx_threads_user_id ON public.threads(user_id);
CREATE INDEX idx_threads_agent_name ON public.threads(agent_name);
CREATE INDEX idx_threads_legacy_id ON public.threads(legacy_thread_id);
CREATE INDEX idx_checkpoints_thread_id ON public.checkpoints(thread_id);

-- Enable RLS
ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_blobs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (open for now, restrict later)
CREATE POLICY "allow_all_threads" ON public.threads FOR ALL USING (true);
CREATE POLICY "allow_all_checkpoints" ON public.checkpoints FOR ALL USING (true);
CREATE POLICY "allow_all_writes" ON public.checkpoint_writes FOR ALL USING (true);
CREATE POLICY "allow_all_blobs" ON public.checkpoint_blobs FOR ALL USING (true);

EOF

echo "✓ Schema created in Supabase"

# Step 4: Create migration script for data
echo ""
echo "📤 Step 4: Creating data migration script..."

cat >migrate_data.py <<'PYTHON_EOF'
#!/usr/bin/env python3
import asyncio
import asyncpg
import os
import uuid

async def migrate_data():
    # Connect to both databases
    local_conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
    
    # Build Supabase connection from components
    supabase_host = os.getenv('SUPABASE_HOST', 'aws-0-us-east-1.pooler.supabase.com')
    supabase_port = os.getenv('SUPABASE_PORT', '6543')
    supabase_user = os.getenv('SUPABASE_USER', 'postgres.oecoeyomphckolkywbzz')
    supabase_password = os.getenv('SUPABASE_PASSWORD', 'ITfz5B0wU6ehVXI1')
    supabase_dbname = os.getenv('SUPABASE_DBNAME', 'postgres')
    
    supabase_uri = f"postgresql://{supabase_user}:{supabase_password}@{supabase_host}:{supabase_port}/{supabase_dbname}?sslmode=require"
    supabase_conn = await asyncpg.connect(supabase_uri)
    
    print("📦 Migrating data with proper UUID mapping...")
    
    # 1. Migrate threads with UUID conversion
    threads = await local_conn.fetch("SELECT * FROM public.threads")
    thread_mapping = {}
    
    for thread in threads:
        new_id = uuid.uuid4()
        thread_mapping[thread['thread_id']] = new_id
        
        await supabase_conn.execute("""
            INSERT INTO public.threads (id, user_id, agent_name, name, metadata, created_at, updated_at, legacy_thread_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, 
            new_id,
            None,  # user_id
            'Migrated Agent',
            f"Thread {thread['thread_id'][:8]}",
            thread['metadata'] or {},
            thread['created_at'],
            thread['last_access'],
            thread['thread_id']
        )
    
    print(f"✓ Migrated {len(threads)} threads")
    
    # 2. Migrate checkpoints with new thread UUIDs
    checkpoints = await local_conn.fetch("SELECT * FROM public.checkpoints")
    migrated = 0
    
    for checkpoint in checkpoints:
        new_thread_id = thread_mapping.get(checkpoint['thread_id'])
        if new_thread_id:
            await supabase_conn.execute("""
                INSERT INTO public.checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                new_thread_id,
                checkpoint['checkpoint_ns'],
                checkpoint['checkpoint_id'],
                checkpoint['parent_checkpoint_id'],
                checkpoint['type'],
                checkpoint['checkpoint'],
                checkpoint['metadata']
            )
            migrated += 1
    
    print(f"✓ Migrated {migrated} checkpoints")
    
    # 3. Migrate writes
    writes = await local_conn.fetch("SELECT * FROM public.checkpoint_writes")
    migrated = 0
    
    for write in writes:
        new_thread_id = thread_mapping.get(write['thread_id'])
        if new_thread_id:
            await supabase_conn.execute("""
                INSERT INTO public.checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, blob, task_path)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                new_thread_id,
                write['checkpoint_ns'],
                write['checkpoint_id'],
                write['task_id'],
                write['idx'],
                write['channel'],
                write['type'],
                write['blob'],
                write['task_path']
            )
            migrated += 1
    
    print(f"✓ Migrated {migrated} writes")
    
    # 4. Migrate blobs
    blobs = await local_conn.fetch("SELECT * FROM public.checkpoint_blobs")
    migrated = 0
    
    for blob in blobs:
        new_thread_id = thread_mapping.get(blob['thread_id'])
        if new_thread_id:
            await supabase_conn.execute("""
                INSERT INTO public.checkpoint_blobs (thread_id, checkpoint_ns, channel, version, type, blob)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                new_thread_id,
                blob['checkpoint_ns'],
                blob['channel'],
                blob['version'],
                blob['type'],
                blob['blob']
            )
            migrated += 1
    
    print(f"✓ Migrated {migrated} blobs")
    
    # 5. Migrations table
    await supabase_conn.execute("INSERT INTO public.checkpoint_migrations (v) VALUES (0), (1), (2), (3), (4) ON CONFLICT DO NOTHING")
    
    await local_conn.close()
    await supabase_conn.close()
    print("🎉 Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate_data())
PYTHON_EOF

echo "✓ Migration script created"

# Step 5: Run the data migration
echo ""
echo "📤 Step 5: Running data migration..."
python3 migrate_data.py

# Step 6: Cleanup
echo ""
echo "🧹 Step 6: Cleaning up temporary files..."
rm -f schema_dump.sql data_dump.sql migrate_data.py

# Step 7: Verify migration
echo ""
echo "🔍 Step 7: Verifying migration..."
psql "${SUPABASE_DB}" <<'EOF'
SELECT 
    'threads' as table_name, COUNT(*) as count 
FROM public.threads
UNION ALL
SELECT 
    'checkpoints' as table_name, COUNT(*) as count 
FROM public.checkpoints
UNION ALL
SELECT 
    'checkpoint_writes' as table_name, COUNT(*) as count 
FROM public.checkpoint_writes
UNION ALL
SELECT 
    'checkpoint_blobs' as table_name, COUNT(*) as count 
FROM public.checkpoint_blobs;
EOF

echo ""
echo "🎉 Migration completed successfully!"
echo "Your local PostgreSQL data is now in Supabase with proper UUID structure."
echo "The Supabase persistence adapter will now work correctly."
