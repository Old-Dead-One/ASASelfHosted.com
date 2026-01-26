-- ASASelfHosted.com - Sprint Cleanup One
-- This migration adds missing indexes and ensures schema consistency
-- Run this in Supabase SQL Editor after 009_sprint_5_ranking_score.sql
--
-- Purpose: Complete database schema alignment for Sprints 1-5
-- - Add missing performance indexes
-- - Ensure all constraints are in place
-- - Verify column types are correct
--
-- NOTE: This migration is idempotent and handles cases where:
-- - Migration 006 (Sprint 4) may not have been run yet (heartbeat_id column check)
-- - Constraints may already exist (duplicate_object exception handling)

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for ranking_score sorting (if sorting by ranking_score is common)
-- This supports ORDER BY ranking_score DESC in directory queries
CREATE INDEX IF NOT EXISTS idx_servers_ranking_score_desc 
    ON servers(ranking_score DESC NULLS LAST) 
    WHERE ranking_score IS NOT NULL;

-- Verify heartbeats index exists (should already exist from 001, but ensure it's there)
-- This is critical for worker queries: SELECT ... WHERE server_id = ? ORDER BY received_at DESC
CREATE INDEX IF NOT EXISTS idx_heartbeats_server_received 
    ON heartbeats(server_id, received_at DESC);

-- Verify servers indexes exist (should already exist from 003, but ensure they're there)
CREATE INDEX IF NOT EXISTS idx_servers_cluster_id 
    ON servers(cluster_id) 
    WHERE cluster_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_servers_effective_status 
    ON servers(effective_status);

-- ============================================================================
-- CONSTRAINTS VERIFICATION
-- ============================================================================

-- Verify favorites unique constraint exists (should already exist from 001)
-- This prevents duplicate favorites per user/server
DO $$ BEGIN
    ALTER TABLE favorites ADD CONSTRAINT uq_favorites_user_server 
        UNIQUE(user_id, server_id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Verify heartbeat replay protection constraint exists (should already exist from 006)
-- This prevents duplicate heartbeat_id per server
-- Only add if heartbeat_id column exists (migration 006 must be run first)
DO $$ 
BEGIN
    -- Check if heartbeat_id column exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'heartbeat_id'
    ) THEN
        -- Column exists, try to add constraint
        ALTER TABLE heartbeats ADD CONSTRAINT uq_heartbeats_server_heartbeat_id 
            UNIQUE(server_id, heartbeat_id);
    END IF;
EXCEPTION
    WHEN duplicate_object THEN null;
    WHEN undefined_column THEN null;
END $$;

-- ============================================================================
-- COLUMN TYPE VERIFICATION
-- ============================================================================

-- Ensure mod_list is TEXT[] (should already be from 001)
-- No change needed if already correct, but document it
COMMENT ON COLUMN servers.mod_list IS 'Array of mod IDs or names. Type: TEXT[]. Never NULL in directory_view (COALESCE to empty array).';

-- Ensure platforms is platform[] with default (should already be from 003)
-- No change needed if already correct, but document it
COMMENT ON COLUMN servers.platforms IS 'Array of supported platforms. Type: platform[] NOT NULL DEFAULT empty array.';

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON INDEX idx_servers_ranking_score_desc IS 'Index for sorting servers by ranking_score DESC. Supports directory queries that sort by ranking.';
COMMENT ON INDEX idx_heartbeats_server_received IS 'Critical index for worker queries: get recent heartbeats for a server ordered by received_at DESC.';
COMMENT ON INDEX idx_servers_cluster_id IS 'Index for filtering servers by cluster_id. Supports directory cluster filters.';
COMMENT ON INDEX idx_servers_effective_status IS 'Index for filtering servers by effective_status. Supports directory status filters.';
COMMENT ON CONSTRAINT uq_favorites_user_server ON favorites IS 'Prevents duplicate favorites: one favorite per user per server.';

-- Comment on heartbeat constraint only if it exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_name = 'heartbeats' 
        AND constraint_name = 'uq_heartbeats_server_heartbeat_id'
    ) THEN
        COMMENT ON CONSTRAINT uq_heartbeats_server_heartbeat_id ON heartbeats IS 'Replay protection: prevents duplicate heartbeat_id per server.';
    END IF;
END $$;
