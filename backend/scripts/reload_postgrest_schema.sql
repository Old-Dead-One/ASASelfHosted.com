-- Refresh PostgREST schema cache
-- Run this in Supabase SQL Editor when you get PGRST205 errors
-- This tells PostgREST to reload its schema cache

NOTIFY pgrst, 'reload schema';

-- You should see: "Success. No rows returned"
-- After running this, restart your backend and the heartbeat_jobs table should be visible
