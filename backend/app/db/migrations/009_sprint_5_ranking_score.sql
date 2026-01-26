-- ASASelfHosted.com - Sprint 5 Ranking Score
-- This migration adds ranking score fields to servers table and updates directory_view
-- Run this in Supabase SQL Editor after 008_sprint_5_directory_view_null_coalesce.sql

-- ============================================================================
-- SERVERS TABLE EXTENSIONS
-- ============================================================================

-- Add ranking score fields (derived metrics, computed by worker)
DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN ranking_score FLOAT;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN ranking_updated_at TIMESTAMPTZ;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

COMMENT ON COLUMN servers.ranking_score IS 'Ranking score (higher = better rank). Derived metric computed by worker using quality_score, uptime_percent, players_current, and anomaly flags. Anti-gaming guards applied.';
COMMENT ON COLUMN servers.ranking_updated_at IS 'Timestamp when ranking_score was last computed/updated by worker.';

-- ============================================================================
-- DIRECTORY_VIEW UPDATE
-- ============================================================================

-- Drop and recreate directory_view to include ranking_score
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
    -- Timestamps (COALESCE for deterministic sorting - ensure never NULL)
    -- Note: created_at and updated_at should never be NULL in practice, but COALESCE ensures safety
    COALESCE(s.created_at, '1970-01-01'::timestamptz) AS created_at,
    COALESCE(s.updated_at, '1970-01-01'::timestamptz) AS updated_at,
    
    -- Cluster info (if associated)
    c.id AS cluster_id,
    c.name AS cluster_name,
    c.slug AS cluster_slug,
    c.visibility AS cluster_visibility,
    
    -- Favorite count (public aggregate) - already COALESCEd to 0, safe for sorting
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
    
    -- Player stats (COALESCE for deterministic sorting)
    -- COALESCE ensures cursor pagination doesn't skip rows when pages end on NULL
    -- Note: DirectoryServer schema expects nullable, but view exposes COALESCEd values for sorting
    COALESCE(s.players_current, 0) AS players_current,
    s.players_capacity,
    
    -- Scoring (COALESCE to 0 for deterministic sorting - NULL treated as 0 for pagination)
    COALESCE(s.quality_score, 0.0) AS quality_score,
    COALESCE(s.uptime_percent, 0.0) AS uptime_percent,
    
    -- Ranking score (COALESCE to 0 for deterministic sorting)
    -- Ranking score is computed by worker and persisted in servers table
    COALESCE(s.ranking_score, 0.0) AS ranking_score
    
FROM servers s
LEFT JOIN clusters c ON s.cluster_id = c.id
LEFT JOIN LATERAL (
    SELECT COUNT(*)::INTEGER AS favorite_count
    FROM favorites f
    WHERE f.server_id = s.id
) fav_count ON true;

COMMENT ON VIEW directory_view IS 'Public read model for directory. Sort columns (players_current, quality_score, uptime_percent, ranking_score) are COALESCE to 0 for deterministic cursor pagination. This ensures cursor pagination never skips rows when pages end on NULL values.';
