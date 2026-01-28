-- ASASelfHosted.com - Sprint 6 Hosting Provider
-- Exclude Nitrado/Official servers from public directory.
-- Public directory lists only self-hosted servers. Enforcement is server-side (view filter).
-- Run after 012_security_fixes.sql

-- ============================================================================
-- SERVERS TABLE: hosting_provider
-- ============================================================================

ALTER TABLE public.servers
ADD COLUMN IF NOT EXISTS hosting_provider text NOT NULL DEFAULT 'self_hosted';

ALTER TABLE public.servers
DROP CONSTRAINT IF EXISTS servers_hosting_provider_check;

ALTER TABLE public.servers
ADD CONSTRAINT servers_hosting_provider_check
CHECK (hosting_provider IN ('self_hosted', 'nitrado', 'official', 'other_managed'));

CREATE INDEX IF NOT EXISTS idx_servers_hosting_provider
ON public.servers (hosting_provider);

COMMENT ON COLUMN public.servers.hosting_provider IS 'Hosting provider (internal validation only, not exposed in API/UI). Used to block creation of official/nitrado servers. Values: self_hosted, nitrado, official, other_managed. Directory only lists self_hosted.';

-- ============================================================================
-- BACKFILL: Ensure all existing servers are self_hosted
-- ============================================================================

-- Reset any existing servers marked as official/nitrado back to self_hosted
-- (We don't track hosting_provider in UI, only use it to block creation)
UPDATE public.servers
SET hosting_provider = 'self_hosted'
WHERE hosting_provider IN ('nitrado', 'official', 'other_managed');

-- ============================================================================
-- DIRECTORY_VIEW: filter to self_hosted only
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

COMMENT ON VIEW directory_view IS 'Public read model for directory. Lists only self_hosted servers (excludes nitrado, official, other_managed). hosting_provider not exposed in view. Sort columns COALESCE to 0 for deterministic cursor pagination.';
