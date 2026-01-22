-- ASASelfHosted.com - Sprint 3 Database Schema Updates
-- This migration extends the Sprint 0 schema with directory filtering, ranking, and read model enhancements
-- Run this in Supabase SQL Editor after 001_sprint_0_schema.sql

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Create enum types (safe to run multiple times - will error if types already exist, which is OK)
-- If you get "type already exists" errors, you can safely ignore them
DO $$ BEGIN
    CREATE TYPE ruleset AS ENUM ('vanilla', 'vanilla_qol', 'boosted', 'modded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE game_mode AS ENUM ('pvp', 'pve', 'pvpve');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE platform AS ENUM ('steam', 'xbox', 'playstation', 'windows_store', 'epic');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- SERVERS TABLE EXTENSIONS
-- ============================================================================

-- Add stored columns (static metadata)
-- Use IF NOT EXISTS for idempotency (safe to re-run)
DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN ruleset ruleset;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN game_mode game_mode;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN platforms platform[] NOT NULL DEFAULT '{}'::platform[];
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN players_capacity INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN is_official_plus BOOLEAN;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN is_crossplay BOOLEAN;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN is_console BOOLEAN;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN is_pc BOOLEAN;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Add nullable dynamic columns (populated by agent pipeline in Sprint 4)
DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN players_current INTEGER;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN quality_score DOUBLE PRECISION;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN uptime_percent DOUBLE PRECISION;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite index matching ORDER BY (updated_at DESC, id ASC) - reduces random heap reads
CREATE INDEX IF NOT EXISTS idx_servers_updated_at_id_desc ON servers(updated_at DESC, id ASC);

-- Filter indexes (commonly used filters)
CREATE INDEX IF NOT EXISTS idx_servers_ruleset ON servers(ruleset);
CREATE INDEX IF NOT EXISTS idx_servers_game_mode ON servers(game_mode);
CREATE INDEX IF NOT EXISTS idx_servers_effective_status ON servers(effective_status);
CREATE INDEX IF NOT EXISTS idx_servers_cluster_id ON servers(cluster_id);
CREATE INDEX IF NOT EXISTS idx_servers_is_verified ON servers(is_verified) WHERE is_verified IS TRUE;
CREATE INDEX IF NOT EXISTS idx_servers_players_current ON servers(players_current) WHERE players_current IS NOT NULL;

-- Optional: GIN index for platforms array if platform filter is used heavily
-- CREATE INDEX idx_servers_platforms_gin ON servers USING GIN (platforms);

-- Index for favorites count (used in directory_view lateral join)
CREATE INDEX IF NOT EXISTS idx_favorites_server_id ON favorites(server_id);

-- ============================================================================
-- DIRECTORY_VIEW UPDATE
-- ============================================================================

-- Drop existing view first to avoid column rename conflicts
-- (PostgreSQL interprets column position changes as renames)
DROP VIEW IF EXISTS directory_view;

CREATE VIEW directory_view AS
SELECT
    s.id,
    s.name,
    s.description,
    s.map_name,
    s.join_address,
    s.join_instructions_pc,
    s.join_instructions_console,
    -- mod_list and platforms must never be NULL (DirectoryServer requires list, not Optional)
    COALESCE(s.mod_list, '{}'::text[]) AS mod_list,
    s.rates,
    s.wipe_info,
    s.effective_status,
    s.status_source,
    s.last_seen_at,
    s.confidence,
    s.created_at,
    s.updated_at,
    
    -- Cluster info (if associated)
    c.id AS cluster_id,
    c.name AS cluster_name,
    c.slug AS cluster_slug,
    c.visibility AS cluster_visibility,
    
    -- Favorite count (public aggregate)
    COALESCE(fav_count.favorite_count, 0) AS favorite_count,
    
    -- Badge flags (computed)
    s.is_verified, -- Real boolean column, NOT NULL DEFAULT FALSE
    CASE WHEN s.created_at > NOW() - INTERVAL '30 days' THEN true ELSE false END AS is_new,
    CASE WHEN s.effective_status = 'online' AND s.last_seen_at > NOW() - INTERVAL '7 days' THEN true ELSE false END AS is_stable,
    
    -- Classification fields
    s.ruleset, -- Enum: vanilla, vanilla_qol, boosted, modded
    s.game_mode, -- Enum: pvp, pve, pvpve
    -- Legacy server_type (derived for backwards compatibility)
    CASE 
        WHEN s.ruleset IN ('vanilla', 'vanilla_qol') THEN 'vanilla'
        WHEN s.ruleset = 'boosted' THEN 'boosted'
        ELSE NULL
    END AS server_type,
    
    -- Platform and feature flags
    -- platforms must never be NULL (DirectoryServer requires list, not Optional)
    COALESCE(s.platforms, '{}'::platform[]) AS platforms,
    s.is_official_plus,
    CASE WHEN COALESCE(array_length(s.mod_list, 1), 0) > 0 THEN true ELSE false END AS is_modded,
    s.is_crossplay,
    s.is_console,
    s.is_pc,
    
    -- Player stats
    s.players_current,
    s.players_capacity,
    
    -- Scoring (nullable, populated by agent pipeline in Sprint 4)
    s.quality_score,
    s.uptime_percent
    
FROM servers s
LEFT JOIN clusters c ON s.cluster_id = c.id
LEFT JOIN LATERAL (
    SELECT COUNT(*)::INTEGER AS favorite_count
    FROM favorites f
    WHERE f.server_id = s.id
) fav_count ON true;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON COLUMN servers.ruleset IS 'Server ruleset classification: vanilla, vanilla_qol, boosted, or modded';
COMMENT ON COLUMN servers.game_mode IS 'Game mode: pvp, pve, or pvpve';
COMMENT ON COLUMN servers.platforms IS 'Array of supported platforms (enum array)';
COMMENT ON COLUMN servers.players_capacity IS 'Maximum player capacity (static server config)';
COMMENT ON COLUMN servers.is_verified IS 'Listing verification/trust flag (NOT NULL, separate from status_source)';
COMMENT ON COLUMN servers.players_current IS 'Current player count (nullable, updated from heartbeats)';
COMMENT ON COLUMN servers.quality_score IS 'Computed quality score 0-100 (nullable, populated by agent pipeline)';
COMMENT ON COLUMN servers.uptime_percent IS 'Uptime percentage 0-100 (nullable, populated by agent pipeline)';
COMMENT ON VIEW directory_view IS 'Public read model for directory - provides persisted fields for DirectoryServer schema. Backend adds computed rank fields (rank_position, rank_delta_24h, rank_by) and legacy aliases.';
