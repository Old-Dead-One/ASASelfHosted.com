-- ASASelfHosted.com - Sprint 0 Database Schema
-- This migration creates the core directory tables, status tracking, and public read model
-- Run this in Supabase SQL Editor after creating your project

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PROFILES TABLE
-- Extends Supabase auth.users with additional profile data
-- ============================================================================

CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
-- Users can read their own profile
CREATE POLICY "Users can read own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Public profiles are readable (if visibility is added later)
-- For now, keep it private

-- ============================================================================
-- CLUSTERS TABLE
-- Data-only cluster model (MVP). Cluster pages come in Phase 1.5
-- ============================================================================

CREATE TYPE cluster_visibility AS ENUM ('public', 'unlisted');

CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    owner_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    visibility cluster_visibility NOT NULL DEFAULT 'public',
    -- Key metadata (no plaintext private keys)
    key_version INTEGER NOT NULL DEFAULT 1,
    public_fingerprint TEXT, -- Hash/fingerprint of cluster public identity
    rotated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE clusters ENABLE ROW LEVEL SECURITY;

-- RLS Policies for clusters
-- Public clusters are readable by everyone
CREATE POLICY "Public clusters are readable"
    ON clusters FOR SELECT
    USING (visibility = 'public');

-- Owners can read their own clusters (including unlisted)
CREATE POLICY "Owners can read own clusters"
    ON clusters FOR SELECT
    USING (auth.uid() = owner_user_id);

-- Owners can create clusters
CREATE POLICY "Owners can create clusters"
    ON clusters FOR INSERT
    WITH CHECK (auth.uid() = owner_user_id);

-- Owners can update their own clusters
CREATE POLICY "Owners can update own clusters"
    ON clusters FOR UPDATE
    USING (auth.uid() = owner_user_id);

-- Owners can delete their own clusters
CREATE POLICY "Owners can delete own clusters"
    ON clusters FOR DELETE
    USING (auth.uid() = owner_user_id);

-- ============================================================================
-- SERVERS TABLE
-- Core server listings with effective status fields
-- ============================================================================

CREATE TYPE server_status AS ENUM ('online', 'offline', 'unknown');
CREATE TYPE status_source AS ENUM ('manual', 'agent');

CREATE TABLE servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES clusters(id) ON DELETE SET NULL,
    
    -- Basic listing info
    name TEXT NOT NULL,
    description TEXT,
    map_name TEXT, -- e.g., "The Island", "Scorched Earth"
    
    -- Join information
    join_address TEXT, -- IP:Port or hostname:port
    join_password TEXT, -- Encrypted or plaintext (gated by RLS)
    join_instructions_pc TEXT,
    join_instructions_console TEXT,
    
    -- Server configuration (manual entry)
    mod_list TEXT[], -- Array of mod IDs or names
    rates TEXT, -- Freeform text description
    wipe_info TEXT,
    pvp_enabled BOOLEAN DEFAULT false,
    vanilla BOOLEAN DEFAULT false,
    
    -- Effective status (current/active status for fast directory reads)
    effective_status server_status NOT NULL DEFAULT 'unknown',
    status_source status_source,
    last_seen_at TIMESTAMPTZ,
    confidence TEXT, -- Optional now; RYG later (e.g., 'green', 'yellow', 'red')
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE servers ENABLE ROW LEVEL SECURITY;

-- RLS Policies for servers
-- Public servers are readable by everyone (for directory)
CREATE POLICY "Public servers are readable"
    ON servers FOR SELECT
    USING (true); -- All servers are public by default (can add visibility later)

-- Owners can read their own servers (including password)
CREATE POLICY "Owners can read own servers"
    ON servers FOR SELECT
    USING (auth.uid() = owner_user_id);

-- Users who favorited a server can read password
-- (This will be handled via favorites table join in a view)

-- Owners can create servers
CREATE POLICY "Owners can create servers"
    ON servers FOR INSERT
    WITH CHECK (auth.uid() = owner_user_id);

-- Owners can update their own servers
CREATE POLICY "Owners can update own servers"
    ON servers FOR UPDATE
    USING (auth.uid() = owner_user_id);

-- Owners can delete their own servers
CREATE POLICY "Owners can delete own servers"
    ON servers FOR DELETE
    USING (auth.uid() = owner_user_id);

-- ============================================================================
-- HEARTBEATS TABLE
-- Generic append-only events table for server status history
-- ============================================================================

CREATE TABLE heartbeats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    source status_source NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB, -- Flexible payload for different sources
    signature TEXT, -- For agent-signed heartbeats
    status server_status,
    -- Additional metadata
    agent_version TEXT,
    map_name TEXT,
    player_count INTEGER,
    max_players INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_heartbeats_server_received ON heartbeats(server_id, received_at DESC);
CREATE INDEX idx_heartbeats_received_at ON heartbeats(received_at DESC);

-- Enable RLS
ALTER TABLE heartbeats ENABLE ROW LEVEL SECURITY;

-- RLS Policies for heartbeats
-- Public can read recent heartbeats (for status display)
CREATE POLICY "Public can read recent heartbeats"
    ON heartbeats FOR SELECT
    USING (received_at > NOW() - INTERVAL '24 hours');

-- Owners can read all heartbeats for their servers
CREATE POLICY "Owners can read own server heartbeats"
    ON heartbeats FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM servers
            WHERE servers.id = heartbeats.server_id
            AND servers.owner_user_id = auth.uid()
        )
    );

-- Only backend service role can insert heartbeats (via FastAPI)
-- This will be handled by service role key, not RLS policy

-- ============================================================================
-- FAVORITES TABLE
-- Player favorites for servers
-- ============================================================================

CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, server_id) -- One favorite per user per server
);

-- Index for fast lookups
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_server ON favorites(server_id);

-- Enable RLS
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;

-- RLS Policies for favorites
-- Users can read their own favorites
CREATE POLICY "Users can read own favorites"
    ON favorites FOR SELECT
    USING (auth.uid() = user_id);

-- Users can create their own favorites
CREATE POLICY "Users can create own favorites"
    ON favorites FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own favorites
CREATE POLICY "Users can delete own favorites"
    ON favorites FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- SUBSCRIPTIONS TABLE
-- Minimal Stripe subscription plumbing (MVP)
-- ============================================================================

CREATE TYPE subscription_status AS ENUM (
    'trialing',
    'active',
    'past_due',
    'canceled',
    'unpaid',
    'incomplete',
    'incomplete_expired'
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT UNIQUE,
    status subscription_status NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT false,
    -- Quota fields (simple, can compute later)
    key_quota_total INTEGER NOT NULL DEFAULT 12, -- Base included keys
    key_quota_additional INTEGER NOT NULL DEFAULT 8, -- Additional available
    key_quota_max INTEGER NOT NULL DEFAULT 20, -- Max total (convenience)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for subscriptions
-- Users can read their own subscription
CREATE POLICY "Users can read own subscription"
    ON subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Only backend service role can create/update subscriptions (via Stripe webhooks)
-- This will be handled by service role key, not RLS policy

-- ============================================================================
-- DIRECTORY_VIEW
-- Public read model for directory (single source of truth for frontend)
-- ============================================================================

CREATE OR REPLACE VIEW directory_view AS
SELECT
    s.id,
    s.name,
    s.description,
    s.map_name,
    s.join_address,
    s.join_password, -- Will be filtered by RLS based on favorites
    s.join_instructions_pc,
    s.join_instructions_console,
    s.mod_list,
    s.rates,
    s.wipe_info,
    s.pvp_enabled,
    s.vanilla,
    s.effective_status,
    s.status_source,
    s.last_seen_at,
    s.confidence,
    s.created_at,
    s.updated_at,
    -- Cluster info (if associated)
    c.id AS cluster_id,
    c.name AS cluster_name,
    c.slug AS cluster_slug,
    c.visibility AS cluster_visibility,
    -- Owner info (minimal)
    p.display_name AS owner_display_name,
    -- Favorite count (public aggregate)
    COALESCE(fav_count.favorite_count, 0) AS favorite_count,
    -- Badge flags (computed, will be enhanced later)
    CASE WHEN s.status_source = 'agent' THEN true ELSE false END AS is_verified,
    CASE WHEN s.created_at > NOW() - INTERVAL '30 days' THEN true ELSE false END AS is_new,
    CASE WHEN s.effective_status = 'online' AND s.last_seen_at > NOW() - INTERVAL '7 days' THEN true ELSE false END AS is_stable,
    CASE WHEN s.pvp_enabled THEN 'pvp' ELSE 'pve' END AS game_mode,
    CASE WHEN s.vanilla THEN 'vanilla' ELSE 'boosted' END AS server_type
FROM servers s
LEFT JOIN clusters c ON s.cluster_id = c.id
LEFT JOIN profiles p ON s.owner_user_id = p.id
LEFT JOIN LATERAL (
    SELECT COUNT(*)::INTEGER AS favorite_count
    FROM favorites f
    WHERE f.server_id = s.id
) fav_count ON true;

-- RLS for directory_view
-- The view itself doesn't have RLS, but it respects RLS on underlying tables
-- Password field visibility will be handled by a separate policy or function

-- Policy to hide passwords from public (except for favorited servers)
-- This is complex, so we'll handle it in application logic for MVP
-- For now, password is readable but frontend should gate it

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Servers indexes
CREATE INDEX idx_servers_owner ON servers(owner_user_id);
CREATE INDEX idx_servers_cluster ON servers(cluster_id);
CREATE INDEX idx_servers_status ON servers(effective_status, last_seen_at DESC);
CREATE INDEX idx_servers_created ON servers(created_at DESC);

-- Clusters indexes
CREATE INDEX idx_clusters_owner ON clusters(owner_user_id);
CREATE INDEX idx_clusters_slug ON clusters(slug);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clusters_updated_at
    BEFORE UPDATE ON clusters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_servers_updated_at
    BEFORE UPDATE ON servers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE profiles IS 'User profiles extending Supabase auth.users';
COMMENT ON TABLE clusters IS 'Server clusters (data-only MVP, pages in Phase 1.5)';
COMMENT ON TABLE servers IS 'Server listings with effective status fields';
COMMENT ON TABLE heartbeats IS 'Append-only events table for server status history';
COMMENT ON TABLE favorites IS 'Player favorites for servers';
COMMENT ON TABLE subscriptions IS 'Stripe subscription state (minimal MVP plumbing)';
COMMENT ON VIEW directory_view IS 'Public read model for directory - single source of truth for frontend';

COMMENT ON COLUMN servers.effective_status IS 'Current/active status for fast directory reads';
COMMENT ON COLUMN servers.status_source IS 'Source of status: manual or agent';
COMMENT ON COLUMN servers.confidence IS 'Optional confidence level (RYG logic in Sprint 2)';
COMMENT ON COLUMN clusters.public_fingerprint IS 'Hash/fingerprint of cluster public identity (no plaintext keys)';
COMMENT ON COLUMN subscriptions.key_quota_total IS 'Base included keys (e.g., 12)';
COMMENT ON COLUMN subscriptions.key_quota_additional IS 'Additional available keys (e.g., up to 8)';
COMMENT ON COLUMN subscriptions.key_quota_max IS 'Max total keys (e.g., 20)';
