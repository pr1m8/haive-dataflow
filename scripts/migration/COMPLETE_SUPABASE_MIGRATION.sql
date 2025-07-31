-- =================================================================
-- COMPLETE HAIVE SUPABASE MIGRATION
-- Copy and paste this entire file into your Supabase SQL Editor
-- =================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =================================================================
-- 1. HAIVE REGISTRY SYSTEM SCHEMAS (from haive-dataflow)
-- =================================================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS registry;
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS components;

-- Registry Items (core entity table)
CREATE TABLE IF NOT EXISTS registry.items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'agent', 'tool', 'engine', 'game', etc.
  description TEXT,
  module_path TEXT,
  class_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  UNIQUE (type, name)
);

-- Configurations (schema, prompts, etc.)
CREATE TABLE IF NOT EXISTS registry.configurations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  registry_id UUID REFERENCES registry.items(id) ON DELETE CASCADE,
  config_type TEXT NOT NULL, -- 'state_schema', 'input_schema', 'output_schema', 'prompt', 'engine', etc.
  config_data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Graph Definitions
CREATE TABLE IF NOT EXISTS registry.graphs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  registry_id UUID REFERENCES registry.items(id) ON DELETE CASCADE,
  nodes JSONB NOT NULL,
  edges JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Dependencies
CREATE TABLE IF NOT EXISTS registry.dependencies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  registry_id UUID REFERENCES registry.items(id) ON DELETE CASCADE,
  dependent_id UUID REFERENCES registry.items(id) ON DELETE CASCADE,
  dependency_type TEXT NOT NULL, -- 'requires', 'uses', 'extends'
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Environment Variables
CREATE TABLE IF NOT EXISTS registry.environment_vars (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  registry_id UUID REFERENCES registry.items(id) ON DELETE CASCADE,
  env_name TEXT NOT NULL,
  is_required BOOLEAN DEFAULT false,
  default_value TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Import Logs
CREATE TABLE IF NOT EXISTS registry.import_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  import_session TEXT NOT NULL,
  entity_name TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  status TEXT NOT NULL, -- 'success', 'failure'
  message TEXT,
  traceback TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Embedding Model Configuration
CREATE TABLE IF NOT EXISTS components.embedding_models (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  provider TEXT NOT NULL, -- 'azure', 'huggingface', 'openai', 'cohere'
  model_name TEXT NOT NULL,
  description TEXT,
  config_data JSONB NOT NULL,
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (provider, model_name)
);

-- LLM Model Configuration
CREATE TABLE IF NOT EXISTS components.llm_models (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  provider TEXT NOT NULL, -- 'azure', 'anthropic', 'openai', etc.
  model_name TEXT NOT NULL,
  description TEXT,
  config_data JSONB NOT NULL, 
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (provider, model_name)
);

-- Engine Templates
CREATE TABLE IF NOT EXISTS components.engine_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  engine_type TEXT NOT NULL, -- 'aug_llm', 'llm_config', etc.
  description TEXT,
  config_data JSONB NOT NULL,
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (name)
);

-- State Schema Templates
CREATE TABLE IF NOT EXISTS components.state_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  schema_type TEXT NOT NULL, -- 'agent_state', 'game_state', etc.
  description TEXT,
  schema_data JSONB NOT NULL,
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (name)
);

-- Tool Catalog
CREATE TABLE IF NOT EXISTS components.tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  tool_type TEXT NOT NULL, -- 'function', 'api', 'llm', etc.
  description TEXT,
  module_path TEXT,
  class_name TEXT,
  schema_data JSONB, -- Input/output schema
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (name)
);

-- Toolkit Catalog
CREATE TABLE IF NOT EXISTS components.toolkits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  tools JSONB NOT NULL, -- List of tool references
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (name)
);

-- =================================================================
-- 2. AGENT STATE SCHEMA (for agent streaming & persistence)
-- =================================================================

-- Create agent_state schema for agent conversations/checkpointing
CREATE SCHEMA IF NOT EXISTS agent_state;

-- Threads table for conversation/agent sessions
CREATE TABLE IF NOT EXISTS agent_state.threads (
    thread_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    agent_name TEXT,
    agent_config JSONB DEFAULT '{}'
);

