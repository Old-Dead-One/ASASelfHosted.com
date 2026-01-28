# Database Migrations

Database schema is managed in Supabase, not in this codebase.

## Migration Process

1. Create your Supabase project
2. Run migrations (choose one method):
   - **CLI (Recommended)**: Use `psql` or Supabase CLI (see `CLI_RUN_GUIDE.md`)
   - **Dashboard**: Run migrations in Supabase SQL Editor (in order)
3. Document any schema changes here
4. Update Pydantic schemas to match database schema

**Quick CLI Example:**
```bash
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
psql "$DATABASE_URL" -f backend/app/db/migrations/012_security_fixes.sql
```

## Migration Files

### `001_sprint_0_schema.sql`
**Sprint 0 - Core Directory Schema**

Creates:
- `profiles` - User profiles extending Supabase auth.users
- `clusters` - Server clusters (data-only MVP)
- `servers` - Server listings with effective status fields
- `heartbeats` - Append-only events table for status history
- `favorites` - Player favorites
- `subscriptions` - Minimal Stripe subscription plumbing
- `directory_view` - Public read model for directory

**RLS Policies:**
- Public read for directory listings
- Owner-only writes for servers/clusters
- User-only access for favorites
- Service role for heartbeats/subscriptions (via FastAPI)

**To Run:**
1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `001_sprint_0_schema.sql`
3. Execute in SQL Editor
4. Verify tables and policies in Database → Tables

### `003_sprint_3_directory_view.sql`
**Sprint 3 - Directory Filtering & Ranking Foundation**

Extends Sprint 0 schema with:
- Enum types: `ruleset`, `game_mode`, `platform`
- New columns on `servers` table:
  - Stored metadata: `ruleset`, `game_mode`, `platforms`, `players_capacity`, `is_official_plus`, `is_crossplay`, `is_console`, `is_pc`, `is_verified`
  - Dynamic metrics (nullable): `players_current`, `quality_score`, `uptime_percent`
- Updated `directory_view` with all DirectoryServer fields (excluding rank_position/rank_delta_24h computed in backend)
- Performance indexes for filtering and sorting

**Key Changes:**
- `is_verified` is a real boolean column (NOT NULL DEFAULT FALSE), separate from `status_source`
- `platforms` is `platform[]` enum array (NOT NULL DEFAULT empty array)
- `mod_list` remains `text[]` in view for clean Supabase filtering
- Composite index `(updated_at DESC, id ASC)` for stable sorting

**To Run:**
1. Ensure `001_sprint_0_schema.sql` has been applied first
2. Open Supabase Dashboard → SQL Editor
3. Copy contents of `003_sprint_3_directory_view.sql`
4. Execute in SQL Editor
5. Verify:
   - New columns exist in `servers` table
   - `directory_view` has been updated
   - Indexes have been created

## Schema Decisions

### Status Model
- `servers` table holds current/effective status for fast directory reads
- `heartbeats` table holds append-only history/events
- This separation keeps directory queries fast while preserving history

### Clusters
- Data-only MVP (no cluster pages until Phase 1.5)
- Key metadata stored (fingerprints, versions) but no plaintext private keys
- Supports cluster association and "Verified Cluster" badge

### Subscriptions
- Minimal Stripe plumbing (webhook scaffolding)
- Quota fields included but not enforced in MVP
- Status tracking for subscription lifecycle

### Directory View
- Single source of truth for frontend directory queries
- Joins servers + clusters + profiles + favorite counts
- Computes badge flags (verified, new, stable, pvp/pve, vanilla/boosted)
- Password visibility handled by RLS (favorited servers can see password)

### `013_sprint_6_hosting_provider.sql`
**Sprint 6 - Hosting Provider (Block Official/Nitrado)**

