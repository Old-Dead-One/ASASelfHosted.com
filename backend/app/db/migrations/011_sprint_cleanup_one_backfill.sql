-- ASASelfHosted.com - Sprint Cleanup One Backfill
-- This migration backfills canonical fields from legacy fields (if needed)
-- Run this in Supabase SQL Editor after 010_sprint_cleanup_one.sql
--
-- Purpose: Migrate existing data to use canonical fields
-- - Backfill players_current from player_count (if exists)
-- - Backfill players_capacity from max_players (if exists)
--
-- NOTE: 
-- - Only run this if you have existing data with legacy fields populated
--   and canonical fields are NULL. If you're starting fresh, skip this migration.
-- - This migration is idempotent and checks if columns exist before backfilling.
-- - Requires migrations 003 (servers.players_current) and 006 (heartbeats.players_current)
--   to be run first. If columns don't exist, backfill is skipped safely.

-- ============================================================================
-- BACKFILL CANONICAL PLAYER FIELDS
-- ============================================================================

-- Backfill players_current from player_count (heartbeats table)
-- Only update rows where players_current is NULL and player_count is NOT NULL
-- Only runs if players_current column exists (migration 006 must be run first)
DO $$ 
BEGIN
    -- Check if players_current column exists in heartbeats
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_current'
    ) THEN
        -- Column exists, perform backfill
        UPDATE heartbeats
        SET players_current = player_count
        WHERE players_current IS NULL 
          AND player_count IS NOT NULL;
    END IF;
END $$;

-- Backfill players_capacity from max_players (heartbeats table)
-- Only update rows where players_capacity is NULL and max_players is NOT NULL
-- Only runs if players_capacity column exists (migration 006 must be run first)
DO $$ 
BEGIN
    -- Check if players_capacity column exists in heartbeats
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_capacity'
    ) THEN
        -- Column exists, perform backfill
        UPDATE heartbeats
        SET players_capacity = max_players
        WHERE players_capacity IS NULL 
          AND max_players IS NOT NULL;
    END IF;
END $$;

-- Backfill servers.players_current from most recent heartbeat
-- Only update rows where players_current is NULL
-- Uses the most recent heartbeat's players_current value
-- Only runs if players_current column exists in both tables (migrations 003 and 006)
DO $$ 
BEGIN
    -- Check if players_current column exists in both servers and heartbeats
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'servers' 
        AND column_name = 'players_current'
    ) AND EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_current'
    ) THEN
        -- Columns exist, perform backfill
        UPDATE servers s
        SET players_current = (
            SELECT h.players_current
            FROM heartbeats h
            WHERE h.server_id = s.id
              AND h.players_current IS NOT NULL
            ORDER BY h.received_at DESC
            LIMIT 1
        )
        WHERE s.players_current IS NULL
          AND EXISTS (
              SELECT 1
              FROM heartbeats h
              WHERE h.server_id = s.id
                AND h.players_current IS NOT NULL
          );
    END IF;
END $$;

-- Backfill servers.players_capacity from most recent heartbeat
-- Only update rows where players_capacity is NULL
-- Uses the most recent heartbeat's players_capacity value
-- Only runs if players_capacity column exists in both tables (migrations 003 and 006)
DO $$ 
BEGIN
    -- Check if players_capacity column exists in both servers and heartbeats
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'servers' 
        AND column_name = 'players_capacity'
    ) AND EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_capacity'
    ) THEN
        -- Columns exist, perform backfill
        UPDATE servers s
        SET players_capacity = (
            SELECT h.players_capacity
            FROM heartbeats h
            WHERE h.server_id = s.id
              AND h.players_capacity IS NOT NULL
            ORDER BY h.received_at DESC
            LIMIT 1
        )
        WHERE s.players_capacity IS NULL
          AND EXISTS (
              SELECT 1
              FROM heartbeats h
              WHERE h.server_id = s.id
                AND h.players_capacity IS NOT NULL
          );
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES (run these to check backfill results)
-- ============================================================================

-- Check how many heartbeats were backfilled
-- SELECT 
--     COUNT(*) FILTER (WHERE players_current IS NOT NULL AND player_count IS NOT NULL) AS backfilled_current,
--     COUNT(*) FILTER (WHERE players_capacity IS NOT NULL AND max_players IS NOT NULL) AS backfilled_capacity
-- FROM heartbeats;

-- Check how many servers were backfilled
-- SELECT 
--     COUNT(*) FILTER (WHERE players_current IS NOT NULL) AS servers_with_current,
--     COUNT(*) FILTER (WHERE players_capacity IS NOT NULL) AS servers_with_capacity
-- FROM servers;

-- Add comments only if columns exist
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_current'
    ) THEN
        COMMENT ON COLUMN heartbeats.players_current IS 'Canonical field: current player count. Backfilled from player_count if needed.';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_capacity'
    ) THEN
        COMMENT ON COLUMN heartbeats.players_capacity IS 'Canonical field: player capacity. Backfilled from max_players if needed.';
    END IF;
END $$;
