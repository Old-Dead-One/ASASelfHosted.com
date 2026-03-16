** Designed to be:

* **Cheap:** rolling sweep (e.g., 100/minute → 6,000/hour)
* **Safe:** no request-path probing; no thundering herds
* **Responsive:** refresh-on-intent (filters/search/server/cluster view), capped to **first 96 servers**
* **Honest:** Observed ≠ Verified (Verified stays agent/plugin signed)

---

# OBSERVED STATUS PLAYBOOK (Step-by-step)

## 0) Lock the rules (do this first)

### 0.1 Status enums

* `status`: `online | offline | unknown`
* `status_source`: `agent | observed | manual`

### 0.1.1 Mode vs Source (clarification)

- **Mode** = owner intent (manual vs observed vs agent)
- **Source** = why the UI is currently showing a given status

Manual is only meaningful when **observation is not enabled** and **agent/plugin monitoring is not active**.
If observation is enabled but stale/missing, show `unknown` (honest uncertainty), not “manual fallback.”

### 0.2 Precedence (effective status shown to users)

1. If agent heartbeat is fresh → show `agent`
2. Else if observed check is fresh → show `observed`
3. Else:
   - if observation is enabled → show `unknown` (source: observed)
   - else show manual (or unknown)

### 0.3 Freshness windows (recommended defaults)

* `OBSERVED_SWEEP_TARGET_PER_MINUTE = 100` (scale later)
* `OBSERVED_FRESH_SECONDS = 3600` (1 hour considered “fresh”)
* `OBSERVED_ON_DEMAND_COOLDOWN_SECONDS = 300` (don’t recheck same server more than every 5 minutes due to UI spam)
* Probe timeout: `2.0s`

---

## 1) Database changes (Supabase/Postgres)

### 1.1 Add columns to `servers`

Add these columns:

**Observed configuration (opt-in)**

* `observation_enabled` boolean not null default false
* `observed_host` text null (default from join_address host portion)
* `observed_port` int null (required when observation_enabled=true)

**Observed state**

* `observed_status` text (or enum) nullable
* `observed_checked_at` timestamptz nullable
* `observed_latency_ms` int nullable
* `observed_error` text nullable (e.g., `timeout`, `refused`, `unreachable`)
* `observed_next_check_at` timestamptz nullable (for scheduling)

**Optional counters (nice for backoff later)**

* `observed_fail_streak` int default 0

If you already store a “status” in the server row, do **not** overwrite it; keep observed separate.
If “manual status” exists today only as `effective_status`, consider storing manual separately so it is not lost after monitoring begins.

### 1.2 Create an on-demand refresh queue table (recommended)

This keeps UI refresh intent separate from the hourly sweep.

`observed_refresh_queue`

* `id` uuid pk
* `server_id` uuid not null
* `requested_at` timestamptz not null default now()
* `requested_by_user_id` uuid nullable
* `reason` text nullable (e.g., `filter`, `server_detail`, `cluster_view`)
* `status` text not null default `queued` (`queued|processing|done|dropped`)
* `dedupe_key` text unique (optional)
* `expires_at` timestamptz default now() + interval '10 minutes'

**Dedupe strategy (important):**

* Unique index on `(server_id)` WHERE status = 'queued'

  * so repeated refresh requests don’t balloon the queue

### 1.3 Indexes

On `servers`:

* index on `observed_next_check_at`
* index on `(observed_checked_at)`
* if you have a “deleted” flag, include it in the selection query

On `observed_refresh_queue`:

* index on `status, requested_at`
* unique partial index for dedupe

---

## 2) Backend dependencies

### 2.1 Python packages (minimal)

You likely already have these, but explicitly:

* `asyncio` (built-in)
* `httpx` (if you later add HTTP-based checks; not required for TCP connect)
* `asyncpg` **or** `psycopg` (direct Postgres access is best for SKIP LOCKED)
* `pydantic` (already)
* Optional for CLI/worker ergonomics:

  * `typer` (nice CLI)
  * `tenacity` (retry policy)

**Why direct Postgres access matters:**
For a worker that needs “claim next batch” safely at scale, you want `FOR UPDATE SKIP LOCKED`.

---

## 3) Implement the probe (Observed check)

### 3.1 What to probe

Use a **UDP query** (A2S-style) to a configured port. The best port for ASA may vary; implement a “Test Observation” flow so owners can validate ports using real servers.

