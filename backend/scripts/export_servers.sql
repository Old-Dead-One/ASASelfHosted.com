-- ASASelfHosted.com - Export existing servers for structure/sample data
-- Run this in Supabase SQL Editor and paste the result back so we can generate
-- an INSERT script for ~150 more servers.
--
-- Columns match schema after migrations 001 + 003 (no 006, 009, 013, 015).
-- If you get "column does not exist" for join_password, you may have run 012
-- (join_password moved to server_secrets); remove join_password from the SELECT.

-- Optional: list your servers table columns (run this if the main query errors)
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_schema = 'public' AND table_name = 'servers'
-- ORDER BY ordinal_position;

SELECT
    id,
    owner_user_id,
    cluster_id,
    name,
    description,
    map_name,
    join_address,
    join_password,
    join_instructions_pc,
    join_instructions_console,
    mod_list,
    rates,
    wipe_info,
    pvp_enabled,
    vanilla,
    effective_status,
    status_source,
    last_seen_at,
    confidence,
    created_at,
    updated_at,
    ruleset,
    game_mode,
    platforms,
    players_capacity,
    is_official_plus,
    is_crossplay,
    is_console,
    is_pc,
    is_verified,
    players_current,
    quality_score,
    uptime_percent
FROM servers
ORDER BY created_at;
