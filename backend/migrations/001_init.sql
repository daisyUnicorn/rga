-- Phone Agent Web Platform Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Sessions table: stores cloud phone sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    agentbay_session_id TEXT,
    resource_url TEXT,
    device_id TEXT,
    status TEXT NOT NULL DEFAULT 'creating' CHECK (status IN ('creating', 'active', 'paused', 'closed', 'error')),
    name TEXT,
    agent_type TEXT DEFAULT 'glm' CHECK (agent_type IN ('glm', 'gelab')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conversations table: stores chat history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    thinking TEXT,
    action JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_type ON sessions(agent_type);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sessions
-- Users can only see their own sessions
CREATE POLICY "Users can view own sessions" ON sessions
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own sessions
CREATE POLICY "Users can create own sessions" ON sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own sessions
CREATE POLICY "Users can update own sessions" ON sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own sessions
CREATE POLICY "Users can delete own sessions" ON sessions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for conversations
-- Users can view conversations of their sessions
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM sessions
            WHERE sessions.id = conversations.session_id
            AND sessions.user_id = auth.uid()
        )
    );

-- Users can create conversations in their sessions
CREATE POLICY "Users can create own conversations" ON conversations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM sessions
            WHERE sessions.id = conversations.session_id
            AND sessions.user_id = auth.uid()
        )
    );

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on sessions
DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (for service role access)
GRANT ALL ON sessions TO service_role;
GRANT ALL ON conversations TO service_role;
GRANT ALL ON sessions TO authenticated;
GRANT ALL ON conversations TO authenticated;
