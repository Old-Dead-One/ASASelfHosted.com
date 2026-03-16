# Status Model (Manual vs Observed vs Agent)

This document is the **single source of truth** for how ASA Self-Hosted computes and displays server status.

**Principle:** `unknown` is an honest uncertainty state, not a failure.

---

## 1) Concepts

### 1.1 Status (what the server “is” right now)

`status` is one of:

- `online`
- `offline`
- `unknown`

### 1.2 Monitoring modes (owner intent)

Monitoring “mode” answers: *how is this server supposed to be monitored?*

- **Manual**: owner manages status themselves (no observation enabled, no agent/plugin transmitting)
- **Observed**: owner opted in to observation checks (best-effort, not verified)
- **Agent**: verified monitoring (Local Agent / plugin heartbeats)

### 1.3 Source (why the UI shows a particular status)

`status_source` answers: *where the currently displayed status came from*:

- `manual`
- `observed`
- `agent`

**Rule:** “Observed” must never be presented as “Verified.”

---

## 2) Persistence fields (recommended shape)

To prevent “manual status” from being lost once monitoring begins, store manual separately.

### 2.1 Manual fields (owner-managed)

- `manual_status` (`online|offline|unknown`, nullable)
- `manual_updated_at` (nullable)

### 2.2 Observed configuration (opt-in)

- `observation_enabled` (boolean, default false)
- `observed_host` (text, nullable; default from `join_address` host portion)
- `observed_port` (int, nullable; required when observation_enabled is true)
- (optional) `observed_probe` (text, default `a2s`)

### 2.3 Observed results (best-effort)

- `observed_status` (nullable)
- `observed_checked_at` (nullable)
- `observed_latency_ms` (nullable)
- `observed_error` (nullable; e.g. `timeout|refused|unreachable|bad_response`)
- `observed_next_check_at` (nullable; used by sweeper)
- `observed_fail_streak` (int, default 0)

### 2.4 Agent/verified results

Existing agent heartbeat pipeline already yields:

- `effective_status` (computed/derived)
- `status_source` (agent when derived from heartbeats)
- `last_seen_at` (server-trusted clock: received_at)
- `last_heartbeat_at` (agent-reported timestamp)

---

## 3) Display computation rules (precedence)

### 3.1 Freshness windows

- **Agent freshness**: driven by cluster grace window + last_seen_at (server-trusted).
  - “Fresh” means: last_seen_at is within the grace window.
- **Observed freshness**:
  - `OBSERVED_FRESH_SECONDS` (recommended 3600)
  - “Fresh” means: `observed_checked_at >= now - OBSERVED_FRESH_SECONDS`

### 3.2 Precedence (display)

Compute:

- `agent_fresh`
- `observed_fresh`
- `manual_available` (manual_status not null)

Then:

1) If `agent_fresh` → show **agent**
2) Else if `observation_enabled` and `observed_fresh` → show **observed**
3) Else if `observation_enabled` and **not** `observed_fresh`:
   - show `status = unknown`, `status_source = observed`
   - keep last observed status/time visible as “last observed” metadata (optional)
4) Else (observation not enabled):
   - show `manual_status` if available, otherwise `unknown`
   - `status_source = manual`

**Key policy decision (locked):**

- Manual is only meaningful when observation/agent are not enabled.
- If observation is enabled but stale/misconfigured, we show `unknown` (honest uncertainty), not “manual fallback.”

---

## 4) UI requirements (minimum)

### 4.1 Server detail page (Monitoring card)

Show:

- **Mode**: Manual / Observed / Agent (owner intent)
- **Source**: manual/observed/agent (why the status shown is what it is)
- **Last update**:
  - agent: last_seen_at
  - observed: observed_checked_at
  - manual: manual_updated_at
- If observation enabled but stale/missing results: show an explicit note (“Observed data is stale / not yet checked”).

### 4.2 Directory list cards/rows

Show:

- Status badge (online/offline/unknown)
- Optional small provenance label:
  - “Verified” only when agent/plugin is fresh (cryptographic)
  - “Observed” when observed is the source
  - No misleading “verified” label for observed

---

## 5) Security guardrails (Observed)

Observed probes run from backend infrastructure. That creates SSRF/scanning risk unless constrained.

Minimum guardrails:

- Only allow observation when `observation_enabled = true`.
- Restrict observed targets:
  - Default observed_host must match join_address host.
  - If user edits observed_host, validate it is not localhost/private/link-local/metadata ranges.
  - Optionally resolve DNS and block private ranges.
- Rate limit refresh endpoint.
- Cooldown per server (`OBSERVED_ON_DEMAND_COOLDOWN_SECONDS`) to prevent spamming.

---

## 6) Open questions (defer until implementation)

- Whether “manual status” should be accepted as input in v1 UI once observation/agent is enabled (likely yes, but displayed only when manual mode is active).
- Whether to expose `observed_error` to the public directory or keep it owner-only.

