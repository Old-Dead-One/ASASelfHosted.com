-- Sprint 8: Allow server_id NULL in ingest_rejections for malformed_payload (no server_id in invalid body).
-- DROP_ON_VIOLATION: malformed_payload and unknown_field audit.

ALTER TABLE public.ingest_rejections
ALTER COLUMN server_id DROP NOT NULL;

COMMENT ON COLUMN public.ingest_rejections.server_id IS 'Server UUID when known; NULL for malformed requests where body could not be parsed.';
