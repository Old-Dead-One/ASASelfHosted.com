-- Observed status: on-demand refresh queue (priority work for observed worker)
--
-- This table is written by FastAPI using the service_role key and drained by the observed worker.
-- It is NOT intended to be written directly by clients.
--
-- Dedupe: at most one queued row per server at a time.

CREATE TABLE IF NOT EXISTS public.observed_refresh_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES public.servers(id) ON DELETE CASCADE,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    requested_by_user_id UUID NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    reason TEXT NULL,
    status TEXT NOT NULL DEFAULT 'queued', -- queued|processing|done|dropped
    claimed_at TIMESTAMPTZ NULL,
    processed_at TIMESTAMPTZ NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '10 minutes')
);

COMMENT ON TABLE public.observed_refresh_queue IS 'Durable queue for observed status refresh requests (on-demand).';
COMMENT ON COLUMN public.observed_refresh_queue.reason IS 'Why this refresh was requested (filter/search/server_detail/owner_login/test_button).';

CREATE INDEX IF NOT EXISTS idx_observed_refresh_queue_status_requested
    ON public.observed_refresh_queue(status, requested_at);
CREATE INDEX IF NOT EXISTS idx_observed_refresh_queue_claimed_at
    ON public.observed_refresh_queue(claimed_at);
CREATE INDEX IF NOT EXISTS idx_observed_refresh_queue_server_id
    ON public.observed_refresh_queue(server_id);

-- Dedupe: one queued row per server
CREATE UNIQUE INDEX IF NOT EXISTS idx_observed_refresh_queue_queued_unique
    ON public.observed_refresh_queue(server_id)
    WHERE status = 'queued';

ALTER TABLE public.observed_refresh_queue ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS; no insert/update policies needed for it.
-- Allow owners to read for debugging (optional).
DROP POLICY IF EXISTS "Owners can read own observed refresh queue" ON public.observed_refresh_queue;
CREATE POLICY "Owners can read own observed refresh queue"
    ON public.observed_refresh_queue FOR SELECT
    USING (
        EXISTS (
            SELECT 1
            FROM public.servers s
            WHERE s.id = observed_refresh_queue.server_id
              AND s.owner_user_id = (select auth.uid())
        )
    );