### 3.2 Mapping to status

* **Valid UDP response** → `online`
* **Immediate unreachable / no route** → `offline` (rare; depends on OS error visibility for UDP)
* **Timeout / ambiguous** → `unknown`

Do not map timeouts to offline.

### 3.3 Implementation approach (backend module)

Create `app/observed/probe_a2s.py` with a single async function:

* input: host, port, timeout_s
* output: `{ status, latency_ms?, error? }`

Implementation detail (sketch):

* Send UDP A2S Info request, wait for response with `asyncio` + timeout.
* Normalize outcomes:
  * response → online
  * timeout → unknown + timeout
  * unreachable → offline + unreachable (when detectable)

### 3.4 Security guardrails (SSRF/scanning prevention)

Observed probes run from backend infrastructure. Constrain targets:

* Only probe when `observation_enabled=true`.
* Default `observed_host` from join_address host. Allow editing, but validate:
  * reject localhost/private/link-local/multicast ranges
  * optionally DNS-resolve and reject private ranges
* Apply cooldown and rate limits to avoid abuse.

---

## 4) The rolling sweep worker (100/minute)

You have two deployment-safe options. Pick one:

### Option A (recommended): **Separate worker process**

* Run `python -m app.workers.observed_sweeper` as its own service on Fly/Render alongside API.
* Pros: stable, scalable, no “multiple API instances double-run jobs” problem.

### Option B: **Cron calls an internal endpoint**

* Supabase scheduled trigger or external cron hits `/internal/observed/sweep?limit=100`
* Pros: quick
* Cons: careful with auth + internal exposure

I recommend Option A if you plan to scale beyond a single instance.

---

### 4.1 Sweep selection logic

You want “next due servers” without collisions.

Use:

* `observed_next_check_at <= now()` or NULL
* exclude deleted/disabled servers
* optionally exclude servers with fresh agent heartbeat (not required, but saves work)

**Claim pattern (Postgres):**

* Select ids with `FOR UPDATE SKIP LOCKED`
* Update their `observed_next_check_at` immediately to spread future load

### 4.2 Scheduling math (rolling hourly)

If you want every server checked ~hourly:

* When a server is checked, set:

  * `observed_next_check_at = now() + interval '1 hour' + jitter`
* Add jitter (±5 minutes) so you don’t align checks.

### 4.3 Worker loop design

Run once per minute:

1. Drain a small amount of `observed_refresh_queue` first (priority work)
2. Then claim `N = OBSERVED_SWEEP_TARGET_PER_MINUTE` due servers
3. Probe them with concurrency cap (e.g., 50)
4. Update observed fields + schedule next check

---

## 5) On-demand refresh endpoint (triggered by filters/search/detail/cluster)

### 5.1 Endpoint

`POST /api/v1/observed/refresh`

Body:

* `server_ids: UUID[]` (client sends up to 96)
* `reason: "filter" | "search" | "server_detail" | "cluster_view"`

Behavior:

* Deduplicate server_ids (server side)
* For each server_id:

  * If `observed_checked_at >= now() - cooldown` → ignore
  * Else insert into `observed_refresh_queue` if not already queued

Return:

* `202 Accepted`
* `{ queued: <count>, skipped_fresh: <count>, skipped_dupe: <count> }`

### 5.3 Owner-login refresh (additional trigger)

On login (or dashboard load), refresh observed status for the owner’s servers (cap at 96). This makes “my servers” feel live without turning observation into constant background scanning.

### 5.2 Security

This endpoint can be public (no auth) **if** you:

* enforce strict input size (<= 96)
* enforce per-IP rate limit (e.g., 1 request / 10 seconds)
* only allow server_ids that exist and are public (optional)

If you want simplest: require auth. But public works fine with guardrails.

---

## 6) API response changes (what frontend consumes)

### 6.1 Server list response must return:

* `status` (effective)
* `status_source` (effective)
* `last_checked_at` (based on chosen source)
* optionally:

  * `observed_checked_at`
  * `is_observed_stale` boolean

### 6.2 How to compute effective status in backend

In the list query (or service layer), compute:

* `agent_fresh = (last_heartbeat_at >= now - HEARTBEAT_FRESH)`
* `observed_fresh = (observed_checked_at >= now - OBSERVED_FRESH)`

Then:

