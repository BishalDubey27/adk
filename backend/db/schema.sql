-- Tech Sarathi Database Schema
-- PostgreSQL 15 + pgvector extension for AlloyDB AI
-- Compatible with both local PostgreSQL (via pgvector/pgvector image) and AlloyDB

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Team members with skill embeddings for vector search
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT,
    skills TEXT[],
    skill_embedding vector(768),
    availability_hours_per_week INT DEFAULT 40,
    current_load_hours INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'medium',
    start_date DATE,
    deadline DATE,
    pm_id UUID REFERENCES team_members(id),
    confidence_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tasks with optional embedding for task-to-task similarity
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    assigned_to UUID REFERENCES team_members(id),
    estimated_hours INT,
    actual_hours INT,
    due_date DATE,
    dependencies UUID[],
    risk_score FLOAT DEFAULT 0.0,
    task_embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Escalation queue
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    agent_name TEXT NOT NULL,
    reason TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    suggested_action JSONB,
    status TEXT DEFAULT 'pending',
    reviewed_by UUID REFERENCES team_members(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Full audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    input_data JSONB,
    output_data JSONB,
    confidence_score FLOAT,
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Standard B-tree indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_project_status ON tasks (project_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_status ON tasks (assigned_to, status);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_agent ON audit_log (agent_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_team_members_email ON team_members (email);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status);

-- Vector indexes for similarity search (pgvector)
-- HNSW: better recall, works well with small-to-medium datasets
-- Use this as the primary index for skill matching
CREATE INDEX IF NOT EXISTS idx_team_skill_embedding_hnsw ON team_members
USING hnsw (skill_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Task embedding index for future task-to-task similarity features
CREATE INDEX IF NOT EXISTS idx_task_embedding_hnsw ON tasks
USING hnsw (task_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DO $$
BEGIN
    -- Drop existing triggers if they exist, then recreate
    DROP TRIGGER IF EXISTS update_team_members_updated_at ON team_members;
    CREATE TRIGGER update_team_members_updated_at BEFORE UPDATE ON team_members
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
    CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
    CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
END;
$$;
