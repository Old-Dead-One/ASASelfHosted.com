# ASASelfHosted.com — **Sprint 2 Playbook**

**Title:** Directory Filtering, Ranking Contracts & Supabase Read Model Foundation
**Goal:** Lock backend contracts and data seams for large-scale directory filtering and ranking without implementing full complexity yet.

---

## Sprint 2 Objectives (Non-Negotiable)

By the end of Sprint 2:

1. **Backend accepts the full filter & ranking vocabulary** the frontend will eventually expose
2. **GET /directory/servers remains simple, cacheable, and stable**
3. **Advanced boolean logic is reserved, not implemented**
4. **Supabase read model (`directory_view`) is introduced (even if stubbed)**
5. **No breaking API changes required in Sprint 3–4**

---

## Scope Guardrails

**In scope**

* Filter & rank *contracts*
* Basic filter implementation
* Ranking scaffolding
* Facets endpoint
* Supabase directory repository (read-only)

**Out of scope**

* AND / OR / NOT boolean logic
* Geo-distance calculations
* Trending math & rank deltas
* Write paths (server CRUD, heartbeat logic)

---

## Phase 2.1 — Lock the Directory Query Contract

### Endpoint (existing, expanded)

```
GET /api/v1/directory/servers
```

### Required Query Parameters (add now)

#### Pagination

* `page` (int, default 1)
* `page_size` (int, default 50, max 100)

#### Search

* `q` (string | null)

#### Ranking

* `rank_by` (enum, default: `updated`)

  * `players`
  * `favorites`
  * `quality`
  * `uptime`
  * `new`
  * `updated`
* `order` (enum: `asc | desc`, default: `desc`)

> ⚠️ Only **one or two rankings need to work** in Sprint 2. The rest may be accepted but ignored internally.

---

### Filters — Simple First (Implement These)

#### Status

* `status: online | offline | unknown`

#### Core Server Traits

* `game_mode: pve | pvp`
* `server_type: vanilla | boosted`
* `cluster_visibility: public | unlisted`
* `cluster_id: string | null`

#### Players

* `players_min: int | null`
* `players_max: int | null`

---

### Tri-State Toggles (Critical — Do Not Skip)

These **must be tri-state**, not booleans.

* `official: any | true | false`
* `modded: any | true | false`
* `crossplay: any | true | false`
* `console: any | true | false`

**Rule:**

* `any` → no filtering
* `true` → include only matching
* `false` → exclude matching

This matches the Steam-style UI exactly and prevents future refactors.

---

### Multi-Select Filters (OR semantics only for now)

* `maps: list[str]`
* `mods: list[str]`
* `platforms: list[str]`

> ⚠️ **No AND / OR / NOT yet.** These are treated as simple `IN (...)`.

---

## Phase 2.2 — Schema Extensions (Backward-Compatible)

### `DirectoryServer` (add fields, nullable)

Add **now**, populate later:

```py
quality_score: float | None = None
uptime_percent: float | None = None
players_current: int | None = None
players_max: int | None = None

rank_position: int | None = None
rank_delta_24h: int | None = None  # for trending arrows
```

> These fields unlock:

* Rankings
* Trend arrows
* Table-style list views
* Sorting without refactors

---

## Phase 2.3 — Facets Endpoint (Frontend Enabler)

### New Endpoint

```
GET /api/v1/directory/filters
```

### Response Contract

```json
{
  "maps": ["The Island", "Ragnarok", "Extinction"],
  "mods": ["S+ Structures", "Dino Storage v2"],
  "platforms": ["steam", "xbox", "playstation"],
  "server_types": ["vanilla", "boosted"],
  "game_modes": ["pve", "pvp"],
  "statuses": ["online", "offline", "unknown"]
}
```

**Rules**

* Data comes from directory_view or derived tables
* Frontend must not hardcode options
* Order does not matter

---

## Phase 2.4 — Supabase Read Model Introduction

### directory_view (Sprint 2 version)

You do **not** need final SQL yet, but the shape must exist.

Minimum requirements:

* One row per server
* Already denormalized
* Public-safe only
* Sortable fields included

Must include:

* server identity
* status & timestamps
* cluster info
* player counts
* flags (verified, modded, crossplay, official)
* ranking inputs (even if null)

---

## Phase 2.5 — Repository Layer

### New Repository

```
SupabaseDirectoryRepository
```

Responsibilities:

* Translate query params → SQL
* Enforce **read-only**
* Never return private fields
* Fail fast if misconfigured in non-local env

Mock repo stays for local/dev until fully wired.

---

## Phase 2.6 — Ranking Rules (Minimal Implementation)

### Implement **one** real ranking:

* `updated` (ORDER BY updated_at DESC)

### Accept but ignore others safely:

* `players`
* `favorites`
* `quality`
* `uptime`

> API must not error if requested; just fallback deterministically.

---

## Phase 2.7 — Explicitly Reserve Advanced Search

### Add (stub only)

```
POST /api/v1/directory/servers/search
```

Return:

* `501 Not Implemented`
* Clear message: “Advanced boolean filtering coming soon”

This **locks the future API** and prevents bad workarounds.

---

## Phase 2.8 — Non-Goals (Write These Down)

Do **not** implement:

* AND / OR / NOT logic
* Geo distance
* Trend math
* Time-series tables
* Write endpoints touching directory_view

---

## Sprint 2 Definition of Done

✔ GET directory endpoint supports all future UI controls
✔ Tri-state filters accepted and stable
✔ Ranking params accepted without breaking
✔ Facets endpoint live
✔ Supabase read model introduced
✔ No frontend hardcoding required
✔ No refactors needed for Sprint 3+

---

## Sprint 3 Preview (So You Don’t Overbuild)

Sprint 3 will:

* Implement real SQL filtering
* Add indexes
* Populate ranking fields
* Begin trending math
* Possibly introduce materialized views

**Sprint 2 is about shape, not power.**
