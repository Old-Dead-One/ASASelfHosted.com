-- Quick check: Does heartbeat_jobs table exist?
SELECT 
    table_name,
    table_schema
FROM information_schema.tables
WHERE table_name = 'heartbeat_jobs'
    AND table_schema = 'public';

-- If the above returns a row, the table exists and it's a PostgREST cache issue.
-- Refresh the schema cache in Supabase Dashboard: Settings → API → "Reload schema cache"