-- Checkpoints table for agent state snapshots (LangGraph checkpointing)
CREATE TABLE IF NOT EXISTS agent_state.checkpoints (
    thread_id UUID NOT NULL,
    checkpoint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_checkpoint_id UUID,
    checkpoint_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (thread_id) REFERENCES agent_state.threads(thread_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_checkpoint_id) REFERENCES agent_state.checkpoints(checkpoint_id)
);

-- Conversations table for message history
CREATE TABLE IF NOT EXISTS agent_state.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL,
    message_id UUID DEFAULT uuid_generate_v4(),
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text', -- 'text', 'image', 'file', etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (thread_id) REFERENCES agent_state.threads(thread_id) ON DELETE CASCADE
);

-- Agent configurations table
CREATE TABLE IF NOT EXISTS agent_state.agent_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    config_version TEXT DEFAULT '1.0',
    config_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (agent_name, config_version)
);

-- Agent metrics for usage tracking
CREATE TABLE IF NOT EXISTS agent_state.agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL,
    agent_name TEXT NOT NULL,
    metric_type TEXT NOT NULL, -- 'message_count', 'tokens_used', 'execution_time', etc.
    metric_value NUMERIC NOT NULL,
    unit TEXT, -- 'count', 'tokens', 'milliseconds', etc.
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (thread_id) REFERENCES agent_state.threads(thread_id) ON DELETE CASCADE
);

-- =================================================================
-- 3. CREATE INDEXES for better performance
-- =================================================================

