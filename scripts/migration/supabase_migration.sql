-- Supabase Migration: Convert threads table to proper UUID structure  
-- Run this in your Supabase SQL editor

-- 1. Create new threads table with proper structure
CREATE TABLE IF NOT EXISTS public.threads_new (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name TEXT,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- 2. Drop old table and rename new one (clean slate approach)
DROP TABLE IF EXISTS public.threads CASCADE;
ALTER TABLE public.threads_new RENAME TO threads;

-- 3. Update checkpoint tables to use UUID thread_id  
-- (Note: existing checkpoints will be orphaned - this is a clean migration)
ALTER TABLE public.checkpoints ALTER COLUMN thread_id TYPE UUID USING thread_id::uuid;
ALTER TABLE public.checkpoint_writes ALTER COLUMN thread_id TYPE UUID USING thread_id::uuid;
ALTER TABLE public.checkpoint_blobs ALTER COLUMN thread_id TYPE UUID USING thread_id::uuid;

-- 4. Recreate foreign key constraints
ALTER TABLE public.checkpoints 
ADD CONSTRAINT checkpoints_thread_id_fkey 
FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE;

ALTER TABLE public.checkpoint_writes
ADD CONSTRAINT checkpoint_writes_thread_id_fkey
FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE;

ALTER TABLE public.checkpoint_blobs
ADD CONSTRAINT checkpoint_blobs_thread_id_fkey
FOREIGN KEY (thread_id) REFERENCES public.threads(id) ON DELETE CASCADE;

-- 5. Create indexes
CREATE INDEX idx_threads_user_id ON public.threads(user_id);
CREATE INDEX idx_threads_agent_name ON public.threads(agent_name);
CREATE INDEX idx_threads_updated_at ON public.threads(updated_at);

-- 6. Enable RLS and create policies
ALTER TABLE public.threads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own threads"
ON public.threads
FOR ALL
USING (auth.uid() = user_id);

-- 7. Grant permissions
GRANT ALL ON public.threads TO authenticated;
EOF < /dev/null
