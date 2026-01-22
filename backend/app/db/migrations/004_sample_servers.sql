-- ASASelfHosted.com - Sample Server Data
-- This script inserts sample servers for testing and development
-- Run this in Supabase SQL Editor after migrations 001 and 003

-- ============================================================================
-- CREATE TEST USER (if needed)
-- ============================================================================

-- First, check if you have any users in auth.users
-- If you don't have any users, you'll need to create one via Supabase Auth UI
-- or use this SQL to create a test user (requires admin privileges)

-- Option 1: Use an existing user
-- Get a user ID from: SELECT id FROM auth.users LIMIT 1;
-- Then replace the UUID below with that ID

-- Option 2: Create a test user via Supabase Dashboard
-- Go to Authentication → Users → Add User
-- Then get the user ID and use it below

-- For this script, we'll use a placeholder UUID
-- Replace '00000000-0000-0000-0000-000000000001' with your actual user ID
DO $$
DECLARE
    test_user_id UUID;
BEGIN
    -- Try to get the first user from auth.users
    SELECT id INTO test_user_id FROM auth.users LIMIT 1;
    
    -- If no users exist, we'll need to create one or use a placeholder
    IF test_user_id IS NULL THEN
        RAISE NOTICE 'No users found in auth.users. Please create a user first via Supabase Dashboard (Authentication → Users → Add User)';
        RAISE EXCEPTION 'No users found. Create a user first.';
    END IF;
    
    -- Store the user ID for use in INSERT statements
    -- We'll use a session variable approach, but for simplicity, 
    -- we'll just use the first user found
    RAISE NOTICE 'Using user ID: %', test_user_id;
END $$;

-- ============================================================================
-- INSERT SAMPLE SERVERS
-- ============================================================================

-- Insert sample servers using the first available user
-- Replace the owner_user_id with your actual user ID from auth.users
INSERT INTO servers (
    owner_user_id,
    name,
    description,
    map_name,
    join_address,
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
    -- Sprint 3 fields
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
) VALUES
-- Server 1: Vanilla PvP Official-like
(
    (SELECT id FROM auth.users LIMIT 1), -- Use first available user
    'Island PvP Server',
    'A classic vanilla PvP experience on The Island. Active community, regular events!',
    'The Island',
    '192.168.1.100:7777',
    'Open ARK, click "Join ARK", search for "Island PvP Server"',
    'Search for "Island PvP Server" in server browser',
    ARRAY[]::TEXT[],
    '1x Harvest, 1x XP, 1x Taming',
    'Monthly wipes on the 1st',
    true,
    true,
    'online',
    'manual',
    NOW() - INTERVAL '2 hours',
    'green',
    'vanilla',
    'pvp',
    ARRAY['steam', 'epic']::platform[],
    70,
    false,
    false,
    false,
    true,
    false,
    45,
    85.5,
    98.2
),
-- Server 2: Modded PvE
(
    (SELECT id FROM auth.users LIMIT 1),
    'Modded PvE Paradise',
    'Heavily modded PvE server with quality of life improvements. Perfect for casual players!',
    'The Island',
    '192.168.1.101:7777',
    'Subscribe to mods: 123456789, 987654321, 555555555',
    NULL,
    ARRAY['S+ Structures', 'Dino Storage v2', 'Awesome Spyglass'],
    '5x Harvest, 10x XP, 15x Taming',
    'No wipes planned',
    false,
    false,
    'online',
    'agent',
    NOW() - INTERVAL '30 minutes',
    'green',
    'modded',
    'pve',
    ARRAY['steam']::platform[],
    50,
    false,
    false,
    false,
    true,
    true,
    32,
    92.0,
    99.5
),
-- Server 3: Boosted PvPvE
(
    (SELECT id FROM auth.users LIMIT 1),
    'Scorched Earth Boosted',
    'Boosted rates on Scorched Earth. PvP during weekdays, PvE on weekends!',
    'Scorched Earth',
    '192.168.1.102:7777',
    'Direct connect: 192.168.1.102:7777',
    'Search "Scorched Earth Boosted"',
    ARRAY[]::TEXT[],
    '3x Harvest, 5x XP, 8x Taming',
    'Bi-weekly wipes',
    true,
    false,
    'online',
    'manual',
    NOW() - INTERVAL '1 hour',
    'yellow',
    'boosted',
    'pvpve',
    ARRAY['steam', 'xbox', 'playstation']::platform[],
    100,
    false,
    true,
    true,
    true,
    false,
    67,
    78.3,
    95.0
),
-- Server 4: Vanilla QoL PvE
(
    (SELECT id FROM auth.users LIMIT 1),
    'Vanilla+ PvE Community',
    'Vanilla experience with quality of life improvements. Great for beginners!',
    'The Island',
    '192.168.1.103:7777',
    'Join via server browser',
    'Join via server browser',
    ARRAY[]::TEXT[],
    '1x Harvest, 2x XP, 2x Taming',
    'Seasonal wipes',
    false,
    true,
    'online',
    'manual',
    NOW() - INTERVAL '15 minutes',
    'green',
    'vanilla_qol',
    'pve',
    ARRAY['steam', 'windows_store']::platform[],
    40,
    false,
    false,
    false,
    true,
    true,
    28,
    88.7,
    97.8
),
-- Server 5: Official+ Crossplay
(
    (SELECT id FROM auth.users LIMIT 1),
    'Official+ Crossplay Server',
    'Official-like experience with crossplay support. All platforms welcome!',
    'The Island',
    '192.168.1.104:7777',
    'Crossplay enabled - join from any platform',
    'Crossplay enabled - join from any platform',
    ARRAY[]::TEXT[],
    '1x Harvest, 1x XP, 1x Taming',
    'No wipes',
    true,
    true,
    'online',
    'agent',
    NOW() - INTERVAL '5 minutes',
    'green',
    'vanilla',
    'pvp',
    ARRAY['steam', 'xbox', 'playstation', 'windows_store', 'epic']::platform[],
    100,
    true,
    true,
    true,
    true,
    true,
    89,
    95.2,
    99.9
),
-- Server 6: Offline Server (for testing)
(
    (SELECT id FROM auth.users LIMIT 1),
    'Test Offline Server',
    'This server is offline for testing purposes',
    'The Island',
    '192.168.1.105:7777',
    NULL,
    NULL,
    ARRAY[]::TEXT[],
    '1x Everything',
    NULL,
    false,
    true,
    'offline',
    'manual',
    NOW() - INTERVAL '2 days',
    'red',
    'vanilla',
    'pve',
    ARRAY['steam']::platform[],
    50,
    false,
    false,
    false,
    true,
    false,
    NULL,
    NULL,
    NULL
);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check that servers were inserted
SELECT 
    COUNT(*) as total_servers,
    COUNT(*) FILTER (WHERE effective_status = 'online') as online_servers,
    COUNT(*) FILTER (WHERE effective_status = 'offline') as offline_servers
FROM servers;

-- View the inserted servers
SELECT 
    id,
    name,
    map_name,
    ruleset,
    game_mode,
    effective_status,
    is_verified,
    players_current,
    platforms
FROM servers
ORDER BY created_at DESC;
