-- ASASelfHosted.com - Fix mutable search_path warning on update_updated_at_column
-- Supabase flags functions without an explicit search_path. Setting it removes
-- the "role mutable search_path" advisory.
-- Run after 001_sprint_0_schema.sql (or any time after the function exists).

ALTER FUNCTION public.update_updated_at_column()
SET search_path = public;
