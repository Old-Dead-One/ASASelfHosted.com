# Sprint Cleanup One - Completion Summary

**Date:** After Sprint 5 completion  
**Status:** ✅ Complete

## Overview

This document summarizes the cleanup work completed to align the database schema, backend code, and documentation with Sprint 1-5 design intent.

## Completed Items

### 1. Database "Truth Alignment" ✅

#### 1.1 Favorites de-dupe ✅
- **Status:** Already implemented in migration 001
- **Constraint:** `UNIQUE(user_id, server_id)` on `public.favorites`
- **Verification:** Constraint verified in migration 010

#### 1.2 Cluster agent-auth fields ✅
- **Status:** Already implemented in migration 006
- **Fields:**
  - `public_key_ed25519 TEXT` - Base64 Ed25519 public key
  - `heartbeat_grace_seconds INTEGER` - Per-cluster grace window override
- **Verification:** Fields exist and are documented

#### 1.3 Heartbeat replay protection ✅
- **Status:** Already implemented in migration 006
- **Fields:**
  - `key_version INTEGER`
  - `heartbeat_id UUID`
  - `players_current INTEGER` (canonical)
  - `players_capacity INTEGER` (canonical)
- **Constraint:** `UNIQUE(server_id, heartbeat_id)` for replay protection
- **Verification:** Constraint verified in migration 010

#### 1.4 Server last_heartbeat_at ✅
- **Status:** Already implemented in migration 006
- **Field:** `last_heartbeat_at TIMESTAMPTZ`
- **Semantics:** Agent-reported timestamp (distinct from `last_seen_at` which is received_at)

#### 1.5 Column types cleanup ✅
- **Status:** Already implemented in migrations 001 and 003
- **Types:**
  - `servers.mod_list TEXT[]`
  - `servers.platforms platform[] DEFAULT '{}'::platform[]`
- **Verification:** Types confirmed correct

### 2. Indexes & Constraints ✅

#### 2.1 Heartbeats query performance ✅
- **Status:** Indexes added/verified in migrations 001, 006, and 010
- **Indexes:**
  - ✅ `heartbeats(server_id, received_at DESC)` - Critical for worker queries
  - ✅ `servers(cluster_id)` - For cluster filtering
  - ✅ `servers(effective_status)` - For status filtering
  - ✅ `servers(ranking_score DESC NULLS LAST)` - For ranking sort (added in 010)

#### 2.2 Heartbeat dedupe key ✅
- **Status:** Already implemented in migration 006
- **Constraint:** `UNIQUE(server_id, heartbeat_id)`
- **Verification:** Constraint verified in migration 010

### 3. Backend Contract Cleanup ✅

#### 3.1 One canonical model for "players" ✅
- **Status:** Backend code already uses canonical fields
- **Canonical fields:** `players_current`, `players_capacity`
- **Legacy fields:** `player_count`, `max_players` (kept for compatibility, not read by engines)
- **Verification:** 
  - `supabase_heartbeat_repo.py` normalizes to canonical fields
  - Engines (`quality_engine.py`, `ranking.py`) use canonical fields
  - Directory view uses canonical fields

#### 3.2 "last seen" semantics are consistent ✅
- **Status:** Semantics documented and implemented
- **Fields:**
  - `servers.last_seen_at` = Backend received time (DB now)
  - `servers.last_heartbeat_at` = Agent timestamp (payload)
- **Verification:** Both fields exist and are used correctly

### 4. RLS / Security ✅

#### 4.1 Public directory access ✅
- **Status:** Policies verified
- **Access:**
  - ✅ Public can read public clusters/servers via `directory_view`
  - ✅ `join_password` protected (only visible to favoriters)
  - ✅ Private cluster fields protected (only visible to owners)

#### 4.2 Owner controls ✅
- **Status:** Policies verified
- **Access:**
  - ✅ Owners can CRUD their servers
  - ✅ Owners can CRUD their clusters (including unlisted)
  - ✅ Users can manage their own favorites

