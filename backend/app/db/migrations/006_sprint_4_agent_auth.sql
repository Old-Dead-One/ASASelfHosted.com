-- ASASelfHosted.com - Sprint 4 Agent Authentication & Heartbeat Pipeline
-- This migration adds agent authentication, heartbeat fields, and durable worker queue
-- Run this in Supabase SQL Editor after 001_sprint_0_schema.sql and 003_sprint_3_directory_view.sql

-- ============================================================================
-- CLUSTERS TABLE EXTENSIONS
-- ============================================================================

-- Add Ed25519 public key for signature verification
-- public_fingerprint remains as identifier only (not used for verification)
DO $$ BEGIN
    ALTER TABLE clusters ADD COLUMN public_key_ed25519 TEXT;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Add per-cluster grace window override (optional, falls back to env default)
DO $$ BEGIN
    ALTER TABLE clusters ADD COLUMN heartbeat_grace_seconds INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

COMMENT ON COLUMN clusters.public_key_ed25519 IS 'Base64-encoded Ed25519 public key for agent signature verification';
COMMENT ON COLUMN clusters.heartbeat_grace_seconds IS 'Per-cluster grace window override (seconds). Falls back to env default if NULL.';
COMMENT ON COLUMN clusters.public_fingerprint IS 'Identifier/fingerprint only (not used for signature verification)';

-- ============================================================================
-- HEARTBEATS TABLE EXTENSIONS (ADD ONLY - NO RENAMES)
-- ============================================================================

-- Add key_version for key rotation tracking
DO $$ BEGIN
    ALTER TABLE heartbeats ADD COLUMN key_version INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Add heartbeat_id for replay protection (UUID)
DO $$ BEGIN
    ALTER TABLE heartbeats ADD COLUMN heartbeat_id UUID;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Add canonical player fields (keep legacy player_count, max_players for compatibility)
DO $$ BEGIN
    ALTER TABLE heartbeats ADD COLUMN players_current INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE heartbeats ADD COLUMN players_capacity INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Replay protection: unique constraint on (server_id, heartbeat_id)
-- This prevents duplicate heartbeat_id per server (replay attacks)
-- Note: heartbeat_id may be NULL for legacy heartbeats, but agents should always send it
DO $$ BEGIN
    ALTER TABLE heartbeats ADD CONSTRAINT uq_heartbeats_server_heartbeat_id 
        UNIQUE(server_id, heartbeat_id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON COLUMN heartbeats.key_version IS 'Key version used for signature (matches clusters.key_version)';
COMMENT ON COLUMN heartbeats.heartbeat_id IS 'UUID for replay protection (unique per server_id)';
COMMENT ON COLUMN heartbeats.players_current IS 'Canonical field: current player count (legacy player_count kept for compatibility)';
COMMENT ON COLUMN heartbeats.players_capacity IS 'Canonical field: player capacity (legacy max_players kept for compatibility)';

-- ============================================================================
-- SERVERS TABLE EXTENSIONS
-- ============================================================================

-- Add last_heartbeat_at (agent-reported timestamp, distinct from last_seen_at which is received_at)
DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN last_heartbeat_at TIMESTAMPTZ;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

COMMENT ON COLUMN servers.last_heartbeat_at IS 'Agent-reported timestamp from heartbeat (distinct from last_seen_at which is received_at)';

-- ============================================================================
-- HEARTBEAT JOBS TABLE (Durable Queue)
-- ============================================================================

-- Create heartbeat_jobs table for durable worker queue
CREATE TABLE IF NOT EXISTS heartbeat_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    enqueued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    claimed_at TIMESTAMPTZ NULL,  -- Row-level claiming: set when worker claims job
    processed_at TIMESTAMPTZ NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial unique constraint: one pending job per server
-- This ensures we don't enqueue duplicate jobs for the same server
DO $$ BEGIN
    CREATE UNIQUE INDEX idx_heartbeat_jobs_pending_unique 
        ON heartbeat_jobs(server_id) 
        WHERE processed_at IS NULL;
EXCEPTION
    WHEN duplicate_table THEN null;
END $$;

COMMENT ON TABLE heartbeat_jobs IS 'Durable queue for heartbeat processing jobs. One pending job per server.';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for heartbeat_id lookups (replay detection)
CREATE INDEX IF NOT EXISTS idx_heartbeats_heartbeat_id 
    ON heartbeats(heartbeat_id) 
    WHERE heartbeat_id IS NOT NULL;

-- Index for cluster grace window lookups
CREATE INDEX IF NOT EXISTS idx_clusters_heartbeat_grace 
    ON clusters(heartbeat_grace_seconds) 
    WHERE heartbeat_grace_seconds IS NOT NULL;

-- Index for worker polling (unclaimed pending jobs ordered by enqueued_at)
CREATE INDEX IF NOT EXISTS idx_heartbeat_jobs_pending 
    ON heartbeat_jobs(processed_at, enqueued_at) 
    WHERE processed_at IS NULL AND claimed_at IS NULL;

-- Index for claimed jobs (for monitoring/debugging)
CREATE INDEX IF NOT EXISTS idx_heartbeat_jobs_claimed 
    ON heartbeat_jobs(claimed_at) 
    WHERE claimed_at IS NOT NULL AND processed_at IS NULL;

-- Keep existing index (already in Sprint 0)
-- idx_heartbeats_server_received on (server_id, received_at DESC)

-- ============================================================================
-- RLS POLICIES FOR HEARTBEAT_JOBS
-- ============================================================================

-- Enable RLS
ALTER TABLE heartbeat_jobs ENABLE ROW LEVEL SECURITY;

-- Only backend service role can insert/update heartbeat_jobs (via FastAPI)
-- This will be handled by service role key, not RLS policy
-- No public read access needed (internal queue)

-- Owners can read heartbeat_jobs for their servers (for debugging/monitoring)
CREATE POLICY "Owners can read own server heartbeat jobs"
    ON heartbeat_jobs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = heartbeat_jobs.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );
