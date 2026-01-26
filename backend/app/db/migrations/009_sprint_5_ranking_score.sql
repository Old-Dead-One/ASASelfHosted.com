-- ASASelfHosted.com - Sprint 5 Ranking Score
-- Adds ranking_score and ranking_updated_at to servers; exposes them in directory_view.
-- Worker computes ranking via engines/ranking.compute_ranking_score and persists here.
-- Run after 007 and 008.

-- ============================================================================
-- SERVERS TABLE EXTENSIONS
-- ============================================================================

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN ranking_score DOUBLE PRECISION;
EXCEPTION
    WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN ranking_updated_at TIMESTAMPTZ;
EXCEPTION
    WHEN duplicate_column THEN NULL;
END $$;

-- ============================================================================
-- DIRECTORY_VIEW: add ranking columns (recreate view from 008 + new columns)
-- ============================================================================

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
    COALESCE(s.mod_list, '{}'::text[]) AS mod_list,
    s.rates,
    s.wipe_info,
    s.effective_status,
    s.status_source,
    s.last_seen_at,
    s.confidence,
    COALESCE(s.created_at, '1970-01-01'::timestamptz) AS created_at,
    COALESCE(s.updated_at, '1970-01-01'::timestamptz) AS updated_at,
    c.id AS cluster_id,
    c.name AS cluster_name,
    c.slug AS cluster_slug,
    c.visibility AS cluster_visibility,
    COALESCE(fav_count.favorite_count, 0) AS favorite_count,
    s.is_verified,
    CASE WHEN s.created_at > NOW() - INTERVAL '30 days' THEN true ELSE false END AS is_new,
    CASE WHEN s.effective_status = 'online' AND s.last_seen_at > NOW() - INTERVAL '7 days' THEN true ELSE false END AS is_stable,
    s.ruleset,
    s.game_mode,
    CASE
        WHEN s.ruleset IN ('vanilla', 'vanilla_qol') THEN 'vanilla'
        WHEN s.ruleset = 'boosted' THEN 'boosted'
        ELSE NULL
    END AS server_type,
    COALESCE(s.platforms, '{}'::platform[]) AS platforms,
    s.is_official_plus,
    CASE WHEN COALESCE(array_length(s.mod_list, 1), 0) > 0 THEN true ELSE false END AS is_modded,
    s.is_crossplay,
    s.is_console,
    s.is_pc,
    COALESCE(s.players_current, 0) AS players_current,
    s.players_capacity,
    COALESCE(s.quality_score, 0.0) AS quality_score,
    COALESCE(s.uptime_percent, 0.0) AS uptime_percent,
    COALESCE(s.ranking_score, 0.0) AS ranking_score,
    s.ranking_updated_at
FROM servers s
LEFT JOIN clusters c ON s.cluster_id = c.id
LEFT JOIN LATERAL (
    SELECT COUNT(*)::INTEGER AS favorite_count
    FROM favorites f
    WHERE f.server_id = s.id
) fav_count ON true;

COMMENT ON VIEW directory_view IS 'Public read model for directory. Sort columns (players_current, quality_score, uptime_percent, ranking_score) COALESCE for deterministic cursor pagination.';
