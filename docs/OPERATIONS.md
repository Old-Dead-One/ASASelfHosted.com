# Operations — Backend, Ingest, and Runbooks

Single reference for ingest contract, violation policy, responsibility map, background jobs, failure modes, and alerting. Use for runbooks and “where does this belong?”

**Last updated:** 2026-02-03

---

## 1. Responsibility Map

Where logic lives: **Supabase** (DB, RLS, auth) vs **FastAPI** (policy, verification, ingest).

| Responsibility | Supabase | FastAPI |
|----------------|----------|---------|
| **Auth** | JWKS/JWT verification, session; anon vs authenticated vs service_role | Uses JWT from request; optional auth bypass (local only); admin role check (env list) |
| **Ownership & RLS** | RLS on profiles, servers, clusters, favorites; “user can only edit own” | No ownership logic; relies on RLS |
| **Directory visibility** | `directory_view`; RLS and view hide private/join_password from anon | Reads via view; filtering/sorting/pagination; no duplicate visibility logic |
| **Ingest validation** | — | Rate limit, signature (Ed25519), timestamp window, key version, consent gate, agent version |
| **Consent gate** | — | `is_data_allowed_now(server_id, data_type, context)`; heartbeat only when self_hosted |
| **Rejection audit** | Table `ingest_rejections` (service_role only) | Writes to ingest_rejections on every reject path; no PII |
| **Heartbeat persistence** | heartbeats, heartbeat_jobs; UNIQUE(server_id, heartbeat_id) | API: validate → consent → insert; worker: claim job, run engines, mark processed |
| **Ranking / badges / status** | Stored columns; views may aggregate | Engines in FastAPI; worker writes results to DB |
| **Admin overrides** | hidden_at, badges_frozen, profiles.servers_limit_override, clusters_limit_override; RLS excludes admin-only | Admin-only endpoints (PATCH hide/unhide, incident_notes; PATCH profile limits) |

**Boundaries:** No business policy in RLS; directory visibility defined once (Supabase); ingest = validate → consent → write; admin actions only via API.

---

## 2. Ingest Contract

Versioned event schemas for data ingested from agents/plugins. No data reaches storage without validation and the consent gate.

**Event types:** `server.heartbeat.v1` (agent heartbeat: server identity, status, map, players, signature).

**Endpoint:** `POST /api/v1/heartbeat`

**Allowed fields:** `server_id`, `key_version`, `timestamp`, `heartbeat_id`, `status`, `map_name`, `players_current`, `players_capacity`, `agent_version`, `payload` (diagnostic only), `signature`. Signed envelope = all except `signature` and `payload` (see `core/crypto.py`).

**Rejected fields:** Any field not in the allowed list; see [§3 Drop-on-Violation](#3-drop-on-violation).

**Validation order:** Rate limit → load server/cluster → key version → signature → timestamp → consent gate → insert (replay via UNIQUE). Rejections written to `ingest_rejections`.

**Timestamp window:** Stale = older than grace window → reject. Future = >60s ahead → reject (clock skew).

**Replay:** DB UNIQUE(server_id, heartbeat_id); duplicate returns 202 with `result: "duplicate"`. All successful ingestion (first-time or replay) returns **202 Accepted** with `result`: `"accepted"` or `"duplicate"`. **426 Upgrade Required** when agent version is below MIN_AGENT_VERSION (heartbeat not persisted).

**Status:** Agent may send `online`, `offline`, or `unknown`. All three are stored and reflected in directory (unknown shown as its own state, e.g. “Unknown (agent unreachable)”).

---

## 3. Drop-on-Violation

How each ingest violation class is handled.

| Class | Action |
|-------|--------|
| `consent_denied` | audit_log → 403 |
| `invalid_signature` | audit_log → 401 |
| `replay` | silent_drop → 202 + `replay: true` |
| `stale_timestamp`, `clock_skew_violation` | audit_log → 400 |
| `malformed_payload`, `unknown_field` | audit_log → 4xx |
| `server_not_found` | audit_log → 404 |
| `cluster_missing_public_key` | audit_log → 401 |
| `key_version_mismatch` | audit_log → 409 |
| `agent_version_too_old` | audit_log → 426 Upgrade Required (heartbeat not persisted) |

**Actions:** silent_drop (replay only); audit_log (write to `ingest_rejections`, no PII). owner_notification and alert are future.

---

## 4. Background Jobs

**Heartbeat jobs:** Table `heartbeat_jobs`; one pending job per server. Flow: ingest API appends heartbeat, enqueues server_id; worker claims jobs, runs engines (status, uptime, confidence, quality, anomaly), writes derived state, marks processed.

**Retry:** Claim with attempts increment and claimed_at; on failure mark_failed. If `attempts >= HEARTBEAT_JOB_MAX_ATTEMPTS` (config, default 5), job is permanently failed (dead-letter): processed_at set, never re-claimed.

**Config (env):** HEARTBEAT_JOB_POLL_INTERVAL_SECONDS, HEARTBEAT_JOB_BATCH_SIZE, HEARTBEAT_JOB_CLAIM_TTL_SECONDS, HEARTBEAT_JOB_MAX_ATTEMPTS, RUN_HEARTBEAT_WORKER.

**Dead-letter:** Query heartbeat_jobs where processed_at IS NOT NULL and last_error IS NOT NULL. No automatic purge; see [§8 Data lifecycle](#8-data-lifecycle).

---

## 5. Failure Modes

| Scenario | What works | What doesn’t | Action |
|----------|------------|--------------|--------|
| **Supabase down** | FastAPI health may respond | Directory, auth, ingest, CRUD | 503 for dependent endpoints; health reports unhealthy |
| **Agent/plugin offline** | Directory readable; listing stays | Auto-update for that server | Owners fix agent or set status manually |
| **Frontend down** | Backend API and heartbeat ingest | Browsing, dashboard, login UI | Restore frontend |

**Degraded:** Read-only mode if Supabase write fails; consider short-lived directory cache. Health: liveness = process up; readiness = can reach Supabase.

---

## 6. Alerting

**Alert on (examples):** Heartbeat 5xx rate; rejection rate spike; worker backlog (pending jobs > threshold); Supabase unreachable; dead-letter growth.

**Principles:** Actionable only; prefer rate/percentage over raw counts; sliding windows; avoid duplicate alerts. Align with [§5 Failure Modes](#5-failure-modes) for response path.

---

## 7. Contact handling

Where contact messages go, who reviews them, and how long we keep them.

**How users reach us:** Contact page offers a mailto link and support email. Users can email for data rights requests, general inquiries, or feedback. No PII in logs.

**Where messages land:** Messages go to the team inbox configured for the deployment (e.g. support@asaselfhosted.com). A designated team member (or rotation) reviews. For data rights requests, identity may be verified before processing (see [§8 Data lifecycle](#8-data-lifecycle)).

**Retention:** General inquiries — per business need; typically deleted or anonymized after resolved. Data rights requests — as needed to fulfill and demonstrate compliance; then deleted or anonymized per §8.

**Privacy Policy alignment:** The Privacy Policy and Data Rights page state that users can contact us via the Contact page; this section describes the handling flow.

---

## 8. Data lifecycle

Retention rules, purge mechanics, and backup posture. Source of truth for retention and deletion; referenced from Data Rights page and account-deletion flows. Align with Privacy Policy and [TRUST_PAGES.md](TRUST_PAGES.md).

**What we keep and for how long:**

| Data | Retention | Why |
|------|-----------|-----|
| Heartbeats | Configurable; default no automatic purge. Recommend 90 days. | Status history, uptime/quality, anomaly detection. |
| Heartbeat jobs | Indefinite; dead-letter rows remain for inspection. | Queue and audit; optional purge job can be added. |
| Ingest rejections | Recommend 30 days; no automatic purge today. | Abuse defense and admin visibility. |
| Profiles | Until account deletion. | Account identity, terms acceptance, display name. |
| Servers | Until owner deletes or account deletion. | Directory listings, ownership. |
| Favorites | Until user removes or account deletion. | User preference. |
| Clusters | Until owner deletes or account deletion. | Agent auth, keys, grace window. |
| Incident notes | Indefinite; admin-only. | Moderation and incident history. |

Retention periods are targets for future purge jobs or manual processes.

**User-initiated deletion:** Account deletion — see below. Server deletion — owner can delete; cascades (heartbeats, heartbeat_jobs, favorites, incident_notes) per schema. Data rights (access, correction, deletion) — described on Data Rights and Privacy pages; identity verification may be required.

**Account deletion (self-service):** Users can permanently delete their account and all associated data from the Data Rights page. **Endpoint:** `DELETE /api/v1/me` (authenticated). Backend calls Supabase Auth Admin API to delete the auth user; DB cascades remove profile, servers, clusters, favorites, and related rows. **Permanent and irreversible:** The UI and copy state clearly that deletion cannot be reversed. A timeout (e.g. 25s) is used so the request does not hang if Supabase is slow; on timeout the user sees a message to try again or contact support. Contact path (§7) remains available for users who cannot use self-service (e.g. auth issues).

**Consent revocation cleanup (future):** When consent is revoked, no further data in scope; existing data in scope should be purged or anonymized per policy.

**Backup and restore:** Supabase backups per project settings. Purged data is not restored; align backup retention with Supabase plan and regulatory requirements.

---

## 9. Per-user limits and admin overrides

**Default limits (config):** `MAX_SERVERS_PER_USER` (default 14), `MAX_CLUSTERS_PER_USER` (default 1). Enforced in POST `/api/v1/servers` and POST `/api/v1/clusters`; GET `/api/v1/me/limits` returns used vs limit for dashboard.

**Profile overrides:** Columns `profiles.servers_limit_override` and `profiles.clusters_limit_override` (nullable). When set by an admin, they override the config defaults for that user (capped by system max: 100 servers, 50 clusters). Used for granting higher limits on a per-use-case basis.

**Admin endpoint:** `PATCH /api/v1/admin/profiles/{user_id}/limits` (admin-only). Body: `{ servers_limit_override?: number | null, clusters_limit_override?: number | null }`. Pass a number to set, or `null` to clear the override so the user falls back to config defaults.

**User-facing “request more”:** The dashboard shows “X of Y servers” and “X of Y clusters” and a note: “Need more servers or clusters? You can request a higher limit for your use case — contact us.” with a link to the Contact page. Admins process requests and, if approved, set the overrides via the admin endpoint (or direct DB update in migrations).

---

## References

- Schema: [REFERENCE_SCHEMA_SPRINT0_TO_5.md](REFERENCE_SCHEMA_SPRINT0_TO_5.md), `backend/app/db/migrations/`
- Trust pages: [TRUST_PAGES.md](TRUST_PAGES.md)
- Consent: `app/middleware/consent.py`; heartbeat: `api/v1/heartbeat.py`; worker: `workers/heartbeat_worker.py`
