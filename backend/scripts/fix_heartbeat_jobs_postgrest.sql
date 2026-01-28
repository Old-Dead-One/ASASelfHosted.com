-- Fix heartbeat_jobs PostgREST visibility issue
-- Run this in Supabase SQL Editor

-- 1. Verify table exists
SELECT 'Table exists:' as check_type, COUNT(*) as count
FROM information_schema.tables
WHERE table_name = 'heartbeat_jobs' AND table_schema = 'public';

-- 2. Check RLS status
SELECT 'RLS enabled:' as check_type, rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename = 'heartbeat_jobs' AND schemaname = 'public';

-- 3. Grant permissions to all roles (PostgREST needs this to see the table)
GRANT ALL ON heartbeat_jobs TO postgres;
GRANT ALL ON heartbeat_jobs TO anon;
GRANT ALL ON heartbeat_jobs TO authenticated;
GRANT ALL ON heartbeat_jobs TO service_role;

-- 4. Ensure table is in public schema (should already be, but verify)
-- If table is in wrong schema, PostgREST won't see it

-- 5. Reload PostgREST schema cache (run this multiple times if needed)
NOTIFY pgrst, 'reload schema';

-- 6. Wait 5-10 seconds, then test if PostgREST can see it
-- Test via curl or Postman:
-- curl -H "apikey: YOUR_SERVICE_ROLE_KEY" \
--      -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY" \
--      https://[project-ref].supabase.co/rest/v1/heartbeat_jobs?select=id&limit=1
-- 
-- Should return: [] (empty array) or data, NOT a 404 or PGRST205 error

-- If still not working after grants and NOTIFY:
-- 1. Wait 1-2 minutes (PostgREST cache refresh can take time)
-- 2. Try restarting your Supabase project (if self-hosted)
-- 3. Check if table is actually in 'public' schema (not another schema)
