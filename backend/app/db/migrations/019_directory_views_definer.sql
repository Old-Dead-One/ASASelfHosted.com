-- ASASelfHosted.com - directory_view and heartbeats_public as SECURITY DEFINER
-- Run after 017_security_invoker_views.sql.
--
-- The backend directory API uses the anon key to query directory_view. Migration 012
-- revoked anon's SELECT on servers/heartbeats so the public can only read via these
-- views. With SECURITY INVOKER (017), the view runs as the caller (anon), who has no
-- SELECT on the base tables, so "permission denied for table servers" occurs.
--
-- We recreate both views as SECURITY DEFINER (default) so that:
-- - anon only needs SELECT on the view; the view runs with the view owner's rights.
-- - The Supabase dashboard may show a SECURITY DEFINER warning; this is intentional.

-- ============================================================================
-- directory_view: SECURITY DEFINER (default)
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
        CREATE VIEW directory_view AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address, s.join_password,
            s.join_instructions_pc, s.join_instructions_console,
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
        CREATE VIEW directory_view AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address, s.join_password,
            s.join_instructions_pc, s.join_instructions_console,
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
        CREATE VIEW directory_view AS
        SELECT
            s.id, s.name, s.description, s.map_name, s.join_address,
            s.join_instructions_pc, s.join_instructions_console,
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

COMMENT ON VIEW directory_view IS 'Public read model. SECURITY DEFINER so anon can read via view without SELECT on servers (012).';

-- ============================================================================
-- heartbeats_public: SECURITY DEFINER (default)
-- ============================================================================

DROP VIEW IF EXISTS heartbeats_public;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'heartbeats'
        AND column_name = 'players_current'
    ) THEN
        EXECUTE '
        CREATE VIEW heartbeats_public AS
        SELECT
            id,
            server_id,
            source,
            received_at,
            status,
            agent_version,
            map_name,
            players_current,
            players_capacity,
            player_count,
            max_players,
            created_at
        FROM heartbeats';
    ELSE
        EXECUTE '
        CREATE VIEW heartbeats_public AS
        SELECT
            id,
            server_id,
            source,
            received_at,
            status,
            agent_version,
            map_name,
            player_count,
            max_players,
            created_at
        FROM heartbeats';
    END IF;
END $$;

COMMENT ON VIEW heartbeats_public IS 'Public sanitized view of heartbeats (excludes payload and signature). SECURITY DEFINER so anon can read via view without SELECT on heartbeats (012).';

-- Re-grant
GRANT SELECT ON directory_view TO anon, authenticated;
GRANT SELECT ON heartbeats_public TO anon, authenticated;
