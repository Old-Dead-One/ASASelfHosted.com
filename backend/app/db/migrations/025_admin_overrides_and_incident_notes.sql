-- Sprint 8: Admin overrides (hidden_at, badges_frozen) and incident_notes.
-- Run after 024_ingest_rejections.sql.

-- ============================================================================
-- SERVERS: admin override columns
-- ============================================================================
ALTER TABLE public.servers
ADD COLUMN IF NOT EXISTS hidden_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS badges_frozen BOOLEAN NOT NULL DEFAULT false;

COMMENT ON COLUMN public.servers.hidden_at IS 'When set, server is excluded from directory_view (admin hide).';
COMMENT ON COLUMN public.servers.badges_frozen IS 'When true, worker does not update badge/ranking-derived fields (admin override).';

-- ============================================================================
-- INCIDENT_NOTES: admin-only notes (e.g. why server was hidden)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.incident_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID REFERENCES public.servers(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES public.clusters(id) ON DELETE SET NULL,
    author_id UUID NOT NULL,
    note_text TEXT NOT NULL,
    internal_only BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_incident_notes_server_id ON public.incident_notes (server_id);
CREATE INDEX IF NOT EXISTS idx_incident_notes_created_at ON public.incident_notes (created_at DESC);

COMMENT ON TABLE public.incident_notes IS 'Admin-only notes (e.g. why server was hidden). Never exposed to public or normal users.';

ALTER TABLE public.incident_notes ENABLE ROW LEVEL SECURITY;

-- Only service_role (backend) can access; no anon/authenticated policy
CREATE POLICY incident_notes_service_role_all
    ON public.incident_notes
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