-- Registry indexes
CREATE INDEX IF NOT EXISTS idx_registry_items_type ON registry.items(type);
CREATE INDEX IF NOT EXISTS idx_configurations_registry_id ON registry.configurations(registry_id);
CREATE INDEX IF NOT EXISTS idx_configurations_type ON registry.configurations(config_type);
CREATE INDEX IF NOT EXISTS idx_graphs_registry_id ON registry.graphs(registry_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_registry_id ON registry.dependencies(registry_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_dependent_id ON registry.dependencies(dependent_id);
CREATE INDEX IF NOT EXISTS idx_env_vars_registry_id ON registry.environment_vars(registry_id);
CREATE INDEX IF NOT EXISTS idx_embedding_models_provider ON components.embedding_models(provider);
CREATE INDEX IF NOT EXISTS idx_llm_models_provider ON components.llm_models(provider);

-- Agent state indexes
CREATE INDEX IF NOT EXISTS idx_agent_threads_user_id ON agent_state.threads(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_threads_agent_name ON agent_state.threads(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_threads_created_at ON agent_state.threads(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_checkpoints_thread_id ON agent_state.checkpoints(thread_id);
CREATE INDEX IF NOT EXISTS idx_agent_checkpoints_parent ON agent_state.checkpoints(parent_checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_agent_checkpoints_created_at ON agent_state.checkpoints(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_conversations_thread_id ON agent_state.conversations(thread_id);
CREATE INDEX IF NOT EXISTS idx_agent_conversations_created_at ON agent_state.conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_conversations_role ON agent_state.conversations(role);

CREATE INDEX IF NOT EXISTS idx_agent_configs_name ON agent_state.agent_configs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_configs_active ON agent_state.agent_configs(is_active);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_thread_id ON agent_state.agent_metrics(thread_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_name ON agent_state.agent_metrics(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_type ON agent_state.agent_metrics(metric_type);

-- =================================================================
-- 4. ROW LEVEL SECURITY (RLS) for multi-tenant data isolation
-- =================================================================

-- Enable RLS on user-specific tables
ALTER TABLE agent_state.threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_state.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_state.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_state.agent_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for threads (users can only access their own threads)
CREATE POLICY "Users can only access their own threads" ON agent_state.threads
    FOR ALL USING (auth.uid() = user_id);

-- Create RLS policies for checkpoints (via thread ownership)
CREATE POLICY "Users can only access checkpoints of their threads" ON agent_state.checkpoints
    FOR ALL USING (
        thread_id IN (
            SELECT thread_id FROM agent_state.threads WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for conversations (via thread ownership)  
CREATE POLICY "Users can only access conversations of their threads" ON agent_state.conversations
    FOR ALL USING (
        thread_id IN (
            SELECT thread_id FROM agent_state.threads WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for metrics (via thread ownership)
CREATE POLICY "Users can only access metrics of their threads" ON agent_state.agent_metrics
    FOR ALL USING (
        thread_id IN (
            SELECT thread_id FROM agent_state.threads WHERE user_id = auth.uid()
        )
    );

-- =================================================================
-- 5. HELPER FUNCTIONS
-- =================================================================

-- Function to create a new agent thread
CREATE OR REPLACE FUNCTION agent_state.create_thread(
    p_user_id UUID,
    p_agent_name TEXT,
    p_agent_config JSONB DEFAULT '{}'::jsonb,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    new_thread_id UUID;
BEGIN
    INSERT INTO agent_state.threads (user_id, agent_name, agent_config, metadata)
    VALUES (p_user_id, p_agent_name, p_agent_config, p_metadata)
    RETURNING thread_id INTO new_thread_id;
    
    RETURN new_thread_id;
END;
$$;

-- Function to add a message to a conversation
CREATE OR REPLACE FUNCTION agent_state.add_message(
    p_thread_id UUID,
    p_role TEXT,
    p_content TEXT,
    p_message_type TEXT DEFAULT 'text',
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    new_message_id UUID;
BEGIN
    -- Verify thread exists and user has access
    IF NOT EXISTS (
        SELECT 1 FROM agent_state.threads 
        WHERE thread_id = p_thread_id AND user_id = auth.uid()
    ) THEN
        RAISE EXCEPTION 'Thread not found or access denied';
    END IF;
    
    INSERT INTO agent_state.conversations (thread_id, role, content, message_type, metadata)
    VALUES (p_thread_id, p_role, p_content, p_message_type, p_metadata)
    RETURNING message_id INTO new_message_id;
    
    -- Update thread timestamp
    UPDATE agent_state.threads 
    SET updated_at = NOW() 
    WHERE thread_id = p_thread_id;
    
    RETURN new_message_id;
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION agent_state.create_thread TO authenticated;
GRANT EXECUTE ON FUNCTION agent_state.add_message TO authenticated;

-- =================================================================
-- 6. INITIAL DATA (Optional)
-- =================================================================

-- Insert some default engine templates
INSERT INTO components.engine_templates (name, engine_type, description, config_data, is_default) VALUES
('Default AugLLM', 'aug_llm', 'Default augmented LLM configuration with Azure OpenAI', 
 '{"provider": "azure", "model": "gpt-4o", "temperature": 0.7}'::jsonb, true),
('Fast Response', 'aug_llm', 'Quick response configuration for real-time chat',
 '{"provider": "azure", "model": "gpt-4o-mini", "temperature": 0.3, "max_tokens": 500}'::jsonb, false)
ON CONFLICT (name) DO NOTHING;

-- Insert some default LLM models
INSERT INTO components.llm_models (provider, model_name, description, config_data, is_default) VALUES
('azure', 'gpt-4o', 'GPT-4 Omni model via Azure OpenAI', 
 '{"max_tokens": 4096, "temperature": 0.7, "top_p": 1.0}'::jsonb, true),
('azure', 'gpt-4o-mini', 'GPT-4 Omni Mini model for faster responses',
 '{"max_tokens": 2048, "temperature": 0.5, "top_p": 0.9}'::jsonb, false),
('anthropic', 'claude-3-sonnet', 'Claude 3 Sonnet by Anthropic',
 '{"max_tokens": 4096, "temperature": 0.7}'::jsonb, false)
ON CONFLICT (provider, model_name) DO NOTHING;

-- =================================================================
-- MIGRATION COMPLETE! 
-- =================================================================

-- Verify the migration
SELECT 'Registry Schema Created' as status, COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'registry';

SELECT 'Components Schema Created' as status, COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'components';

SELECT 'Agent State Schema Created' as status, COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'agent_state';

-- List all created tables
SELECT 
    table_schema as schema_name,
    table_name,
    'Created' as status
FROM information_schema.tables 
WHERE table_schema IN ('registry', 'components', 'agent_state', 'agents')
ORDER BY table_schema, table_name;