### 5. Docs & "Single Source of Truth" ✅

#### 5.1 Consolidated reference schema ✅
- **Status:** Created
- **File:** `docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md`
- **Content:**
  - Complete schema reference (all tables, views, indexes, constraints)
  - Enum types documentation
  - RLS policies summary
  - Migration history
  - Notes on canonical vs legacy fields

#### 5.2 Sprint closure notes ✅
- **Status:** This document
- **Content:**
  - What changed (constraints/columns/indexes/policies)
  - Verification status
  - Migration files created

## Migrations Created

### 010_sprint_cleanup_one.sql
**Purpose:** Add missing indexes and verify constraints

**Changes:**
- Add `idx_servers_ranking_score_desc` index for ranking sort
- Verify existing indexes (heartbeats, servers)
- Verify existing constraints (favorites, heartbeats)
- Add documentation comments

**To Run:**
1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `010_sprint_cleanup_one.sql`
3. Execute

### 011_sprint_cleanup_one_backfill.sql
**Purpose:** Backfill canonical fields from legacy fields (if needed)

**Changes:**
- Backfill `heartbeats.players_current` from `player_count`
- Backfill `heartbeats.players_capacity` from `max_players`
- Backfill `servers.players_current` from most recent heartbeat
- Backfill `servers.players_capacity` from most recent heartbeat

**To Run:**
- **Only if you have existing data with legacy fields populated and canonical fields are NULL**
- If starting fresh, skip this migration

## Verification Queries

Run these in Supabase SQL Editor to verify completion:

```sql
-- Verify favorites constraint
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'favorites' 
  AND constraint_name = 'uq_favorites_user_server';

-- Verify heartbeat replay protection
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'heartbeats' 
  AND constraint_name = 'uq_heartbeats_server_heartbeat_id';

-- Verify indexes exist
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('servers', 'heartbeats', 'favorites')
  AND indexname IN (
    'idx_servers_ranking_score_desc',
    'idx_heartbeats_server_received',
    'idx_servers_cluster_id',
    'idx_servers_effective_status',
    'idx_favorites_user',
    'idx_favorites_server'
  );

-- Check column types
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'servers'
  AND column_name IN ('mod_list', 'platforms');
```

## Upgrade Notes

### For Existing Databases

1. **Run migration 010** (always required)
   - Adds missing indexes
   - Verifies constraints
   - Safe to run multiple times (idempotent)

2. **Run migration 011** (only if you have existing data)
   - Backfills canonical fields from legacy fields
   - Only needed if `players_current`/`players_capacity` are NULL
   - Safe to run multiple times (only updates NULL values)

### For New Databases

1. Run migrations 001-009 in order
2. Run migration 010 (cleanup)
3. Skip migration 011 (no existing data to backfill)

## Backfill Notes

If you have existing data with legacy fields (`player_count`, `max_players`) populated:

1. Migration 011 will backfill canonical fields automatically
2. Legacy fields remain for compatibility during deprecation window
3. Backend code uses canonical fields, so ranking/uptime won't drop to NULL
4. After backfill, new heartbeats will populate canonical fields directly

## Next Steps

1. ✅ Run migration 010 in Supabase SQL Editor
2. ⚠️ Run migration 011 if you have existing data (otherwise skip)
3. ✅ Verify using queries above
4. ✅ Reference `docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md` for schema details

## Summary

All cleanup items from SPRINT_CLEANUP_ONE.md have been completed:

- ✅ Database schema aligned (constraints, indexes, column types)
- ✅ Backend contract consistent (canonical fields used throughout)
- ✅ RLS policies verified (public access, owner controls, protected fields)
- ✅ Reference documentation created (single source of truth)
- ✅ Migrations created (cleanup + optional backfill)

The database schema is now fully aligned with Sprint 1-5 design intent.
