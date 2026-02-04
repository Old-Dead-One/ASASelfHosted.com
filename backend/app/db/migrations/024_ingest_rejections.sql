-- Sprint 8: Ingest rejections audit trail
-- Stores rejection reason and minimal context for every rejected ingest (no PII).
-- Used by admin views and to demonstrate "we detected and ignored it".

CREATE TABLE IF NOT EXISTS public.ingest_rejections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    received_at timestamptz NOT NULL DEFAULT now(),
    server_id uuid NOT NULL,
    rejection_reason text NOT NULL,
    agent_version text,
    metadata jsonb,
    event_type text DEFAULT 'server.heartbeat.v1'
);

CREATE INDEX IF NOT EXISTS idx_ingest_rejections_received_at
    ON public.ingest_rejections (received_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingest_rejections_server_id
    ON public.ingest_rejections (server_id);
CREATE INDEX IF NOT EXISTS idx_ingest_rejections_rejection_reason
    ON public.ingest_rejections (rejection_reason);

COMMENT ON TABLE public.ingest_rejections IS
    'Audit trail for rejected ingest (heartbeat, etc.). No raw payload or PII. Used for abuse defense and admin visibility.';

ALTER TABLE public.ingest_rejections ENABLE ROW LEVEL SECURITY;

-- Only service role (backend) can insert/select; no anon or authenticated user access
CREATE POLICY ingest_rejections_service_role_all
    ON public.ingest_rejections
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
