# Sprint 5 Implementation Plan

## Overview

**Sprint Theme:** Make the data trustworthy, consumable, and safe to expose.

**Goals:**
- Public directory reads are correct, fast, and deterministic
- Derived metrics behave predictably over time
- Ranking & sorting are stable and abuse-resistant
- No new write paths introduced
- No Supabase leakage outside repositories

---

## Phase 1: Directory Read APIs (5.1)

### Current State
- ✅ `/directory/servers` endpoint exists with pagination (currently page-based)
- ✅ `/directory/servers/{id}` endpoint exists
- ✅ DirectoryRepository interface exists (server-only)
- ❌ `/directory/clusters` endpoints are stubs (TODO)
- ❌ DirectoryClustersRepository doesn't exist
- ⚠️ Need to verify no direct Supabase calls in routes
- ⚠️ **CRITICAL**: Current pagination is page-based (not deterministic under churn)

### Tasks

#### 5.1.1: Audit Directory Endpoints & Pagination Determinism
**Priority:** High  
**Status:** Pending

- [ ] Verify `/directory/servers` is read-only (no mutations)
- [ ] **CRITICAL**: Confirm pagination determinism - current page-based pagination is unstable under writes
- [ ] Verify explicit sort keys with tie-break ordering (ORDER BY sort_key, id)
- [ ] Verify directory_view always includes fields needed for sorting/filtering (no per-row joins)
- [ ] Audit routes for any direct Supabase calls (should be zero)
- [ ] Document pagination issues and plan cursor migration

**Files to check:**
- `backend/app/api/v1/directory.py`
- `backend/app/db/supabase_directory_repo.py`
- `backend/app/db/migrations/003_sprint_3_directory_view.sql`

#### 5.1.2: Migrate DirectoryRepository to Cursor Pagination
**Priority:** High  
**Status:** Pending

- [ ] Update `DirectoryRepository.list_servers()` signature:
  - Change from `(page, page_size, ...)` to `(limit, cursor, ...)`
  - Return type: `(items, next_cursor)` where cursor is opaque string
  - Default limit: 25, max: 100
  - **CRITICAL**: Enforce max limit - `limit > 100` → return `400` (client error, not clamp)
- [ ] **CRITICAL**: Cursor encoding must include:
  - `{sort_by, order, last_value, last_id}` (all four fields)
  - If request `sort_by`/`order` don't match cursor, return `400` with clear error
- [ ] **CRITICAL**: Implement correct seek predicates per sort key:
  - For `order=desc`: `WHERE (sort_key < last_value) OR (sort_key = last_value AND id < last_id)`
  - For `order=asc`: `WHERE (sort_key > last_value) OR (sort_key = last_value AND id > last_id)`
- [ ] **CRITICAL**: Define NULL sort_key behavior:
  - Either disallow sorting on nullable keys, OR
  - Use `NULLS LAST` consistently and define cursor rules for null (null values come after all non-null)
