# LOCAL_AGENT_PLAYBOOK — Backend & Frontend Readiness Review

Review of [LOCAL_AGENT_PLAYBOOK.md](LOCAL_AGENT_PLAYBOOK.md) against the current backend and frontend. **We are not building the Local Agent yet**; this ensures the backend and frontend expose what the agent (and its UX) will need.

**Updates (implemented):**

- **Heartbeat status:** Schema and storage support `online` | `offline` | `unknown`. Fast-path and directory show `unknown` as its own state (no mapping to offline).
- **HTTP semantics:** Success path returns **202 Accepted** with `result`: `"accepted"` or `"duplicate"`. **426 Upgrade Required** for `agent_version_too_old` (no longer 200).
- **Dashboard:** Copyable Heartbeat URL, API Base, Cluster ID, Key version, Public key; “Copy Server ID (for agent)” on server cards and rows.
- **Backend:** `GET /api/v1/clusters/{id}/agent-config` (owner), `GET /api/v1/clusters/{id}/servers` (owner) for agent UX.

---

## 1. Backend: Heartbeat & DB (current state)

### 1.1 Heartbeat endpoint and contract

| Playbook expectation | Current backend | Status |
|----------------------|-----------------|--------|
| POST to `/api/v1/heartbeat` | `POST /api/v1/heartbeat` exists | ✅ |
| Envelope: server_id, key_version, timestamp, heartbeat_id, status, map_name, players_current, players_capacity, agent_version, signature | `HeartbeatRequest` matches; canonicalization in `core/crypto.py` uses same field set | ✅ |
| status: online/offline/unknown | Schema is `Literal["online", "offline", "unknown"]`; fast-path and directory use as-is | ✅ |
| Ed25519 sign over canonical envelope (sorted keys, RFC3339, no whitespace, nulls included) | `canonicalize_heartbeat_envelope()` + `verify_ed25519_signature()` | ✅ |
| Replay protection via heartbeat_id | Unique (server_id, heartbeat_id); replay returns success with `replay: true` | ✅ |
| Cluster has public_key + key_version; verify with cluster key | Load server→cluster; check key_version; verify signature with cluster public key | ✅ |
| Rate limit: 12/min per server | `heartbeat_rate_limit(request, server_id)` → 12/min per server_id | ✅ |
| 202 Accepted on success | Route returns **202** with `result`: `"accepted"` or `"duplicate"` | ✅ |
| 401 invalid_signature, 409 key_version_mismatch | Raised as appropriate; rejections written to ingest_rejections | ✅ |
| agent_version_too_old → stop spamming | Returns **426 Upgrade Required** (heartbeat not persisted); agent should show “upgrade required” | ✅ |
| Timestamp: stale beyond grace → 400; future >60s → 400 | Implemented; grace from cluster override or config | ✅ |
| Consent gate (e.g. self_hosted) | `is_data_allowed_now(server_id, HEARTBEAT, ...)` → 403 if not allowed | ✅ |

### 1.2 Persistence and worker

| Playbook expectation | Current backend | Status |
|----------------------|-----------------|--------|
| Record heartbeat (append-only) | `heartbeat_repo.create_heartbeat()`; replay detected by UNIQUE(server_id, heartbeat_id) | ✅ |
| Fast-path server update (last_seen_at, status_source=agent) | `derived_repo.fast_path_update_from_heartbeat()` | ✅ |
| Enqueue for worker (durable queue) | `jobs_repo.enqueue_server(server_id)`; worker runs engines, updates derived state | ✅ |
| Rejections audited (no PII) | `ingest_rejections_repo.record_rejection()` with reason + optional metadata | ✅ |

**Conclusion:** The heartbeat pipeline (verify → persist → fast-path update → enqueue → response) is in place. Status `unknown` is supported; 202/426 and `result` field are implemented.

---

## 2. Backend: Endpoints for agent UX (playbook §5)

Playbook recommends these to make agent setup and diagnosis smooth:

