-- ASASelfHosted.com - Per-user limit overrides (admin can grant more servers/clusters)
-- Default limits come from env (MAX_SERVERS_PER_USER, MAX_CLUSTERS_PER_USER).
-- When set, these override the default for that user.

ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS servers_limit_override INTEGER,
    ADD COLUMN IF NOT EXISTS clusters_limit_override INTEGER;

COMMENT ON COLUMN public.profiles.servers_limit_override IS 'Admin override: max servers for this user. NULL = use MAX_SERVERS_PER_USER.';
COMMENT ON COLUMN public.profiles.clusters_limit_override IS 'Admin override: max clusters for this user. NULL = use MAX_CLUSTERS_PER_USER.';
