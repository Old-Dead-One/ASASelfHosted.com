-- ASASelfHosted.com - Restore join_password to servers table
-- join_password should be public/visible, not secret
-- Run this if join_password was moved to server_secrets in migration 012

-- ============================================================================
-- RESTORE join_password COLUMN TO servers TABLE
-- ============================================================================

-- Add join_password column back to servers table if it doesn't exist
ALTER TABLE public.servers
ADD COLUMN IF NOT EXISTS join_password TEXT;

COMMENT ON COLUMN public.servers.join_password IS 'Server join password (public, visible to all players). Not a secret.';

-- ============================================================================
-- MIGRATE DATA FROM server_secrets (if exists)
-- ============================================================================

-- Migrate any existing join_password data from server_secrets back to servers
UPDATE public.servers s
SET join_password = ss.join_password
FROM public.server_secrets ss
WHERE s.id = ss.server_id
  AND ss.join_password IS NOT NULL
  AND s.join_password IS NULL;

-- ============================================================================
-- UPDATE directory_view TO INCLUDE join_password
-- ============================================================================

DROP VIEW IF EXISTS directory_view;

CREATE VIEW directory_view AS
SELECT
    s.id,
    s.name,
    s.description,
    s.map_name,
    s.join_address,
    s.join_password,  -- Now included in public view
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
    -- hosting_provider NOT included in public view (internal validation only)
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
    COALESCE(s.ranking_score, 0.0) AS ranking_score
FROM servers s
LEFT JOIN clusters c ON s.cluster_id = c.id
LEFT JOIN LATERAL (
    SELECT COUNT(*)::INTEGER AS favorite_count
    FROM favorites f
    WHERE f.server_id = s.id
) fav_count ON true
WHERE s.hosting_provider = 'self_hosted';

COMMENT ON VIEW directory_view IS 'Public read model for directory. Lists only self_hosted servers. Includes join_password (public, visible to all players).';
