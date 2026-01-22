-- ASASelfHosted.com - Validation Query for Platforms Type
-- Run this in Supabase SQL Editor to verify platforms column type is correct
-- Expected: platform[] (not text)

-- Check the actual type of platforms column in servers table
SELECT 
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_name = 'servers' 
  AND column_name = 'platforms';

-- Expected result:
-- column_name: platforms
-- data_type: ARRAY
-- udt_name: platform

-- Also check what PostgREST/JSON will return
SELECT 
    id,
    name,
    platforms,
    pg_typeof(platforms) as platforms_type
FROM servers
LIMIT 1;

-- Expected: platforms_type should be 'platform[]'

-- Check directory_view output
SELECT 
    id,
    name,
    platforms,
    pg_typeof(platforms) as platforms_type
FROM directory_view
LIMIT 1;

-- Expected: platforms_type should be 'platform[]'
-- When returned as JSON via PostgREST, this should serialize as ["steam", "epic"]
-- not as "{steam,epic}"
