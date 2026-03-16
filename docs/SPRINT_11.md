# Sprint 11 — Local Agent v0.1 (Windows-first)

**Theme:** Ship the Local Agent that makes verified monitoring real.  
**Sprint goal:** A Windows-first executable that can handshake using the **account agent key**, accept opt-in cluster/server keys, and transmit signed heartbeats on a schedule after explicit consent.

**Status:** Planned.

---

## Scope lock (non-negotiable)

### In scope (must ship)

- **Windows-first** agent distribution (exe) that runs on the host machine.
- **Simple UI** for:
  - Paste keys
  - Handshake
  - See status colors (R/Y/G) for clusters/servers
  - Explicit **Transmit Heartbeats** toggle with disclosure
- **Heartbeat scheduler** (every X minutes) with correct backoff semantics.
- **No server ID copy/paste** required by the user.

### Explicitly not in scope (v1.1+)

- Rich auto-discovery across machines.
- Remote management UI.
- Deep ASA telemetry (RCON, mod sync, password sync) beyond minimal checks.

---

## Agent UX contract (what the user experiences)

### First run (blocking until configured)

1. **Paste Account Agent Private Key** (required)
2. Click **Handshake**
   - UI shows: “Account recognized” + list of clusters and servers
3. (Opt-in) Paste:
   - **Cluster private key** (optional but recommended)
   - **Server private keys** (required for servers this host will transmit for)
4. Read privacy disclosure and toggle **Transmit Heartbeats → ON**

**Rule:** the agent must not transmit anything until the user enables transmit.

---

## Playbook (11.1–11.8)

### 11.1 Tech stack + repo layout

**Recommended stack:** Node.js + TypeScript.

**Minimum agent components**

- `agent-core`
  - config + storage
  - checks
  - signing
  - http client + retry/backoff
  - scheduler
- `agent-ui`
  - simple window that wraps a local UI or native UI toolkit

**Exit criteria**

- Local dev runs: `npm run dev` (or equivalent) and can hit bootstrap against a dev backend.

---

### 11.2 Config model (local, explicit, inspectable)

**Objective:** Keep it boring and debuggable.

**Config fields (minimum)**

- `api_base` (default `https://asaselfhosted.com`)
- `account_private_key_b64` (required)
- `cluster_keys[]` (optional): `{ cluster_id, private_key_b64, key_version }`
- `server_keys[]` (required for transmit): `{ server_id, private_key_b64, key_version }`
- `transmit_enabled` (default false)
- `interval_seconds` (default 60–300; must respect backend rate limit)
- `selected_server_ids[]` (this host only; user selects)

**Storage**

- Start with JSON on disk.
- v1.0 should at least protect against accidental UI display of secrets (masking).

**Exit criteria**

- Agent can restart and retain settings and transmit state.

---

### 11.3 Handshake (bootstrap) implementation

**Objective:** From only the account key, fetch inventory and show readiness.

**Behavior**

- Derive account public key locally
- Call `POST /api/v1/agent/bootstrap`
- Populate UI with clusters + servers
- Show per item:
  - “Key missing” / “Key ok” / “Key version mismatch”

**Exit criteria**

- Handshake succeeds, shows inventory, and never requires server IDs pasted by user.

---

### 11.4 Opt-in key import (paste keys)

**Objective:** Support “opt-in first policy.”

**Behavior**

- User pastes keys (cluster optional, server required for transmit)
- Agent derives public key locally and:
  - calls register endpoints (Sprint 10) to store public keys, OR
  - validates keys against expected public key/version if already registered
- UI shows “Registered” status per server/cluster

**Exit criteria**

- User can fully configure without touching the web dashboard after generating the account key.

---

### 11.5 Local checks → status mapping (online/offline/unknown)

**Objective:** Implement checks that are reliable on day one.

**Checks (v0.1)**

- Port open / connect check to `join_address` host (or configured host) + query/game port if known
- Optional: HTTP/UDP query if ASA exposes a reliable endpoint (only if stable)

**Mapping**

- Check passes → `online`
- Check definitively fails (connection refused, process absent if you implement it) → `offline`
- Ambiguous failures (timeout, permission, host unreachable) → `unknown`

**Exit criteria**

- Agent can produce a status for each selected server with sensible “unknown” handling.

---

### 11.6 Heartbeat scheduler + error handling

**Objective:** Respect backend semantics and avoid spamming.

**Behavior**

- Heartbeat interval default keeps under backend rate limits.
- Each server has its own backoff state.
- Status-code handling:
  - `202 accepted/duplicate`: record success time
  - `401 invalid signature`: stop sending for that server; show “bad key”
  - `409 key_version_mismatch`: stop sending; show “rotation required”
  - `426 upgrade required`: stop sending globally; show “upgrade required”
  - `429`: exponential backoff with jitter
  - `5xx`: retry with jitter, bounded

**Exit criteria**

- Agent behaves predictably under all errors and does not hammer the API.

---

### 11.7 UI requirements (simple but shippable)

**Main screen**

- Top status strip:
  - Agent version
  - Handshake state (ok/error)
  - Transmit state (OFF by default)
- Two lists:
  - Clusters (badge: “Key configured” if cluster key provided)
  - Servers (R/Y/G, last heartbeat attempt, last error)
- Buttons:
  - Handshake
  - Test now (per server)
  - Toggle: **Transmit Heartbeats** (with disclosure modal)

**Disclosure (minimum copy)**

- “When enabled, this agent will transmit server status heartbeats to asaselfhosted.com on a schedule.”
- “You can disable transmit at any time.”

**Exit criteria**

- A non-technical user can paste keys, see readiness, and enable transmit confidently.

---

### 11.8 Packaging + distribution (Windows-first)

**Objective:** Deliver a usable exe.

**Deliverables**

- Build a signed-ish installer story later; for v0.1:
  - a single executable is acceptable
  - optional: “Install as service” helper command/button
- Logging:
  - view recent logs in UI
  - export diagnostics bundle (redacted secrets)

**Exit criteria**

- You can hand the exe to a closed-group tester and they can run it without dev tooling.

---

## Sprint 11 definition of done

- The agent can complete:
  - account-key handshake
  - opt-in key paste (server keys)
  - explicit transmit enable
  - scheduled heartbeats with correct error handling
- A tester can set it up without copying server IDs and without DB access.

