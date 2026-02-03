-- ASASelfHosted.com - Add discord_url and website_url to servers
-- Run after 021. Adds optional URL fields and updates directory_view.

-- ============================================================================
-- ADD COLUMNS TO servers
-- ============================================================================
ALTER TABLE public.servers
ADD COLUMN IF NOT EXISTS discord_url TEXT,
ADD COLUMN IF NOT EXISTS website_url TEXT;

COMMENT ON COLUMN public.servers.discord_url IS 'Optional Discord invite or community URL.';
COMMENT ON COLUMN public.servers.website_url IS 'Optional website URL.';

-- ============================================================================
-- RECREATE directory_view TO INCLUDE discord_url, website_url
-- ============================================================================
DROP VIEW IF EXISTS directory_view;

DO $$
DECLARE
    has_join_password boolean;
    has_rulesets boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'servers' AND column_name = 'join_password'
    ) INTO has_join_password;
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'servers' AND column_name = 'rulesets'
    ) INTO has_rulesets;

    IF has_rulesets AND has_join_password THEN
        EXECUTE '
        CREATE VIEW directory_view WITH (security_invoker = true) AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address, s.join_password,
            s.join_instructions_pc, s.join_instructions_console,
            s.discord_url, s.website_url,
            COALESCE(s.mod_list, ''{}''::text[]) AS mod_list, s.rates, s.wipe_info,
            s.effective_status, s.status_source, s.last_seen_at, s.confidence,
            COALESCE(s.created_at, ''1970-01-01''::timestamptz) AS created_at,
            COALESCE(s.updated_at, ''1970-01-01''::timestamptz) AS updated_at,
            c.id AS cluster_id, c.name AS cluster_name, c.slug AS cluster_slug, c.visibility AS cluster_visibility,
            COALESCE(fav_count.favorite_count, 0) AS favorite_count, s.is_verified,
            (CASE WHEN s.created_at > NOW() - INTERVAL ''30 days'' THEN true ELSE false END) AS is_new,
            (CASE WHEN s.effective_status = ''online'' AND s.last_seen_at > NOW() - INTERVAL ''7 days'' THEN true ELSE false END) AS is_stable,
            s.ruleset, COALESCE(s.rulesets, CASE WHEN s.ruleset IS NOT NULL THEN ARRAY[s.ruleset]::text[] ELSE ''{}''::text[] END) AS rulesets,
            s.game_mode,
            (CASE WHEN s.ruleset IN (''vanilla'', ''vanilla_qol'') THEN ''vanilla'' WHEN s.ruleset = ''boosted'' THEN ''boosted'' ELSE NULL END) AS server_type,
            COALESCE(s.platforms, ''{}''::platform[]) AS platforms, s.is_official_plus,
            (CASE WHEN COALESCE(array_length(s.mod_list, 1), 0) > 0 THEN true ELSE false END) AS is_modded,
            s.is_crossplay, s.is_console, s.is_pc,
            COALESCE(s.players_current, 0) AS players_current, s.players_capacity,
            COALESCE(s.quality_score, 0.0) AS quality_score, COALESCE(s.uptime_percent, 0.0) AS uptime_percent,
            COALESCE(s.ranking_score, 0.0) AS ranking_score
        FROM servers s
        LEFT JOIN clusters c ON s.cluster_id = c.id
        LEFT JOIN LATERAL (SELECT COUNT(*)::INTEGER AS favorite_count FROM favorites f WHERE f.server_id = s.id) fav_count ON true
        WHERE s.hosting_provider = ''self_hosted''';
    ELSIF has_join_password THEN
        EXECUTE '
        CREATE VIEW directory_view WITH (security_invoker = true) AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address, s.join_password,
            s.join_instructions_pc, s.join_instructions_console,
            s.discord_url, s.website_url,
            COALESCE(s.mod_list, ''{}''::text[]) AS mod_list, s.rates, s.wipe_info,
            s.effective_status, s.status_source, s.last_seen_at, s.confidence,
            COALESCE(s.created_at, ''1970-01-01''::timestamptz) AS created_at,
            COALESCE(s.updated_at, ''1970-01-01''::timestamptz) AS updated_at,
            c.id AS cluster_id, c.name AS cluster_name, c.slug AS cluster_slug, c.visibility AS cluster_visibility,
            COALESCE(fav_count.favorite_count, 0) AS favorite_count, s.is_verified,
            (CASE WHEN s.created_at > NOW() - INTERVAL ''30 days'' THEN true ELSE false END) AS is_new,
            (CASE WHEN s.effective_status = ''online'' AND s.last_seen_at > NOW() - INTERVAL ''7 days'' THEN true ELSE false END) AS is_stable,
            s.ruleset, (CASE WHEN s.ruleset IS NOT NULL THEN ARRAY[s.ruleset]::text[] ELSE ''{}''::text[] END) AS rulesets,
            s.game_mode,
            (CASE WHEN s.ruleset IN (''vanilla'', ''vanilla_qol'') THEN ''vanilla'' WHEN s.ruleset = ''boosted'' THEN ''boosted'' ELSE NULL END) AS server_type,
            COALESCE(s.platforms, ''{}''::platform[]) AS platforms, s.is_official_plus,
            (CASE WHEN COALESCE(array_length(s.mod_list, 1), 0) > 0 THEN true ELSE false END) AS is_modded,
            s.is_crossplay, s.is_console, s.is_pc,
            COALESCE(s.players_current, 0) AS players_current, s.players_capacity,
            COALESCE(s.quality_score, 0.0) AS quality_score, COALESCE(s.uptime_percent, 0.0) AS uptime_percent,
            COALESCE(s.ranking_score, 0.0) AS ranking_score
        FROM servers s
        LEFT JOIN clusters c ON s.cluster_id = c.id
        LEFT JOIN LATERAL (SELECT COUNT(*)::INTEGER AS favorite_count FROM favorites f WHERE f.server_id = s.id) fav_count ON true
        WHERE s.hosting_provider = ''self_hosted''';
    ELSE
        EXECUTE '
        CREATE VIEW directory_view WITH (security_invoker = true) AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address,
            s.join_instructions_pc, s.join_instructions_console,
            s.discord_url, s.website_url,
            COALESCE(s.mod_list, ''{}''::text[]) AS mod_list, s.rates, s.wipe_info,
            s.effective_status, s.status_source, s.last_seen_at, s.confidence,
            COALESCE(s.created_at, ''1970-01-01''::timestamptz) AS created_at,
            COALESCE(s.updated_at, ''1970-01-01''::timestamptz) AS updated_at,
            c.id AS cluster_id, c.name AS cluster_name, c.slug AS cluster_slug, c.visibility AS cluster_visibility,
            COALESCE(fav_count.favorite_count, 0) AS favorite_count, s.is_verified,
            (CASE WHEN s.created_at > NOW() - INTERVAL ''30 days'' THEN true ELSE false END) AS is_new,
            (CASE WHEN s.effective_status = ''online'' AND s.last_seen_at > NOW() - INTERVAL ''7 days'' THEN true ELSE false END) AS is_stable,
            s.ruleset, (CASE WHEN s.ruleset IS NOT NULL THEN ARRAY[s.ruleset]::text[] ELSE ''{}''::text[] END) AS rulesets,
            s.game_mode,
            (CASE WHEN s.ruleset IN (''vanilla'', ''vanilla_qol'') THEN ''vanilla'' WHEN s.ruleset = ''boosted'' THEN ''boosted'' ELSE NULL END) AS server_type,
            COALESCE(s.platforms, ''{}''::platform[]) AS platforms, s.is_official_plus,
            (CASE WHEN COALESCE(array_length(s.mod_list, 1), 0) > 0 THEN true ELSE false END) AS is_modded,
            s.is_crossplay, s.is_console, s.is_pc,
            COALESCE(s.players_current, 0) AS players_current, s.players_capacity,
            COALESCE(s.quality_score, 0.0) AS quality_score, COALESCE(s.uptime_percent, 0.0) AS uptime_percent,
            COALESCE(s.ranking_score, 0.0) AS ranking_score
        FROM servers s
        LEFT JOIN clusters c ON s.cluster_id = c.id
        LEFT JOIN LATERAL (SELECT COUNT(*)::INTEGER AS favorite_count FROM favorites f WHERE f.server_id = s.id) fav_count ON true
        WHERE s.hosting_provider = ''self_hosted''';
    END IF;
END $$;

COMMENT ON VIEW directory_view IS 'Public read model. Includes discord_url, website_url. SECURITY INVOKER.';
GRANT SELECT ON directory_view TO anon, authenticated;