| Endpoint | Purpose | Exists? | Notes |
|----------|---------|---------|--------|
| **GET /api/v1/clusters/{cluster_id}/servers** | List servers in cluster (owner) so agent UI can import server IDs | ✅ | Returns minimal list: id, name, map_name (owner-only). |
| **GET /api/v1/clusters/{cluster_id}/agent-config** | Return key_version, heartbeat_grace_seconds, min_agent_version | ✅ | Owner-only. min_agent_version from app config. |
| **POST /api/v1/clusters/{id}/agent-bootstrap-token** | Short-lived token for one-time config + server list without long-lived JWT | ❌ No | Optional for v0.2; copy/paste and agent-config endpoint suffice for v0.1. |

So: **heartbeat and key verification are ready; no backend changes are required for the agent to work.** The above are **UX improvements** so the agent can avoid manual copy/paste and avoid storing a user JWT on the game host.

---

## 3. Frontend / dashboard vs playbook UX

Playbook §2 describes the **Local Agent UI** (first-run wizard, operational dashboard, logs, settings). The **web dashboard** is the place where owners get everything the agent needs: cluster identity, keys, server IDs, and target URL.

### 3.1 What the agent needs from the web (playbook §1.2 & §2.1)

- **Cluster ID** — paste into agent.
- **Cluster private key (base64)** — from Generate key (one-time); paste into agent.
- **API base URL** — e.g. `https://asaselfhosted.com` (or override for dev).
- **Heartbeat URL** — e.g. `https://asaselfhosted.com/api/v1/heartbeat` (or derived from API base).
- **Server IDs** — one per server the agent will report; playbook Step 3: “ASA Self-Hosted Server ID (paste from your dashboard).”
- **key_version** (and optionally heartbeat_grace_seconds, min_agent_version) — so agent can show “Config status: OK / key mismatch” and avoid sending wrong key_version.

### 3.2 What the dashboard currently provides

| Need | Current UI | Gap? |
|------|-------------|------|
| Cluster ID | Copy button per cluster in “Your Clusters” | ✅ |
| Private key | Shown once after Generate key; Copy button | ✅ |
| API base URL | Shown in “Agent verification setup” with Copy | ✅ |
| Heartbeat URL | Shown (API_BASE + /api/v1/heartbeat) with Copy | ✅ |
| Server IDs | “Copy Server ID” on each dashboard server card and row | ✅ |
| key_version | Shown per cluster with Copy (“Key v2”) | ✅ |

### 3.3 Verification page

VerificationPage explains verification and signed heartbeats at a high level. It does not provide agent setup steps or the heartbeat URL; that’s appropriate if agent setup is documented in the playbook and/or a future “Agent setup” help page.

---

## 4. Summary: backend readiness

- **Heartbeat:** Endpoint, schema, canonicalization, signature verification, replay, rate limit, consent, grace window, agent version check, persistence, fast-path update, and job enqueue are all in place.
- **Implemented:** `status: "unknown"` in schema and fast-path; 202 for success with `result`; 426 for agent_version_too_old; GET clusters/{id}/agent-config and GET clusters/{id}/servers (owner).
- **Optional (v0.2):** POST clusters/{id}/agent-bootstrap-token for one-time config fetch without long-lived JWT.

---

## 5. Summary: frontend/dashboard readiness

- **Keys:** Generate key / Rotate key and one-time private key display with Copy are in place.
- **Implemented:** Heartbeat URL and API Base with Copy in Agent verification setup; Cluster ID, Key version, Public key with Copy per cluster; “Copy Server ID” on dashboard server cards and rows.

---

## 6. Clarifying questions

1. **Status `"unknown"`** — Implemented. Schema and fast-path accept and store `unknown`; directory shows it as its own state.
2. **HTTP 202 / 426** — Implemented. 202 for accepted/duplicate with `result`; 426 for agent_version_too_old.
3. **Heartbeat URL and API base** — Implemented. Copyable in Agent verification setup.
4. **Cluster ID and key version** — Implemented. Copy per cluster (ID, Key vN, Public key).
5. **Server IDs** — Implemented. “Copy Server ID” on dashboard server cards and rows.
6. **Bootstrap token** — Deferred to v0.2; agent-config and copy/paste suffice for v0.1.
7. **GET clusters/{id}/servers** — Implemented. Owner-only list for agent import.

---

## 7. Status

All items above are implemented. The backend and frontend are in a clear state for the Local Agent to consume. For the authoritative heartbeat contract, see `backend/app/api/v1/heartbeat.py`, `backend/app/schemas/heartbeat.py`, and `backend/app/core/crypto.py`.
