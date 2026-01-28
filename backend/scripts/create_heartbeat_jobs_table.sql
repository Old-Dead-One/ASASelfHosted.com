-- Create heartbeat_jobs table (from migration 006_sprint_4_agent_auth.sql)
-- Run this in Supabase SQL Editor

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

-- Enable RLS
ALTER TABLE heartbeat_jobs ENABLE ROW LEVEL SECURITY;

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

-- Grant permissions for PostgREST
GRANT ALL ON heartbeat_jobs TO postgres;
GRANT ALL ON heartbeat_jobs TO anon;
GRANT ALL ON heartbeat_jobs TO authenticated;
GRANT ALL ON heartbeat_jobs TO service_role;

-- Index for worker polling (unclaimed pending jobs ordered by enqueued_at)
CREATE INDEX IF NOT EXISTS idx_heartbeat_jobs_pending 
    ON heartbeat_jobs(processed_at, enqueued_at) 
    WHERE processed_at IS NULL AND claimed_at IS NULL;

-- Index for claimed jobs (for monitoring/debugging)
CREATE INDEX IF NOT EXISTS idx_heartbeat_jobs_claimed 
    ON heartbeat_jobs(claimed_at) 
    WHERE claimed_at IS NOT NULL AND processed_at IS NULL;

-- Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify table was created
SELECT 'heartbeat_jobs table created' as status, COUNT(*) as row_count
FROM heartbeat_jobs;
