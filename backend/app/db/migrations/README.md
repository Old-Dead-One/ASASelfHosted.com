# Database Migrations

Database schema is managed in Supabase, not in this codebase.

## Migration Process

1. Create your Supabase project
2. Run migrations in Supabase SQL Editor (in order)
3. Document any schema changes here
4. Update Pydantic schemas to match database schema

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

## Next Steps

After running migrations:
1. Verify RLS policies are active
2. Test public read access to `directory_view`
3. Test owner write access to `servers`
4. Update Pydantic schemas to match database schema
5. Create TypeScript types for `DirectoryServer` contract
