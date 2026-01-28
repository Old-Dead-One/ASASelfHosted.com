-- ASASelfHosted.com - Security Fixes Migration
-- This migration fixes critical security issues:
-- 1. Moves join_password to owner-only server_secrets table
-- 2. Restricts heartbeat payload/signature to service-role only
-- Run this in Supabase SQL Editor after all previous migrations

-- ============================================================================
-- FIX 1: MOVE join_password TO OWNER-ONLY TABLE
-- ============================================================================

-- Create server_secrets table for owner-only sensitive data
CREATE TABLE IF NOT EXISTS server_secrets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL UNIQUE REFERENCES servers(id) ON DELETE CASCADE,
    join_password TEXT, -- Encrypted or plaintext (owner-only)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE server_secrets ENABLE ROW LEVEL SECURITY;

-- RLS Policies for server_secrets
-- Only owners can read their own server secrets
CREATE POLICY "Owners can read own server secrets"
    ON server_secrets FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = server_secrets.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );

-- Only owners can insert their own server secrets
CREATE POLICY "Owners can create own server secrets"
    ON server_secrets FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = server_secrets.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );

-- Only owners can update their own server secrets
CREATE POLICY "Owners can update own server secrets"
    ON server_secrets FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = server_secrets.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );

-- Only owners can delete their own server secrets
CREATE POLICY "Owners can delete own server secrets"
    ON server_secrets FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = server_secrets.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );

-- Migrate existing join_password data to server_secrets
-- Only migrate rows where join_password is not null
INSERT INTO server_secrets (server_id, join_password, created_at, updated_at)
SELECT 
    id AS server_id,
    join_password,
    created_at,
    updated_at
FROM servers
WHERE join_password IS NOT NULL
ON CONFLICT (server_id) DO NOTHING;

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_server_secrets_server_id ON server_secrets(server_id);

-- Drop join_password column from servers table
-- This will fail if column doesn't exist, which is OK
DO $$ 
BEGIN
    ALTER TABLE servers DROP COLUMN join_password;
EXCEPTION
    WHEN undefined_column THEN
        RAISE NOTICE 'Column join_password does not exist, skipping drop';
END $$;

-- ============================================================================
-- FIX 2: RESTRICT servers TABLE PUBLIC ACCESS
-- ============================================================================

-- Drop the overly permissive public read policy
DROP POLICY IF EXISTS "Public servers are readable" ON servers;

-- Create a more restrictive policy: public can only read via directory_view
-- We'll create a public view that doesn't expose sensitive fields
-- But first, let's ensure owners can still read their own servers
-- (The "Owners can read own servers" policy already exists)

-- Note: directory_view already exists and is public-readable
-- The servers table itself should not be directly readable by anon users
-- Only owners and service-role should access servers directly

-- ============================================================================
-- FIX 3: RESTRICT heartbeat payload/signature ACCESS
-- ============================================================================

-- Drop the overly permissive public read policy on heartbeats
DROP POLICY IF EXISTS "Public can read recent heartbeats" ON heartbeats;

-- Create a new policy that allows public read of recent heartbeats
-- (This policy will apply to both the base table and views)
-- But we'll revoke direct table access and force public to use the view
CREATE POLICY "Public can read recent heartbeats (sanitized)"
    ON heartbeats FOR SELECT
    USING (received_at > NOW() - INTERVAL '24 hours');

-- Create a sanitized public view of heartbeats (without payload/signature)
-- Views inherit RLS from the base table, so the policy above will apply
-- Note: This view conditionally includes players_current/players_capacity if they exist
-- (added in migration 006). If migration 006 hasn't run, it falls back to legacy fields.
DO $$
BEGIN
    -- Check if players_current column exists (migration 006)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'heartbeats' 
        AND column_name = 'players_current'
    ) THEN
        -- Columns from migration 006 exist - use canonical fields
        EXECUTE '
        CREATE OR REPLACE VIEW heartbeats_public AS
        SELECT
            id,
            server_id,
            source,
            received_at,
            status,
            agent_version,
            map_name,
            players_current,
            players_capacity,
            -- Legacy fields for compatibility
            player_count,
            max_players,
            created_at
            -- NOTE: payload and signature are intentionally excluded
        FROM heartbeats';
    ELSE
        -- Migration 006 hasn't run - use only legacy fields
        EXECUTE '
        CREATE OR REPLACE VIEW heartbeats_public AS
        SELECT
            id,
            server_id,
            source,
            received_at,
            status,
            agent_version,
            map_name,
            -- Legacy fields only (players_current/players_capacity not available yet)
            player_count,
            max_players,
            created_at
            -- NOTE: payload and signature are intentionally excluded
        FROM heartbeats';
    END IF;
END $$;

-- Owners can still read all heartbeats for their servers (including payload/signature)
-- (The "Owners can read own server heartbeats" policy already exists)

-- Service-role can read all heartbeats (for backend operations)
-- Service-role bypasses RLS automatically, no policy needed

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant public read access to heartbeats_public view
-- (anon key can read this view, which respects RLS on base table)
GRANT SELECT ON heartbeats_public TO anon, authenticated;

-- Revoke direct SELECT on heartbeats table from anon
-- (service-role and owners via RLS can still access the base table)
-- Public must use heartbeats_public view instead
REVOKE SELECT ON heartbeats FROM anon;

-- Revoke direct SELECT on servers table from anon
-- (service-role and owners via RLS can still access the base table)
-- Public must use directory_view instead (which doesn't include join_password)
REVOKE SELECT ON servers FROM anon;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE server_secrets IS 'Owner-only sensitive server data (join_password). Not accessible via anon key.';
COMMENT ON COLUMN server_secrets.join_password IS 'Server join password (encrypted or plaintext). Only visible to server owner.';
COMMENT ON VIEW heartbeats_public IS 'Public sanitized view of heartbeats (excludes payload and signature). Use this for public status displays.';
COMMENT ON TABLE heartbeats IS 'Raw heartbeat data including payload and signature. Only accessible to owners and service-role.';
