-- ===================================================================
-- COMPLETE SUPABASE SETUP - Run this in your Supabase SQL Editor
-- ===================================================================
-- This will create the proper schema and allow your persistence to work

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================================================
-- 1. CLEAN SLATE - Drop existing tables
-- ===================================================================
DROP TABLE IF EXISTS public.checkpoint_blobs CASCADE;
DROP TABLE IF EXISTS public.checkpoint_writes CASCADE;
DROP TABLE IF EXISTS public.checkpoints CASCADE;
DROP TABLE IF EXISTS public.threads CASCADE;
DROP TABLE IF EXISTS public.checkpoint_migrations CASCADE;

-- ===================================================================
-- 2. CREATE PROPER THREADS TABLE WITH UUID
-- ===================================================================
CREATE TABLE public.threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL DEFAULT 'Unknown Agent',
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ===================================================================
-- 3. CREATE LANGGRAPH CHECKPOINT TABLES
-- ===================================================================

-- Checkpoint migrations
CREATE TABLE public.checkpoint_migrations (
    v INTEGER PRIMARY KEY
);

INSERT INTO public.checkpoint_migrations (v) 
VALUES (0), (1), (2), (3), (4);

-- Main checkpoints table
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

-- Checkpoint writes
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

-- Checkpoint blobs
CREATE TABLE public.checkpoint_blobs (
    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- ===================================================================
-- 4. CREATE INDEXES FOR PERFORMANCE
-- ===================================================================
CREATE INDEX idx_threads_user_id ON public.threads(user_id);
CREATE INDEX idx_threads_agent_name ON public.threads(agent_name);
CREATE INDEX idx_threads_updated_at ON public.threads(updated_at DESC);
CREATE INDEX idx_threads_created_at ON public.threads(created_at DESC);

CREATE INDEX idx_checkpoints_thread_id ON public.checkpoints(thread_id);
CREATE INDEX idx_checkpoints_checkpoint_id ON public.checkpoints(checkpoint_id);
CREATE INDEX idx_checkpoints_ns_id ON public.checkpoints(checkpoint_ns, checkpoint_id);

CREATE INDEX idx_checkpoint_writes_thread_id ON public.checkpoint_writes(thread_id);
CREATE INDEX idx_checkpoint_writes_checkpoint_id ON public.checkpoint_writes(checkpoint_id);

CREATE INDEX idx_checkpoint_blobs_thread_id ON public.checkpoint_blobs(thread_id);
CREATE INDEX idx_checkpoint_blobs_channel ON public.checkpoint_blobs(channel);

-- ===================================================================
-- 5. ENABLE ROW LEVEL SECURITY
-- ===================================================================
ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_blobs ENABLE ROW LEVEL SECURITY;

-- ===================================================================
-- 6. CREATE RLS POLICIES
-- ===================================================================

-- Threads policies
CREATE POLICY "Users can view their own threads"
    ON public.threads FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own threads"
    ON public.threads FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own threads"
    ON public.threads FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own threads"
    ON public.threads FOR DELETE
    USING (auth.uid() = user_id);

-- Checkpoints policies (inherit from threads)
CREATE POLICY "Users can manage checkpoints for their threads"
    ON public.checkpoints FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.threads 
            WHERE id = checkpoints.thread_id 
            AND user_id = auth.uid()
        )
    );

-- Checkpoint writes policies
CREATE POLICY "Users can manage checkpoint_writes for their threads"
    ON public.checkpoint_writes FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.threads 
            WHERE id = checkpoint_writes.thread_id 
            AND user_id = auth.uid()
        )
    );

-- Checkpoint blobs policies
CREATE POLICY "Users can manage checkpoint_blobs for their threads"
    ON public.checkpoint_blobs FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.threads 
            WHERE id = checkpoint_blobs.thread_id 
            AND user_id = auth.uid()
        )
    );

-- ===================================================================
-- 7. CREATE UPDATED_AT TRIGGER
-- ===================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_threads_updated_at
    BEFORE UPDATE ON public.threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 8. GRANT PERMISSIONS
-- ===================================================================
GRANT ALL ON public.threads TO authenticated;
GRANT ALL ON public.checkpoints TO authenticated;
GRANT ALL ON public.checkpoint_writes TO authenticated;
GRANT ALL ON public.checkpoint_blobs TO authenticated;
GRANT ALL ON public.checkpoint_migrations TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ===================================================================
-- 9. CREATE TEST DATA (Optional - remove after testing)
-- ===================================================================
-- Uncomment to create a test thread:
/*
INSERT INTO public.threads (user_id, agent_name, name, metadata)
SELECT 
    auth.uid(),
    'TestAgent',
    'Test Thread',
    '{"test": true, "setup_complete": true}'::jsonb
WHERE auth.uid() IS NOT NULL;
*/

-- ===================================================================
-- 10. VERIFICATION
-- ===================================================================
SELECT 
    'SETUP COMPLETE!' as status,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('threads', 'checkpoints', 'checkpoint_writes', 'checkpoint_blobs')) as tables_created,
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'public' AND constraint_type = 'FOREIGN KEY') as foreign_keys_created,
    (SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public') as rls_policies_created;

-- Show the table structure
\d public.threads
\d public.checkpoints

-- Show sample of what the structure looks like
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('threads', 'checkpoints')
ORDER BY table_name, ordinal_position;