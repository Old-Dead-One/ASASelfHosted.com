-- Sprint 10 (detour): Observed status foundations
--
-- Adds:
-- - status_source enum value: observed
-- - observed result fields on servers (safe to expose via directory)
-- - manual_status fields (owner-managed status, preserved across monitoring modes)
-- - server_observation_config (owner-only observation configuration: enable + host + port)
--
-- Notes:
-- - Observed configuration is owner-only (similar to server_secrets) to avoid exposing
--   editable probe targets publicly.
-- - Observed results live on servers for cheap reads and future directory display.

-- 1) Extend status_source enum to include 'observed'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = 'status_source' AND e.enumlabel = 'observed'
    ) THEN
        -- already present
        NULL;
    ELSE
        ALTER TYPE status_source ADD VALUE 'observed';
    END IF;
END $$;

-- 2) Observed result fields on servers
ALTER TABLE public.servers
    ADD COLUMN IF NOT EXISTS observed_status server_status,
    ADD COLUMN IF NOT EXISTS observed_checked_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS observed_latency_ms INTEGER,
    ADD COLUMN IF NOT EXISTS observed_error TEXT,
    ADD COLUMN IF NOT EXISTS observed_next_check_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS observed_fail_streak INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.servers.observed_status IS 'Best-effort observed status (not verified).';
COMMENT ON COLUMN public.servers.observed_checked_at IS 'When observed status was last checked.';
COMMENT ON COLUMN public.servers.observed_latency_ms IS 'Observed probe round-trip latency in ms (if known).';
COMMENT ON COLUMN public.servers.observed_error IS 'Observed probe error category (timeout/refused/unreachable/bad_response).';
COMMENT ON COLUMN public.servers.observed_next_check_at IS 'Next scheduled observed check time (rolling sweeps).';
COMMENT ON COLUMN public.servers.observed_fail_streak IS 'Consecutive observed failures (for backoff/tuning).';

CREATE INDEX IF NOT EXISTS idx_servers_observed_next_check_at
    ON public.servers(observed_next_check_at);
CREATE INDEX IF NOT EXISTS idx_servers_observed_checked_at
    ON public.servers(observed_checked_at DESC);

-- 3) Manual status fields (owner-managed)
ALTER TABLE public.servers
    ADD COLUMN IF NOT EXISTS manual_status server_status,
    ADD COLUMN IF NOT EXISTS manual_updated_at TIMESTAMPTZ;

COMMENT ON COLUMN public.servers.manual_status IS 'Owner-managed manual status when no observation/agent monitoring is enabled.';
COMMENT ON COLUMN public.servers.manual_updated_at IS 'Timestamp when manual_status was last updated.';

-- 4) Owner-only observation configuration (editable probe target)
CREATE TABLE IF NOT EXISTS public.server_observation_config (
    server_id UUID PRIMARY KEY REFERENCES public.servers(id) ON DELETE CASCADE,
    observation_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    observed_host TEXT,
    observed_port INTEGER,
    observed_probe TEXT NOT NULL DEFAULT 'a2s',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.server_observation_config IS 'Owner-only observation settings (opt-in). Stores probe host/port/probe type.';
COMMENT ON COLUMN public.server_observation_config.observed_host IS 'Observed probe host (defaulted from join_address host portion).';
COMMENT ON COLUMN public.server_observation_config.observed_port IS 'Observed probe port (required when observation_enabled=true).';
COMMENT ON COLUMN public.server_observation_config.observed_probe IS 'Observed probe type (default a2s). Future-proofing.';

CREATE INDEX IF NOT EXISTS idx_server_observation_config_enabled
    ON public.server_observation_config(observation_enabled);

-- Trigger to keep updated_at current (reuse helper function if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        DROP TRIGGER IF EXISTS update_server_observation_config_updated_at ON public.server_observation_config;
        CREATE TRIGGER update_server_observation_config_updated_at
            BEFORE UPDATE ON public.server_observation_config
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- RLS: owner-only (match patterns from server_secrets)
ALTER TABLE public.server_observation_config ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Owners can read own server observation config" ON public.server_observation_config;
CREATE POLICY "Owners can read own server observation config"
    ON public.server_observation_config FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_observation_config.server_id
              AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can create own server observation config" ON public.server_observation_config;
CREATE POLICY "Owners can create own server observation config"
    ON public.server_observation_config FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_observation_config.server_id
              AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can update own server observation config" ON public.server_observation_config;
CREATE POLICY "Owners can update own server observation config"
    ON public.server_observation_config FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_observation_config.server_id
              AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can delete own server observation config" ON public.server_observation_config;
CREATE POLICY "Owners can delete own server observation config"
    ON public.server_observation_config FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_observation_config.server_id
              AND s.owner_user_id = (select auth.uid())
        )
    );