* if agent_fresh → `status = heartbeat_status`, `status_source = "agent"`
* else if observed_fresh → `status = observed_status`, `status_source = "observed"`
* else if observation_enabled → `status = "unknown"`, `status_source = "observed"`
* else if manual exists → `manual`
* else → `unknown`

---

## 7) Frontend triggers (the “right filters” logic)

### 7.1 Principle: refresh on intent, not on cosmetics

Trigger refresh when **filters change the set of servers**, not when sort/page changes.

**Trigger refresh on:**

* `search` / name query (debounced)
* `map`
* `game_mode`
* `ruleset`
* `platform`
* `status filter`
* `cluster_id` view/filter

**Do NOT trigger refresh on:**

* sort order changes
* page number changes
* page size changes (24/36/48)
* switching between “card view” and “row view”

### 7.5 Server edit UX (opt-in + test)

When the owner enables observation on the server form:

* default Observed Host from join_address host portion
* enable Observed Port input (required)
* add a **Test Observation** action that queues an on-demand refresh and shows the latest observed result (status + latency + error)

### 7.2 “First 96 servers” rule

When filters/search trigger a refresh:

* Take the current result set as rendered (or first few pages):

  * If you have 24/page: refresh first 96 = first 4 pages
* But do this without fetching 4 pages. Use the list you already have on screen:

  * **Option 1 (simple):** refresh only the current page’s IDs (24/36/48)
  * **Option 2 (your request):** refresh first 96 IDs:

    * request your API with `limit=96` for the refresh trigger only (not for display)
    * then call refresh endpoint with those 96 ids
    * display still shows 24/36/48

I recommend Option 2 for “filters/search,” Option 1 for “server detail.”

### 7.3 Debounce and rate protection (frontend)

* Debounce search input (300–500ms)
* Only send refresh if the **filter signature** changed:

Compute a stable key like:

* `refreshKey = JSON.stringify({ map, mode, ruleset, platform, status, search, cluster })`

If only `sort` changed, refreshKey unchanged → no refresh.

### 7.4 UI behavior

* After calling refresh endpoint, you can:

  * do nothing (status will be fresher next time), or
  * schedule a single refetch after 2–3 seconds if you want “feels live”

Don’t loop.

---

## 8) Observed sweep scaling (your 100/min plan)

Your plan is correct:

* 100/min → 6,000/hour
* 200/min → 12,000/hour
* 300/min → 18,000/hour

Add one more safeguard:

* cap global concurrency (e.g., 50 probes at once)
* enforce per-host timeout 2s
* use jittered scheduling

This keeps resource use predictable.

---

## 9) Step-by-step implementation order (follow exactly)

### Phase 1 — DB + API output (no worker yet)

1. Add `observed_*` columns and migrate
2. Update backend schemas to include `status_source`
3. Implement effective status precedence logic in list + detail responses
4. Frontend: show **Observed vs Verified** label/badge based on `status_source`

### Phase 2 — Worker sweep

5. Implement probe function
6. Implement sweeper worker:

   * claim next N due servers
   * probe with concurrency cap
   * update observed fields
   * schedule next check
7. Deploy worker and confirm observed_checked_at is updating steadily

### Phase 3 — On-demand refresh

8. Add `/observed/refresh` endpoint with dedupe + cooldown
9. Update worker to drain refresh queue before sweep
10. Frontend: add refresh triggers:

* on filter/search changes: request first 96 ids then call refresh endpoint
* on server detail view: call refresh for that one server_id

### Phase 4 — Tuning + guardrails

11. Add rate limit to refresh endpoint
12. Add basic metrics/logging for:

* probes per minute
* timeouts vs refused vs success

13. Adjust `OBSERVED_SWEEP_TARGET_PER_MINUTE` from config/env

---

## 10) What to name and where to put things (suggested layout)

Backend:

* `app/observed/probe.py`
* `app/observed/sweep.py` (claim logic + update)
* `app/observed/router.py` (refresh endpoint)
* `app/workers/observed_sweeper.py` (loop)

Docs:

* `docs/STATUS_MODEL.md`
* `docs/OBSERVED.md` (intervals, triggers, semantics)

Frontend:

* Add `refreshObserved(serverIds, reason)` in your API client
* Add a `useObservedRefresh()` hook that:

  * watches filter signature
  * fetches ids up to 96
  * posts refresh request
