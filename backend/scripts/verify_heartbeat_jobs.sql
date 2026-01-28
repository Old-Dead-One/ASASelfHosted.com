-- Verify heartbeat_jobs table exists and check permissions
-- Run this in Supabase SQL Editor

-- 1. Check if table exists
SELECT 
    table_name,
    table_schema,
    table_type
FROM information_schema.tables
WHERE table_name = 'heartbeat_jobs'
    AND table_schema = 'public';

-- 2. Check table structure
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'heartbeat_jobs'
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- 3. Check RLS status
SELECT 
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename = 'heartbeat_jobs'
    AND schemaname = 'public';

-- 4. Check if PostgREST can see it (check exposed schema)
-- PostgREST only exposes tables in the 'public' schema by default
SELECT 
    schemaname,
    tablename
FROM pg_tables
WHERE tablename = 'heartbeat_jobs';

-- 5. Try to reload schema cache again
NOTIFY pgrst, 'reload schema';

-- If table exists but PostgREST still can't see it:
-- 1. Make sure table is in 'public' schema (not another schema)
-- 2. Check if RLS is blocking service_role (shouldn't, but verify)
-- 3. Try restarting Supabase project (if self-hosted) or wait a few minutes for cache to refresh