- Adds `hosting_provider` to `servers`: `self_hosted` | `nitrado` | `official` | `other_managed`.
- `NOT NULL DEFAULT 'self_hosted'`, CHECK constraint, index.
- Updates `directory_view`: `WHERE s.hosting_provider = 'self_hosted'`. Column **not** exposed in view/API/UI.
- Backfill: resets any `nitrado`/`official`/`other_managed` rows to `self_hosted`.
- **Create/update validation:** API rejects `hosting_provider` other than `self_hosted`. Use message: "ASASelfHosted lists self-hosted servers only."

**To Run:**
1. Run after `012_security_fixes.sql`.
2. See `013_sprint_6_hosting_provider_VERIFY.md` for verification.

### `012_security_fixes.sql`
**Security Fixes - Critical Security Boundary Fixes**

Fixes two critical security issues:

1. **join_password moved to owner-only table:**
   - Creates `server_secrets` table for owner-only sensitive data
   - Migrates existing `join_password` from `servers` to `server_secrets`
   - Drops `join_password` column from `servers` table
   - Revokes direct SELECT on `servers` table from anon (public must use `directory_view`)

2. **heartbeat payload/signature restricted:**
   - Creates `heartbeats_public` view (excludes `payload` and `signature`)
   - Revokes direct SELECT on `heartbeats` table from anon
   - Public must use `heartbeats_public` view (respects RLS for recent heartbeats)
   - Owners and service-role can still access full `heartbeats` table

**Security Impact:**
- Anon key can no longer read `join_password` (moved to `server_secrets`)
- Anon key can no longer read `heartbeats.payload` or `heartbeats.signature`
- Public access restricted to sanitized views only

**To Run:**
1. Ensure all previous migrations have been applied
2. Open Supabase Dashboard → SQL Editor
3. Copy contents of `012_security_fixes.sql`
4. Execute in SQL Editor
5. Verify:
   - `server_secrets` table created with RLS policies
   - `join_password` column removed from `servers` table
   - `heartbeats_public` view created
   - Direct SELECT revoked on `servers` and `heartbeats` from anon
   - Test with anon key: `SELECT join_password FROM servers` should fail
   - Test with anon key: `SELECT payload, signature FROM heartbeats` should fail
   - Test with anon key: `SELECT * FROM heartbeats_public` should work (recent only)

### `006_sprint_4_agent_auth.sql`
**Sprint 4 - Agent Authentication & Heartbeat Pipeline**

Adds agent authentication infrastructure:
- **Clusters table extensions:**
  - `public_key_ed25519` - Base64 Ed25519 public key for signature verification
  - `heartbeat_grace_seconds` - Per-cluster grace window override
- **Heartbeats table extensions:**
  - `key_version` - Key version for rotation tracking
  - `heartbeat_id` - UUID for replay protection
  - `players_current`, `players_capacity` - Canonical player fields (legacy fields kept for compatibility)
  - `UNIQUE(server_id, heartbeat_id)` constraint for replay protection
- **Servers table extensions:**
  - `last_heartbeat_at` - Agent-reported timestamp (distinct from `last_seen_at`)
- **Heartbeat jobs table:**
  - Durable queue table for async heartbeat processing
  - Row-level claiming via `claimed_at` timestamp
  - One pending job per server (partial unique constraint)

**Key Features:**
- Ed25519 signature verification (cluster-based, not agent token-based)
- Replay protection via unique constraint
- Durable worker queue (table-based, not BackgroundTasks)
- Grace window: env default + per-cluster override

**To Run:**
1. Ensure `001_sprint_0_schema.sql` and `003_sprint_3_directory_view.sql` have been applied first
2. Open Supabase Dashboard → SQL Editor
3. Copy contents of `006_sprint_4_agent_auth.sql`
4. Execute in SQL Editor
5. Verify:
   - New columns exist in `clusters`, `heartbeats`, `servers` tables
   - `heartbeat_jobs` table created
   - Indexes and constraints created

## Next Steps

After running migrations:
1. Verify RLS policies are active
2. Test public read access to `directory_view`
3. Test owner write access to `servers`
4. Test heartbeat endpoint with Ed25519 signature
5. Verify worker can process heartbeat jobs
6. Update Pydantic schemas to match database schema
7. Create TypeScript types for `DirectoryServer` contract
