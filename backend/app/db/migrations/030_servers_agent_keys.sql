-- Per-server agent keys (optional). When set, heartbeat verification uses server key; else cluster key.
-- Run after 029.

ALTER TABLE servers
    ADD COLUMN IF NOT EXISTS public_key_ed25519 TEXT,
    ADD COLUMN IF NOT EXISTS key_version INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS rotated_at TIMESTAMPTZ;

COMMENT ON COLUMN servers.public_key_ed25519 IS 'Base64 Ed25519 public key for agent auth. When set, heartbeat verified with this key; else cluster key.';
COMMENT ON COLUMN servers.key_version IS 'Key version for this server (used when public_key_ed25519 is set).';
COMMENT ON COLUMN servers.rotated_at IS 'When server key was last rotated (ISO timestamp).';
