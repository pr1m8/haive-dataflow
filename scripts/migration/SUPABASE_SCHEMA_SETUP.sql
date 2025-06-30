-- ===================================================================
-- SUPABASE SCHEMA SETUP FOR HAIVE PERSISTENCE
-- ===================================================================
-- Copy and paste this into your Supabase SQL Editor and run it
-- This creates the proper schema for frontend integration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================================================
-- 1. THREADS TABLE (Main conversation threads)
-- ===================================================================
CREATE TABLE IF NOT EXISTS public.threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ===================================================================
-- 2. LANGGRAPH CHECKPOINT TABLES (Required for agent state persistence)
-- ===================================================================

-- Checkpoint migrations table
CREATE TABLE IF NOT EXISTS public.checkpoint_migrations (
    v INTEGER PRIMARY KEY
);

-- Insert migration versions if not exists
INSERT INTO public.checkpoint_migrations (v) 
VALUES (0), (1), (2), (3), (4)
ON CONFLICT (v) DO NOTHING;

-- Main checkpoints table
CREATE TABLE IF NOT EXISTS public.checkpoints (
    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- Checkpoint writes table
CREATE TABLE IF NOT EXISTS public.checkpoint_writes (
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

-- Checkpoint blobs table
CREATE TABLE IF NOT EXISTS public.checkpoint_blobs (
    thread_id UUID NOT NULL REFERENCES public.threads(id) ON DELETE CASCADE,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- ===================================================================
-- 3. INDEXES FOR PERFORMANCE
-- ===================================================================
CREATE INDEX IF NOT EXISTS idx_threads_user_id ON public.threads(user_id);
CREATE INDEX IF NOT EXISTS idx_threads_agent_name ON public.threads(agent_name);
CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON public.threads(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_threads_created_at ON public.threads(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON public.checkpoints(thread_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_checkpoint_id ON public.checkpoints(checkpoint_id);

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_id ON public.checkpoint_writes(thread_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_checkpoint_id ON public.checkpoint_writes(checkpoint_id);

CREATE INDEX IF NOT EXISTS idx_checkpoint_blobs_thread_id ON public.checkpoint_blobs(thread_id);

-- ===================================================================
-- 4. ROW LEVEL SECURITY (RLS) POLICIES
-- ===================================================================

-- Enable RLS on all tables
ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkpoint_blobs ENABLE ROW LEVEL SECURITY;

-- Threads policies
DROP POLICY IF EXISTS "Users can view their own threads" ON public.threads;
DROP POLICY IF EXISTS "Users can insert their own threads" ON public.threads;
DROP POLICY IF EXISTS "Users can update their own threads" ON public.threads;
DROP POLICY IF EXISTS "Users can delete their own threads" ON public.threads;

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

-- Checkpoints policies (inherit from threads via foreign key)
DROP POLICY IF EXISTS "Users can manage checkpoints for their threads" ON public.checkpoints;
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
DROP POLICY IF EXISTS "Users can manage checkpoint_writes for their threads" ON public.checkpoint_writes;
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
DROP POLICY IF EXISTS "Users can manage checkpoint_blobs for their threads" ON public.checkpoint_blobs;
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
-- 5. FUNCTIONS AND TRIGGERS
-- ===================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on threads
DROP TRIGGER IF EXISTS update_threads_updated_at ON public.threads;
CREATE TRIGGER update_threads_updated_at
    BEFORE UPDATE ON public.threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 6. GRANTS AND PERMISSIONS
-- ===================================================================

-- Grant permissions to authenticated users
GRANT ALL ON public.threads TO authenticated;
GRANT ALL ON public.checkpoints TO authenticated;
GRANT ALL ON public.checkpoint_writes TO authenticated;
GRANT ALL ON public.checkpoint_blobs TO authenticated;
GRANT ALL ON public.checkpoint_migrations TO authenticated;

-- Grant usage on sequences (if any)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ===================================================================
-- 7. HELPER VIEWS FOR FRONTEND (Optional)
-- ===================================================================

-- View to get thread with latest message preview
CREATE OR REPLACE VIEW public.threads_with_preview AS
SELECT 
    t.id,
    t.user_id,
    t.agent_name,
    t.name,
    t.created_at,
    t.updated_at,
    t.metadata,
    -- Extract latest message from most recent checkpoint
    (
        SELECT 
            CASE 
                WHEN c.checkpoint->'channel_values'->'messages' IS NOT NULL 
                THEN (c.checkpoint->'channel_values'->'messages'->-1)
                ELSE NULL
            END
        FROM public.checkpoints c
        WHERE c.thread_id = t.id
        ORDER BY c.checkpoint->>'ts' DESC
        LIMIT 1
    ) as latest_message
FROM public.threads t;

-- Grant access to view
GRANT SELECT ON public.threads_with_preview TO authenticated;

-- ===================================================================
-- SETUP COMPLETE
-- ===================================================================

-- Insert a test thread to verify everything works
-- (Remove this after testing)
/*
INSERT INTO public.threads (user_id, agent_name, name, metadata)
VALUES (
    auth.uid(),
    'TestAgent',
    'Test Thread',
    '{"test": true, "setup": "complete"}'
);
*/

-- Verify the setup
SELECT 
    'Setup Complete!' as status,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('threads', 'checkpoints', 'checkpoint_writes', 'checkpoint_blobs');