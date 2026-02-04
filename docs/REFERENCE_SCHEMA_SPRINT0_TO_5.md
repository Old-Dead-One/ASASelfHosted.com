# Reference Schema: Sprint 0 to Sprint 5

**WARNING: This schema is for reference only and is not meant to be executed.**
**It represents the cumulative state after all migrations 001-010 have been applied.**

**Current schema:** For up-to-date schema and migrations, see **backend/app/db/migrations/** and **backend/app/db/migrations/README.md**. This doc is a historical reference (Sprint 0–5 baseline).

This document provides a single source of truth for the database schema after Sprint 5 completion.

## Table of Contents

1. [Enum Types](#enum-types)
2. [Tables](#tables)
   - [profiles](#profiles)
   - [clusters](#clusters)
   - [servers](#servers)
   - [heartbeats](#heartbeats)
   - [heartbeat_jobs](#heartbeat_jobs)
   - [favorites](#favorites)
   - [subscriptions](#subscriptions)
3. [Views](#views)
   - [directory_view](#directory_view)
4. [Indexes](#indexes)
5. [Constraints](#constraints)
6. [RLS Policies](#rls-policies)

---

## Enum Types

```sql
-- Server status
CREATE TYPE server_status AS ENUM ('online', 'offline', 'unknown');

-- Status source (how status was determined)
CREATE TYPE status_source AS ENUM ('manual', 'agent');

-- Cluster visibility
CREATE TYPE cluster_visibility AS ENUM ('public', 'unlisted');

-- Server ruleset classification
CREATE TYPE ruleset AS ENUM ('vanilla', 'vanilla_qol', 'boosted', 'modded');

-- Game mode
CREATE TYPE game_mode AS ENUM ('pvp', 'pve', 'pvpve');

-- Platform
CREATE TYPE platform AS ENUM ('steam', 'xbox', 'playstation', 'windows_store', 'epic');
```

---

## Tables

### profiles

User profiles extending Supabase auth.users.

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**RLS:** Users can read/update their own profile.

---

### clusters

Server clusters (data-only MVP). Cluster pages come in Phase 1.5.

```sql
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    owner_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    visibility cluster_visibility NOT NULL DEFAULT 'public',
    
    -- Key metadata (no plaintext private keys)
    key_version INTEGER NOT NULL DEFAULT 1,
    public_fingerprint TEXT,  -- Hash/fingerprint of cluster public identity
    public_key_ed25519 TEXT,  -- Base64-encoded Ed25519 public key (Sprint 4)
    heartbeat_grace_seconds INTEGER,  -- Per-cluster grace window override (Sprint 4)
    
    rotated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Key Fields:**
- `public_key_ed25519`: Base64-encoded Ed25519 public key for agent signature verification
- `heartbeat_grace_seconds`: Per-cluster grace window override (falls back to env default if NULL)

**RLS:** Public clusters readable by everyone. Owners can CRUD their own clusters (including unlisted).

---

### servers

Core server listings with effective status fields and derived metrics.

```sql
CREATE TABLE servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES clusters(id) ON DELETE SET NULL,
    
    -- Core listing fields
    name TEXT NOT NULL,
    description TEXT,
    map_name TEXT,
    join_address TEXT,
    join_password TEXT,  -- Protected by RLS (only visible to favoriters)
    join_instructions_pc TEXT,
    join_instructions_console TEXT,
    mod_list TEXT[],  -- Array of mod IDs or names
    rates TEXT,
    wipe_info TEXT,
    
    -- Legacy flags (deprecated, use ruleset/game_mode instead)
    pvp_enabled BOOLEAN DEFAULT false,
    vanilla BOOLEAN DEFAULT false,
    
    -- Status fields
    effective_status server_status NOT NULL DEFAULT 'unknown',
    status_source status_source,
    last_seen_at TIMESTAMPTZ,  -- Backend received time (DB now)
    last_heartbeat_at TIMESTAMPTZ,  -- Agent-reported timestamp (Sprint 4)
    confidence TEXT,  -- RYG: 'green', 'yellow', 'red'
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Classification (Sprint 3)
    ruleset ruleset,
    game_mode game_mode,
    platforms platform[] NOT NULL DEFAULT '{}'::platform[],
    
    -- Feature flags (Sprint 3)
    is_official_plus BOOLEAN,
    is_crossplay BOOLEAN,
    is_console BOOLEAN,
    is_pc BOOLEAN,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Player stats (canonical fields)
    players_capacity INTEGER,  -- Maximum player capacity (static)
    players_current INTEGER,  -- Current player count (nullable, updated from heartbeats)
    
    -- Derived metrics (Sprint 2-5)
    quality_score DOUBLE PRECISION,  -- 0-100
    uptime_percent DOUBLE PRECISION,  -- 0-100
    ranking_score DOUBLE PRECISION,  -- Higher = better rank (Sprint 5)
    ranking_updated_at TIMESTAMPTZ,  -- When ranking_score was computed (Sprint 5)
    
    -- Anomaly detection (Sprint 5)
    anomaly_players_spike BOOLEAN,  -- True if spike detected, False if cleared, NULL if never set
    anomaly_last_detected_at TIMESTAMPTZ  -- Timestamp of last detected anomaly
);
```

**Key Fields:**
- `last_seen_at`: Backend received time (when heartbeat was received by DB)
- `last_heartbeat_at`: Agent-reported timestamp (from heartbeat payload)
- `players_current`, `players_capacity`: Canonical player fields (use these, not legacy)
- `ranking_score`: Computed ranking score with anti-gaming guards (Sprint 5)

**RLS:** Public servers readable by everyone (via directory_view). Owners can CRUD their own servers. `join_password` only visible to favoriters.

---

### heartbeats

Append-only events table for server status history.

```sql
CREATE TABLE heartbeats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    source status_source NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Agent authentication (Sprint 4)
    key_version INTEGER,  -- Key version used for signature
    heartbeat_id UUID,  -- UUID for replay protection
    signature TEXT,  -- Ed25519 signature
    
    -- Status and metadata
    status server_status,
    agent_version TEXT,
    map_name TEXT,
    
    -- Player fields (canonical)
    players_current INTEGER,  -- Canonical field (use this)
    players_capacity INTEGER,  -- Canonical field (use this)
    
    -- Legacy player fields (for compatibility during deprecation)
    player_count INTEGER,  -- Legacy: maps to players_current
    max_players INTEGER,  -- Legacy: maps to players_capacity
    
    -- Flexible payload
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Replay protection constraint
    CONSTRAINT uq_heartbeats_server_heartbeat_id UNIQUE(server_id, heartbeat_id)
);
```

**Key Fields:**
- `players_current`, `players_capacity`: Canonical fields (use these)
- `heartbeat_id`: UUID for replay protection (unique per server_id)
- `key_version`: Matches clusters.key_version for signature verification

**RLS:** Public can read recent heartbeats (24h). Owners can read all heartbeats for their servers. Only backend service role can insert.

---

### heartbeat_jobs

Durable queue table for async heartbeat processing.

```sql
CREATE TABLE heartbeat_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    enqueued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    claimed_at TIMESTAMPTZ NULL,  -- Row-level claiming: set when worker claims job
    processed_at TIMESTAMPTZ NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Partial unique constraint: one pending job per server
    CONSTRAINT idx_heartbeat_jobs_pending_unique UNIQUE(server_id) 
        WHERE processed_at IS NULL
);
```

**RLS:** Only backend service role can insert/update. Owners can read jobs for their servers.

---

### favorites

Player favorites for servers.

```sql
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Prevent duplicate favorites
    CONSTRAINT uq_favorites_user_server UNIQUE(user_id, server_id)
);
```

**RLS:** Users can read/create/delete their own favorites.

---

### subscriptions

Stripe subscription state (minimal MVP plumbing).

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT UNIQUE,
    status USER-DEFINED NOT NULL,  -- Stripe subscription status enum
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT false,
    key_quota_total INTEGER NOT NULL DEFAULT 12,
    key_quota_additional INTEGER NOT NULL DEFAULT 8,
    key_quota_max INTEGER NOT NULL DEFAULT 20,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**RLS:** Users can read their own subscriptions. Only backend service role can update (via webhooks).

---

## Views

### directory_view

Public read model for directory. Provides persisted fields for DirectoryServer schema.

**Key Features:**
- COALESCE for nullable sort columns (players_current, quality_score, uptime_percent, ranking_score) ensures deterministic cursor pagination
- mod_list and platforms never NULL (COALESCE to empty arrays)
- Favorite count computed via LATERAL join
- Badge flags computed (is_new, is_stable, is_modded)

**Sort Columns (COALESCE to 0 for pagination):**
- `players_current`: COALESCE(s.players_current, 0)
- `quality_score`: COALESCE(s.quality_score, 0.0)
- `uptime_percent`: COALESCE(s.uptime_percent, 0.0)
- `ranking_score`: COALESCE(s.ranking_score, 0.0)

**RLS:** Public read access (no RLS on views, inherits from underlying tables).

---

## Indexes

### Performance Indexes

```sql
-- Servers
CREATE INDEX idx_servers_owner ON servers(owner_user_id);
CREATE INDEX idx_servers_cluster ON servers(cluster_id) WHERE cluster_id IS NOT NULL;
CREATE INDEX idx_servers_status ON servers(effective_status, last_seen_at DESC);
CREATE INDEX idx_servers_created ON servers(created_at DESC);
CREATE INDEX idx_servers_updated_at_id_desc ON servers(updated_at DESC, id ASC);
CREATE INDEX idx_servers_ruleset ON servers(ruleset);
CREATE INDEX idx_servers_game_mode ON servers(game_mode);
CREATE INDEX idx_servers_effective_status ON servers(effective_status);
CREATE INDEX idx_servers_is_verified ON servers(is_verified) WHERE is_verified IS TRUE;
CREATE INDEX idx_servers_players_current ON servers(players_current) WHERE players_current IS NOT NULL;
CREATE INDEX idx_servers_ranking_score_desc ON servers(ranking_score DESC NULLS LAST) WHERE ranking_score IS NOT NULL;

-- Heartbeats
CREATE INDEX idx_heartbeats_server_received ON heartbeats(server_id, received_at DESC);
CREATE INDEX idx_heartbeats_received_at ON heartbeats(received_at DESC);
CREATE INDEX idx_heartbeats_heartbeat_id ON heartbeats(heartbeat_id) WHERE heartbeat_id IS NOT NULL;

-- Clusters
CREATE INDEX idx_clusters_owner ON clusters(owner_user_id);
CREATE INDEX idx_clusters_slug ON clusters(slug);
CREATE INDEX idx_clusters_heartbeat_grace ON clusters(heartbeat_grace_seconds) WHERE heartbeat_grace_seconds IS NOT NULL;

-- Favorites
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_server ON favorites(server_id);

-- Heartbeat Jobs
CREATE INDEX idx_heartbeat_jobs_pending ON heartbeat_jobs(processed_at, enqueued_at) WHERE processed_at IS NULL AND claimed_at IS NULL;
CREATE INDEX idx_heartbeat_jobs_claimed ON heartbeat_jobs(claimed_at) WHERE claimed_at IS NOT NULL AND processed_at IS NULL;
```

---

## Constraints

### Unique Constraints

```sql
-- Favorites: one favorite per user per server
ALTER TABLE favorites ADD CONSTRAINT uq_favorites_user_server UNIQUE(user_id, server_id);

-- Heartbeats: replay protection (one heartbeat_id per server)
ALTER TABLE heartbeats ADD CONSTRAINT uq_heartbeats_server_heartbeat_id UNIQUE(server_id, heartbeat_id);

-- Clusters: unique slug
ALTER TABLE clusters ADD CONSTRAINT clusters_slug_key UNIQUE(slug);

-- Subscriptions: unique user_id and stripe_subscription_id
ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_id_key UNIQUE(user_id);
ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_stripe_subscription_id_key UNIQUE(stripe_subscription_id);
```

### Partial Unique Constraints

```sql
-- Heartbeat Jobs: one pending job per server
CREATE UNIQUE INDEX idx_heartbeat_jobs_pending_unique 
    ON heartbeat_jobs(server_id) 
    WHERE processed_at IS NULL;
```

---

## RLS Policies

### Public Directory Access

- **directory_view**: Public read access (no RLS on views)
- **servers**: Public can read via directory_view (RLS on underlying table allows owner access)
- **clusters**: Public can read public clusters (visibility = 'public')

### Protected Fields

- **servers.join_password**: Only visible to users who favorited the server
- **clusters.public_key_ed25519**: Only visible to cluster owners
- **heartbeats.signature**: Only visible to owners and recent public reads (24h)

### Owner Controls

- **servers**: Owners can CRUD their own servers
- **clusters**: Owners can CRUD their own clusters (including unlisted)
- **favorites**: Users can CRUD their own favorites
- **profiles**: Users can read/update their own profile

### Service Role Only

- **heartbeats**: Only backend service role can insert (via FastAPI)
- **heartbeat_jobs**: Only backend service role can insert/update
- **subscriptions**: Only backend service role can update (via webhooks)

---

## Migration History

1. **001_sprint_0_schema.sql**: Core schema (profiles, clusters, servers, heartbeats, favorites, subscriptions, directory_view)
2. **003_sprint_3_directory_view.sql**: Classification fields (ruleset, game_mode, platforms), feature flags, derived metrics
3. **006_sprint_4_agent_auth.sql**: Agent authentication (public_key_ed25519, heartbeat_grace_seconds, key_version, heartbeat_id, players_current, players_capacity, last_heartbeat_at, heartbeat_jobs)
4. **007_sprint_5_anomaly_detection.sql**: Anomaly detection fields (anomaly_players_spike, anomaly_last_detected_at)
5. **008_sprint_5_directory_view_null_coalesce.sql**: NULL coalesce for cursor pagination
6. **009_sprint_5_ranking_score.sql**: Ranking score fields (ranking_score, ranking_updated_at)
7. **010_sprint_cleanup_one.sql**: Missing indexes and constraint verification

---

## Notes

### Canonical vs Legacy Fields

**Use these canonical fields:**
- `players_current`, `players_capacity` (not `player_count`, `max_players`)
- `uptime_percent` (not `uptime_24h`)
- `rank_position` (not `rank`)

**Legacy fields are kept for compatibility during deprecation window but should not be read by engines.**

### Cursor Pagination

Sort columns in `directory_view` are COALESCEd to 0 to ensure deterministic pagination:
- NULL values don't break cursor pagination
- Pages ending on NULL don't skip rows
- Consistent ordering across requests

### Replay Protection

Heartbeat replay protection via `UNIQUE(server_id, heartbeat_id)`:
- Same heartbeat_id, same server → idempotent (returns replay=True)
- Same heartbeat_id, different server → rejected (DB constraint violation)
- NULL heartbeat_id allowed for legacy heartbeats (but agents should always send it)

---

**Last Updated:** After Sprint 5 completion (migration 010)
