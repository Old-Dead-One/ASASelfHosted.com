## SPRINT_CLEANUP_ONE (finish missing items + align Sprint 1–5)

### Goal

Make the backend + DB schema + docs consistent with the Sprint 1–5 design intent, and close the gaps that cause correctness/security/ranking issues.

---

## 1) Database “truth alignment” (must-do)

### 1.1 Favorites de-dupe

**Task**

* Add constraint: `UNIQUE(user_id, server_id)` on `public.favorites`.

**Acceptance**

* Attempting to insert a duplicate favorite for the same user/server fails.
* Favorites count queries are stable (no double counting).

---

### 1.2 Cluster agent-auth fields (Sprint 4)

**Task**

* Ensure `public.clusters` contains:

  * `public_key_ed25519 text`
  * `heartbeat_grace_seconds integer`

**Acceptance**

* Cluster can store verification key + grace window.
* Heartbeat verification logic can look up key/grace per cluster without fallback hacks.

---

### 1.3 Heartbeat replay protection + canonical player fields (Sprint 4)

**Task**

* Ensure `public.heartbeats` contains:

  * `key_version integer`
  * `heartbeat_id text` (or uuid/text—must match code)
  * `players_current integer`
  * `players_capacity integer`
* Decide whether to keep legacy fields (`player_count`, `max_players`) and map them.

**Acceptance**

* Duplicate/replayed heartbeats are rejected or safely ignored (unique index or dedupe logic).
* The “current/capacity” fields your directory uses come from canonical columns.

---

### 1.4 Server last_heartbeat_at (Sprint 4)

**Task**

* Ensure `public.servers.last_heartbeat_at timestamptz` exists.

**Acceptance**

* Directory can distinguish “agent says it’s fresh” vs “backend saw it late.”
* Confidence/scoring can use this.

---

### 1.5 Column types cleanup (avoid future pain)

**Task**

* Make sure array columns are typed:

  * `servers.mod_list text[]`
  * `servers.platforms platform[] DEFAULT '{}'::platform[]`

**Acceptance**

* PostgREST filters work predictably.
* No implicit casts or random client-side weirdness.

---

## 2) Indexes & constraints (high leverage)

### 2.1 Heartbeats query performance

**Task**

* Add indexes commonly needed:

  * `heartbeats(server_id, received_at desc)`
  * `servers(cluster_id)`
  * `servers(effective_status)`
  * optional: `servers(ranking_score desc)` if you sort by it often

**Acceptance**

* Directory list endpoints don’t degrade as heartbeats grow.

---

### 2.2 Heartbeat dedupe key (if used)

**Task**

* If `heartbeat_id` is your replay guard, enforce uniqueness:

  * `UNIQUE(server_id, heartbeat_id)` (or global unique if that’s your contract)

**Acceptance**

* Same heartbeat cannot be stored twice.

---

## 3) Backend contract cleanup (code + schema match)

### 3.1 One canonical model for “players”

**Task**

* Decide the canonical fields:

  * `players_current`, `players_capacity`
* Map agent payload fields to these.
* Deprecate legacy names internally (still accept from payload if needed).

**Acceptance**

* Directory always reads from canonical columns.
* Agent payload variations don’t break your stats pipeline.

---

### 3.2 “last seen” semantics are consistent

**Task**

* Confirm meanings:

  * `servers.last_seen_at` = backend received time (DB now)
  * `servers.last_heartbeat_at` = agent timestamp (payload)
* Ensure update logic sets both correctly.

**Acceptance**

* A delayed heartbeat shows “received late” but still indicates agent time.

---

## 4) RLS / security sanity pass (don’t ship without this)

### 4.1 Public directory access

**Task**

* Confirm policies allow:

  * Public read of public clusters/servers as intended
  * No public access to secrets (`join_password`, private fields, etc.)

**Acceptance**

* Anonymous can list public servers (if intended).
* Anonymous cannot read `join_password` or private cluster fields.

---

### 4.2 Owner controls

**Task**

* Confirm policies allow owners to:

  * CRUD their servers
  * Manage their clusters
  * Manage favorites (per-user)

**Acceptance**

* No cross-user access is possible via PostgREST.

---

## 5) Docs & “single source of truth” update

### 5.1 Consolidated reference schema (documentation-only)

**Task**

* Generate a `docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md` (or `.sql` marked non-executable) that reflects the real migrations + enums + indexes.

**Acceptance**

* Anyone reviewing can compare code/migrations to one doc and stop guessing.

---

### 5.2 Sprint closure notes

**Task**

* Add `SPRINT_CLEANUP_ONE.md` with:

  * What changed (constraints/columns/indexes/policies)
  * Upgrade notes
  * Backfill notes (if any)

**Acceptance**

* Future-you doesn’t have to rediscover this in six weeks.

---

## 6) Backfills (only if you already have data)

### 6.1 Populate new canonical player fields

**Task**

* If you already have `player_count/max_players`, backfill:

  * `players_current = COALESCE(players_current, player_count)`
  * `players_capacity = COALESCE(players_capacity, max_players)`

**Acceptance**

* Ranking/uptime doesn’t drop to null due to new columns.

---

## Deliverable checklist (what “done” looks like)

* [x] Migrations exist for all schema changes above
  * ✅ 010_sprint_cleanup_one.sql - Missing indexes and constraint verification
  * ✅ 011_sprint_cleanup_one_backfill.sql - Backfill canonical fields (optional, only if needed)
* [x] RLS policies verified against intended access model
  * ✅ Public directory access confirmed (directory_view, public clusters/servers)
  * ✅ Owner controls confirmed (CRUD own servers/clusters/favorites)
  * ✅ Protected fields confirmed (join_password, private cluster fields)
* [x] Directory endpoints return stable results (no dup favorites, no null players)
  * ✅ UNIQUE(user_id, server_id) constraint on favorites
  * ✅ Canonical player fields (players_current, players_capacity) used throughout
* [x] Heartbeat ingestion enforces dedupe/replay protection
  * ✅ UNIQUE(server_id, heartbeat_id) constraint on heartbeats
  * ✅ Backend code uses canonical fields
* [x] Reference schema doc updated
  * ✅ docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md created with complete schema reference
