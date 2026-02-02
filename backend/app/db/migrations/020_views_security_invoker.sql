-- ASASelfHosted.com - Set directory_view and heartbeats_public to SECURITY INVOKER
-- Run this in Supabase SQL Editor to clear the "SECURITY DEFINER" advisory.
-- Backend directory API uses service_role, so INVOKER views work without granting anon table access.

ALTER VIEW directory_view SET (security_invoker = true);
ALTER VIEW heartbeats_public SET (security_invoker = true);

COMMENT ON VIEW directory_view IS 'Public read model. SECURITY INVOKER so RLS of querying user applies.';
COMMENT ON VIEW heartbeats_public IS 'Public sanitized view of heartbeats (excludes payload and signature). SECURITY INVOKER so RLS of querying user applies.';
