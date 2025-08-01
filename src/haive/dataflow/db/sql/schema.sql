-- Haive Registry System Schema Definitions
-- For Supabase PostgreSQL Database

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_registry_items_type ON registry.items(type);
CREATE INDEX IF NOT EXISTS idx_configurations_registry_id ON registry.configurations(registry_id);
CREATE INDEX IF NOT EXISTS idx_configurations_type ON registry.configurations(config_type);
CREATE INDEX IF NOT EXISTS idx_graphs_registry_id ON registry.graphs(registry_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_registry_id ON registry.dependencies(registry_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_dependent_id ON registry.dependencies(dependent_id);
CREATE INDEX IF NOT EXISTS idx_env_vars_registry_id ON registry.environment_vars(registry_id);
CREATE INDEX IF NOT EXISTS idx_embedding_models_provider ON components.embedding_models(provider);
CREATE INDEX IF NOT EXISTS idx_llm_models_provider ON components.llm_models(provider);