- [ ] Ensure deterministic ordering: `ORDER BY sort_key, id` (id as tie-breaker)
- [ ] Update `SupabaseDirectoryRepository` implementation
- [ ] Update `/directory/servers` endpoint to use cursor pagination
- [ ] Add `seconds_since_seen` field to directory response:
  - Definition: `seconds_since_seen = now_utc - last_seen_at` (server-side)
  - **CRITICAL**: `now_utc` = request handling time (`datetime.now(timezone.utc)` in route)
  - Pass `now_utc` into repo/mapper so it's consistent across all items in a response
  - This avoids "seconds_since_seen differs across items by a few ms"
  - `last_seen_at` = `received_at` from last accepted heartbeat (not derived update time)
  - If `last_seen_at` is null: return `null` (don't invent numbers)
  - Clamp negatives to 0 (clock edge cases)

**Files:**
- `backend/app/db/directory_repo.py`
- `backend/app/db/supabase_directory_repo.py`
- `backend/app/api/v1/directory.py`
- `backend/app/schemas/directory.py`

**Dependencies:** 5.1.1

#### 5.1.3: Implement DirectoryClustersRepository (Separate File)
**Priority:** High  
**Status:** Pending

- [ ] Create `backend/app/db/directory_clusters_repo.py` (separate from directory_repo.py)
- [ ] Create `DirectoryClustersRepository` ABC with methods:
  - `list_clusters(limit, cursor, filters, sort_by, order) -> tuple[Sequence[DirectoryCluster], str | None]`
  - `get_cluster(cluster_id) -> DirectoryCluster | None`
- [ ] Create `SupabaseDirectoryClustersRepository` implementation
- [ ] Add provider function `get_directory_clusters_repo()` in `backend/app/db/providers.py`
- [ ] Create `DirectoryCluster` schema in `backend/app/schemas/directory.py`
- [ ] **CRITICAL**: Inspect DB enum/constraints for cluster visibility:
  - Check `clusters.visibility` column type (enum, constraint, or text)
  - **If only `public|unlisted` exist**: Lock in these two values only
  - **If `private` exists in DB**: Officially add it (may require migration)
  - **If `private` doesn't exist**: Don't mention it in contracts; use "not public" = 404
- [ ] Define cluster visibility rules (based on actual DB state):
  - `public` → appears in lists, can be fetched by id
  - `unlisted` → does NOT appear in lists, but GET /directory/clusters/{id} returns 200 if id known
  - `private` (if exists) → 404 always

**Files:**
- `backend/app/db/directory_clusters_repo.py` (new)
- `backend/app/db/supabase_directory_clusters_repo.py` (new)
- `backend/app/db/providers.py`
- `backend/app/schemas/directory.py`
- `backend/app/db/migrations/` (if private needs to be added)

**Dependencies:** 5.1.2

#### 5.1.4: Implement `/directory/clusters` Endpoint
**Priority:** High  
**Status:** Pending

- [ ] Update `backend/app/api/v1/clusters.py` (or create directory-specific cluster endpoints)
- [ ] Implement `GET /directory/clusters` with:
  - Pagination: `limit` (default 25, max 100), `cursor` (opaque)
  - Filters: `cluster_visibility=public` (unlisted excluded from lists)
  - Sorting: `updated`, `server_count`, etc. with deterministic tie-break (id)
  - Explicit default sort (not DB-dependent)
- [ ] Use `DirectoryClustersRepository` only (no direct Supabase)
- [ ] Add response model `DirectoryClustersResponse` with cursor pagination

**Dependencies:** 5.1.3

#### 5.1.5: Implement `/directory/clusters/{id}` Endpoint
**Priority:** High  
**Status:** Pending

- [ ] Implement `GET /directory/clusters/{id}` endpoint
- [ ] **Visibility rules:**
  - `public` → 200 OK
  - `unlisted` → 200 OK (if id known, even though not in lists)
  - `private` (if exists) → 404
  - Not found → 404
- [ ] Use `DirectoryClustersRepository.get_cluster()` only

**Dependencies:** 5.1.3

#### 5.1.6: Add Directory Contract Tests (Consolidated)
**Priority:** Medium  
**Status:** Pending

- [ ] Create `tests/test_directory_contracts.py` (consolidated directory test suite)
- [ ] Test response shape (schema validation)
- [ ] Test ordering (asc/desc for each sort key with deterministic tie-break)
- [ ] Test cursor pagination:
  - Cursor encoding/decoding (includes sort_by, order, last_value, last_id)
  - next_cursor presence/absence
  - **CRITICAL**: Test cursor mismatch rejection (400 error if sort_by/order don't match cursor)
  - **CRITICAL**: Test max limit enforcement (`limit > 100` → 400 error, not clamp)
  - Test seek predicates (correct WHERE clauses for asc/desc)
  - Test NULL sort_key handling (if nullable keys are allowed)
- [ ] Test pagination determinism (same cursor returns same results, assuming stable sort keys)
- [ ] Test filter combinations
- [ ] Test cluster visibility rules (public/unlisted, and private if it exists)
- [ ] Use fake repositories (hermetic, no Supabase)

**Dependencies:** 5.1.4, 5.1.5

---

## Phase 2: Ranking & Scoring Hardening (5.2)

### Current State
- ✅ Quality engine exists (`backend/app/engines/quality_engine.py`)
- ✅ Uptime engine exists (`backend/app/engines/uptime_engine.py`)
- ✅ Confidence engine exists (`backend/app/engines/confidence_engine.py`)
- ✅ Status engine exists (`backend/app/engines/status_engine.py`)
- ⚠️ Quality engine already clamps to 0-100 (good!)
- ⚠️ Need to verify monotonic decay, unknown behavior, stability

### Tasks

#### 5.2.1: Harden Quality Engine
**Priority:** High  
**Status:** Pending

- [ ] Verify clamping (0-100) - already done, document it
- [ ] Document monotonic decay rules (when does quality decrease?)
- [ ] Define "unknown" behavior (what happens with insufficient data?)
- [ ] Add inline documentation for invariants
- [ ] Add property tests for clamping and monotonic behavior

**Files:**
- `backend/app/engines/quality_engine.py`
- `backend/tests/test_quality_engine.py`

#### 5.2.2: Harden Uptime Engine
**Priority:** High  
**Status:** Pending

- [ ] Verify logic is based on `received_at` (not `timestamp`)
- [ ] Ensure stability across restarts (deterministic calculation)
- [ ] Document window boundaries and edge cases
- [ ] Add inline documentation for invariants

**Files:**
- `backend/app/engines/uptime_engine.py`
- `backend/tests/test_uptime_engine.py`

#### 5.2.3: Add Uptime Regression Tests
**Priority:** High  
**Status:** Pending

- [ ] Test: Long offline gap (server offline for days, then comes back)
- [ ] Test: Flapping servers (online/offline rapidly)
- [ ] Test: Cold-start servers (new server, no history)
- [ ] Verify uptime degrades gracefully in all cases

**Files:**
- `backend/tests/test_uptime_engine.py`

#### 5.2.4a: Add Anomaly Detection to Worker (Derived Metrics)
**Priority:** High  
**Status:** Pending

- [ ] Create `backend/app/engines/anomaly_engine.py` (or add to existing engine)
- [ ] Detect impossible player count changes (0→70→0 in < 60 seconds)
- [ ] Detect suspicious player spikes (sudden large increases)
- [ ] Compute `anomaly_players_spike` flag (boolean) or `anomaly_score` (0-100)
- [ ] Update worker to compute and store anomaly flags in `servers` table
- [ ] **CRITICAL**: This is derived metrics (no new write path), stored alongside other derived fields
- [ ] **CRITICAL**: Define decay/reset behavior (pick one strategy for Sprint 5):
  - **Chosen**: Clear after T minutes without spikes based on `received_at` (simpler, doesn't depend on heartbeat frequency)
  - Example: clear flag if no spike observed in the last 30 minutes
  - Alternative (future): N clean heartbeats, but not in Sprint 5
  - Prevents permanent scars on servers
- [ ] Add tests for anomaly detection and decay logic

**Files:**
- `backend/app/engines/anomaly_engine.py` (new)
- `backend/app/workers/heartbeat_worker.py`
- `backend/app/db/servers_derived_repo.py` (add anomaly fields)
- `backend/tests/test_anomaly_engine.py` (new)

**Dependencies:** None (can be done in parallel with other engine work)

#### 5.2.4b: Harden Confidence Engine
**Priority:** High  
**Status:** Pending

- [ ] Review current downgrade rules
- [ ] Add explicit downgrade rules (document when confidence decreases)
- [ ] Prevent sudden jumps (red → green without sustained signal)
- [ ] Add state machine documentation (green → yellow → red transitions)
- [ ] Add inline documentation for invariants

**Files:**
- `backend/app/engines/confidence_engine.py`
- `backend/tests/test_confidence_engine.py`

#### 5.2.5: Document Engine Invariants
**Priority:** Medium  
**Status:** Pending

- [ ] Add inline docstrings to each engine function
- [ ] Document:
  - Input ranges and constraints
  - Output ranges and guarantees
  - Monotonic behavior (if applicable)
  - Edge cases and "unknown" behavior
  - Stability guarantees

**Files:**
- All files in `backend/app/engines/`

#### 5.2.6: Add Property-Style Tests
**Priority:** Medium  
**Status:** Pending

- [ ] Quality engine: Test inputs → bounded outputs (0-100)
- [ ] Quality engine: Test monotonic decay (if applicable)
- [ ] Uptime engine: Test inputs → bounded outputs (0-100)
- [ ] Confidence engine: Test state transitions (no sudden jumps)
- [ ] Status engine: Test deterministic behavior

**Files:**
- `backend/tests/test_quality_engine.py`
- `backend/tests/test_uptime_engine.py`
- `backend/tests/test_confidence_engine.py`
- `backend/tests/test_status_engine.py`

---

## Phase 3: Anti-Gaming Guards (5.3)

### Current State
- ❌ No ranking math module exists
- ❌ No anti-gaming guards exist
- ⚠️ Ranking happens in repository/SQL, needs centralization

### Tasks

#### 5.3.1: Create Ranking Math Module (Python-Based)
**Priority:** High  
**Status:** Pending

- [ ] **DECISION**: Ranking computed in Python (Option A) - simple, testable, fast iteration
- [ ] Create `backend/app/engines/ranking.py`
- [ ] Define ranking computation functions:
  - `compute_ranking_score(server_data) -> float`
  - Apply anti-gaming guards here
  - **CRITICAL**: Ranking reads derived fields only (including anomaly flags), NOT raw heartbeat history
- [ ] Document ranking formula and guards
- [ ] Make this the single source of truth for ranking
- [ ] **CRITICAL**: Ranking placement:
  - Route: parsing + response shaping only (no business logic)
  - Repo: fetch + rank + sort (ranking happens here)
  - This preserves "no business logic in routes" and keeps tests clean

**Files:**
- `backend/app/engines/ranking.py` (new)
- `backend/app/db/supabase_directory_repo.py` (calls ranking module)

#### 5.3.2: Cap Players Contribution
**Priority:** High  
**Status:** Pending

- [ ] Add guard: Cap `players_current` contribution to ranking
- [ ] Example: If players > 50, treat as 50 for ranking purposes
- [ ] Document the cap value and rationale
- [ ] Add tests

**Dependencies:** 5.3.1

#### 5.3.3: Diminishing Returns for Uptime
**Priority:** High  
**Status:** Pending

- [ ] Add guard: Diminishing returns for uptime beyond threshold
- [ ] Example: Uptime > 95% gets diminishing returns (log scale)
- [ ] Document threshold and formula
- [ ] Add tests

**Dependencies:** 5.3.1

#### 5.3.4: Use Anomaly Flags in Ranking (Not Detection)
**Priority:** High  
**Status:** Pending

- [ ] Ranking module reads `anomaly_players_spike` or `anomaly_score` from server data
- [ ] Apply penalty to ranking score when anomaly detected
- [ ] Document penalty formula
- [ ] Add tests: ranking penalizes servers with anomaly flags

**Dependencies:** 5.3.1, 5.2.4a

#### 5.3.5: Add Gaming Attempt Tests
**Priority:** Medium  
**Status:** Pending

- [ ] Test: Rapid player count changes (gaming attempt)
- [ ] Test: Uptime manipulation attempts
- [ ] Test: Impossible heartbeat sequences
- [ ] Verify all gaming attempts fail (don't affect ranking)

**Files:**
- `backend/tests/test_ranking.py` (new)

---

## Phase 4: Snapshot Consistency & Caching (5.4)

### Current State
- ✅ Directory reads use `directory_view` (good)
- ⚠️ Need to verify no ad-hoc `.table("servers")` calls
- ⚠️ Need to document consistency model

### Tasks

#### 5.4.1: Document Consistency Model
**Priority:** Medium  
**Status:** Pending

- [ ] Document how directory reads achieve consistency
- [ ] Options:
  - Transaction-scoped reads (current approach)
  - Read replicas (future)
  - Materialized view (current: `directory_view`)
- [ ] Document guarantees (repeatable within request, no partial updates)
- [ ] **CRITICAL**: Document cursor pagination determinism limitations:
  - "Cursor pagination is deterministic for stable sort keys"
  - "No duplicates within a traversal **assuming stable ordering and correct cursor seek predicates**"
  - "Under concurrent updates, items may shift between pages"
  - "Duplicates can occur if sort keys change between requests (sort_key updates mid-traversal)"
  - "Cursors remain valid and reduce (but don't eliminate) pagination issues under churn"
  - This is the real-world truth about cursor pagination
- [ ] Add to `DECISIONS.md` or `DEV_NOTES.md`

**Files:**
- `backend/app/db/migrations/README.md` or `DECISIONS.md`

#### 5.4.2: Audit Routes for Ad-Hoc Supabase Calls
**Priority:** High  
**Status:** Pending

- [ ] Search entire codebase for `.table("servers")` outside repositories
- [ ] Search for `get_supabase_admin()` calls in routes
- [ ] Move any found calls to repositories
- [ ] Verify all directory reads go through repositories
- [ ] **CRITICAL**: Do this BEFORE adding new endpoints (cheaper to fix now)

**Command:**
```bash
grep -r "\.table(" backend/app/api/
grep -r "get_supabase_admin" backend/app/api/
```

**Note:** Moved earlier in timeline (Week 1) to catch issues before building new endpoints.

---

## Phase 5: Observability (5.5)

### Current State
- ✅ Some logging exists (heartbeat rejections, job failures)
- ⚠️ Need structured logging (consistent format)
- ❌ No metrics collection

### Tasks

#### 5.5.1: Structured Logging for Heartbeat Rejections
**Priority:** Medium  
**Status:** Pending

- [ ] Ensure all heartbeat rejections log with:
  - Structured format (JSON or key-value pairs)
  - Reason code (signature_invalid, stale_timestamp, etc.)
  - Server ID, cluster ID
  - Timestamp
- [ ] Review `backend/app/api/v1/heartbeat.py` logging

**Files:**
- `backend/app/api/v1/heartbeat.py`

#### 5.5.2: Structured Logging for Job Failures
**Priority:** Medium  
**Status:** Pending

- [ ] Ensure job failures log with:
  - Structured format
  - Job ID, server ID
  - Error message, attempt count
  - Timestamp
- [ ] Review `backend/app/workers/heartbeat_worker.py` logging

**Files:**
- `backend/app/workers/heartbeat_worker.py`
- `backend/app/db/supabase_heartbeat_jobs_repo.py`

#### 5.5.3: Structured Logging for Directory Read Errors
**Priority:** Medium  
**Status:** Pending

- [ ] Add structured logging for directory read errors
  - Endpoint path, query parameters
  - Error type, message
  - Timestamp
- [ ] Review `backend/app/api/v1/directory.py` error handling

**Files:**
- `backend/app/api/v1/directory.py`

#### 5.5.4: Add Request Timing Middleware
**Priority:** Medium  
**Status:** Pending

- [ ] Add request timing middleware to measure directory read latency
- [ ] Log timing in structured format (endpoint, method, duration_ms)
- [ ] **CRITICAL**: Do NOT use in-memory counters (reset on restart, wrong under multi-process)
- [ ] Structured logs are sufficient for Sprint 5 (log pipeline can compute metrics)
- [ ] If metrics needed: defer to Prometheus endpoint later with proper multiprocess story

**Files:**
- `backend/app/middleware/timing.py` (new)
- `backend/app/main.py` (add middleware)

**Note:** In-memory counters are fine for dev-only debugging, but not for production observability.

---

## Phase 6: Test Expansion (5.6)

### Current State
- ✅ Some engine tests exist
- ✅ Heartbeat endpoint tests exist (hermetic)
- ⚠️ Need directory endpoint tests
- ⚠️ Need ranking stability tests
- ⚠️ Need regression tests

### Tasks

#### 5.6.1: Directory Contract Tests (Already in 5.1.6)
**Priority:** High  
**Status:** Pending

- [ ] Covered in 5.1.6 (consolidated directory test suite)

#### 5.6.2: Ranking Tests (Consolidated)
**Priority:** High  
**Status:** Pending

- [ ] Create `backend/tests/test_ranking.py` (consolidated ranking test suite)
- [ ] Test anti-gaming guards (players cap, uptime diminishing returns, anomaly penalties)
- [ ] **CRITICAL**: Test "no ranking oscillation under identical inputs":
  - Same input list → same output ordering + scores (pure function test)
  - Multiple calls with identical data must produce identical results
- [ ] Test ranking stability (same inputs produce same ranking over time)
- [ ] Test ranking doesn't oscillate with minor data changes
- [ ] Test ranking degrades gracefully (stale data)
- [ ] Test gaming attempts fail (all in one file)

**Files:**
- `backend/tests/test_ranking.py` (new)

#### 5.6.3: Engine Boundary Condition Tests
**Priority:** High  
**Status:** Pending

- [ ] Test: Empty inputs (no heartbeats)
- [ ] Test: Single heartbeat
- [ ] Test: Extreme values (uptime 0%, 100%, etc.)
- [ ] Test: Null/None inputs
- [ ] Test: Invalid inputs (negative values, etc.)
- [ ] **Note**: Keep engine tests in separate files (test_quality_engine.py, etc.)

**Files:**
- Expand existing engine test files

#### 5.6.4: Regression Test - Replay Heartbeats
**Priority:** Medium  
**Status:** Pending

- [ ] Test: Duplicate heartbeat_id doesn't affect ranking
- [ ] Test: Replay detection works correctly
- [ ] Test: Replay doesn't create duplicate jobs

**Files:**
- `backend/tests/test_heartbeat_endpoint.py` (expand)

#### 5.6.5: Regression Test - Worker Crash + Recovery
**Priority:** Medium  
**Status:** Pending

- [ ] Test: Worker crash mid-processing (claimed jobs)
- [ ] Test: Stale claim reclaim works
- [ ] Test: Jobs are retried after worker restart
- [ ] Test: No duplicate processing

**Files:**
- `backend/tests/test_heartbeat_worker.py` (new or expand)

#### 5.6.6: Regression Test - Stale Servers Decaying
**Priority:** Medium  
**Status:** Pending

- [ ] Test: Server goes offline, metrics decay over time
- [ ] Test: Confidence degrades (green → yellow → red)
- [ ] Test: Uptime decreases over time
- [ ] Test: Quality score decreases

**Files:**
- `backend/tests/test_engine_decay.py` (new)

#### 5.6.7: Verify CI Hermeticity
**Priority:** High  
**Status:** Pending

- [ ] Verify all tests run with `ENV=test`
- [ ] Verify no Supabase connections in tests
- [ ] Verify no network calls in tests
- [ ] Verify CI passes with empty Supabase credentials
- [ ] Document test environment requirements

**Files:**
- `.github/workflows/ci.yml`
- `backend/tests/` (all test files)

---

## Implementation Order

### Week 1: Foundation (Phases 1 & 2)
1. **5.1.1** - Audit directory endpoints & pagination determinism
2. **5.4.2** - Audit routes for ad-hoc Supabase calls (do this early, before new endpoints)
3. **5.1.2** - Migrate to cursor pagination (servers) - includes sort_by/order in cursor
4. **5.2.4a** - Add anomaly detection to worker (derived metrics with decay behavior)
5. **5.1.3** - Implement DirectoryClustersRepository (separate file, check DB for visibility enum)
6. **5.1.4** - Implement `/directory/clusters` endpoint (cursor pagination)
7. **5.1.5** - Implement `/directory/clusters/{id}` endpoint
8. **5.2.1** - Harden Quality Engine
9. **5.2.2** - Harden Uptime Engine
10. **5.2.4b** - Harden Confidence Engine

### Week 2: Hardening & Guards (Phases 2 & 3)
11. **5.2.3** - Add uptime regression tests
12. **5.2.5** - Document engine invariants
13. **5.2.6** - Add property-style tests
14. **5.3.1** - Create ranking math module (Python-based)
15. **5.3.2** - Cap players contribution
16. **5.3.3** - Diminishing returns for uptime
17. **5.3.4** - Use anomaly flags in ranking (not detection)

### Week 3: Consistency & Observability (Phases 4 & 5)
18. **5.4.1** - Document consistency model (including cursor determinism limitations)
19. **5.5.1** - Structured logging for heartbeat rejections
20. **5.5.2** - Structured logging for job failures
21. **5.5.3** - Structured logging for directory read errors
22. **5.5.4** - Add request timing middleware (structured logs only, no in-memory counters)

### Week 4: Testing & Verification (Phase 6)
23. **5.1.6** - Directory contract tests (consolidated, including max limit enforcement)
24. **5.6.2** - Ranking tests (consolidated: anti-gaming + stability)
25. **5.6.3** - Engine boundary condition tests
26. **5.6.4** - Regression test - replay heartbeats
27. **5.6.5** - Regression test - worker crash + recovery
28. **5.6.6** - Regression test - stale servers decaying
29. **5.6.7** - Verify CI hermeticity

---

## Success Criteria

Sprint 5 is complete when:

- ✅ Directory endpoints can be safely exposed publicly
- ✅ **Cursor pagination implemented** (deterministic under churn)
- ✅ **Tie-break ordering explicit** (ORDER BY sort_key, id) for all sorts
- ✅ Rankings do not oscillate or get gamed
- ✅ Derived metrics degrade gracefully over time
- ✅ **Anomaly detection in worker** (not in ranking)
- ✅ **Ranking computed in Python** (testable, no SQL complexity)
- ✅ CI remains fast, hermetic, and boring
- ✅ No TODOs left in ranking/engine logic
- ✅ All tests pass (hermetic, no Supabase dependency)
- ✅ No direct Supabase calls in routes (all via repositories)
- ✅ All engines have documented invariants
- ✅ Anti-gaming guards are in place and tested
- ✅ **Cluster visibility rules clearly defined and tested** (based on actual DB enum state)
- ✅ **Staleness indicator** (seconds_since_seen) in directory responses:
  - Precisely defined: `now_utc - last_seen_at` where `now_utc` = request handling time
  - Consistent across all items in a response (passed into repo/mapper)
- ✅ **Cursor includes sort_by/order** (reject mismatches with 400)
- ✅ **Cursor seek predicates** correctly implemented (asc/desc WHERE clauses)
- ✅ **NULL sort_key handling** defined (disallow or NULLS LAST)
- ✅ **Max limit enforcement** (`limit > 100` → 400 error, tested)
- ✅ **Anomaly flags decay/reset** (T minutes strategy, 30 min default)
- ✅ **No ranking oscillation** (same inputs → same outputs, pure function)
- ✅ **seconds_since_seen consistency** (request handling time, consistent across response)

---

## Out of Scope (Do Not Drift)

- ❌ Auth changes
- ❌ Agent protocol changes
- ❌ Write-path refactors
- ❌ Paid features
- ❌ UI/frontend concerns
- ❌ New write paths
- ❌ Supabase leakage outside repositories

---

## Notes

- **Priority Levels:**
  - High: Critical for Sprint 5 goals
  - Medium: Important but not blocking
  - Low: Nice to have

- **Dependencies:** Tasks are ordered to respect dependencies. Some can be done in parallel (e.g., engine hardening tasks).

- **Testing:** All tests must be hermetic (no Supabase, no network). Use fake repositories and mock data.

- **Documentation:** Inline documentation is preferred. Add to `DECISIONS.md` for architectural decisions.

## Critical Requirements (Blocking Gates)

- **No direct Supabase calls in routes** - All data access via repositories
- **ENV=test hermetic** - All tests must pass with empty Supabase credentials
- **Cursor pagination** - Required for determinism (not page-based)
  - Cursor must encode: `{sort_by, order, last_value, last_id}`
  - Reject cursor if `sort_by`/`order` don't match (400 error)
  - Implement correct seek predicates (asc/desc WHERE clauses)
  - Define NULL sort_key behavior (disallow or NULLS LAST)
  - Enforce max limit: `limit > 100` → 400 error (not clamp)
- **Tie-break ordering** - Every sort must include `id` as tie-breaker
- **Ranking in Python** - Chosen for testability and fast iteration
  - Ranking computed in repo layer, not route (no business logic in routes)
- **Anomaly detection in worker** - Not in ranking (derived metrics only)
  - Anomaly flags must decay/reset: clear after T minutes without spikes (30 min default)
  - Based on `received_at` timestamps (simpler, doesn't depend on heartbeat frequency)
- **No ranking oscillation** - Same inputs → same outputs (pure function test)
- **seconds_since_seen** - Precisely defined: `now_utc - last_seen_at` where `last_seen_at = received_at` from heartbeat

## Risks & Mitigations

- **Risk**: Directory view missing fields needed for sorting/filtering
  - **Mitigation**: Audit directory_view in 5.1.1, ensure all sort keys available

- **Risk**: Pagination determinism broken by writes during read
  - **Mitigation**: Cursor pagination with (sort_key, id) encoding

- **Risk**: Ranking computation becomes expensive
  - **Mitigation**: Ranking reads derived fields only, not raw heartbeat history

- **Risk**: Cluster visibility rules unclear
  - **Mitigation**: Explicitly define in 5.1.3 and test in 5.1.6

- **Risk**: Staleness not communicated to clients
  - **Mitigation**: Add `seconds_since_seen` field to directory responses
