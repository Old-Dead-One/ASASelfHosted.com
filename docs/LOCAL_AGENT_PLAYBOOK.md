## Bring-you-up-to-speed: what the Local Agent is (and isn’t)

**Local Agent = a small service that runs on the same machine hosting your ASA dedicated server(s)** and sends **signed heartbeats** to `asaselfhosted.com` so the directory can mark servers as **Verified / agent-sourced** without depending on ASA mods/plugins. This keeps verification **free and reliable**, and it stays outside the ASA ecosystem (no mod maintenance treadmill). 

**What it sends (MVP heartbeat envelope)** is intentionally minimal (your backend already expects this shape):

* `server_id`
* `key_version`
* `timestamp`
* `heartbeat_id`
* `status` (online/offline/unknown)
* `map_name`
* `players_current`, `players_capacity` (optional)
* `agent_version`
* `signature` (Ed25519 over canonicalized envelope)

**Auth model (current, working in your backend):**

* **Cluster has `public_key_ed25519` + `key_version` stored in DB**
* Agent holds the corresponding **cluster private key** and signs every heartbeat
* Backend loads server → cluster, checks `key_version`, verifies signature using cluster public key

This lines up with your “Verified+ / key generation & rotation / cluster identity” direction. 

---

# Local Agent Sprint Playbook (Detailed)

## 0) Scope lock

### MVP (ship first)

1. Install/run agent on host
2. Configure cluster private key + server mappings
3. Run health checks on each server
4. Send signed heartbeats on a schedule
5. Show local UI for status + logs + troubleshooting
6. Handle temporary outages (queue/retry)
7. Support key rotation (manual update to new private key + key_version)

### Explicitly not in MVP

* Player-level data collection (consent system is separate and stricter) 
* Auto password sync
* Discord bot hooks
* Complex auto-discovery across multiple machines
* Remote UI exposure (keep local-first)

---

## 1) System architecture

### 1.1 Agent components (recommended shape)

**Language:** Node.js + TypeScript (matches your stack and your existing design direction) 

**Runtime layout:**

* **Agent Service (daemon)**

  * Scheduler
  * Health check runners
  * Heartbeat signer + sender
  * Local state store (SQLite or JSON)
  * Retry queue / backoff
* **Local Web UI**

  * Served by the agent at `http://127.0.0.1:<port>`
  * Configuration wizard + operational dashboard
* **Optional OS integration**

  * Windows service wrapper / systemd unit
  * “Run at startup”

### 1.2 Data flow (end-to-end)

1. Owner creates cluster + servers in web dashboard
2. Owner generates/rotates keys in dashboard (cluster keys are already implemented in backend)
3. Owner installs agent on host machine
4. Owner configures agent:

   * `cluster_id`
   * `cluster_private_key_ed25519` (base64)
   * server mappings (each has `server_id`, ports, map label)
5. Agent performs checks (process + query port + optional RCON)
6. Agent signs heartbeat envelope with cluster private key
7. Agent POSTs to `/api/v1/heartbeat`
8. Backend verifies signature + key_version + consent gates, records heartbeat, updates derived state

---

## 2) UX/UI Playbook (Local Agent)

You want the local agent UX to do two jobs:

* **Make setup idiot-proof**
* **Make diagnosis instant when something breaks**

### 2.1 Local UI pages (minimum set)

#### A) First-run Setup Wizard (blocking until done)

**Step 1 — Welcome / what this does**

* Explain: “This agent reports status for your servers to asaselfhosted.com. It does not change your server.”
* Show a checkbox: “I understand this agent sends heartbeat data (status/map/players).”

**Step 2 — Connect to your cluster**
Inputs:

* `Cluster ID` (paste)
* `Cluster Private Key (base64)` (paste)
* `API Base URL` (default `https://asaselfhosted.com`)
* “Test connection” button

Test connection should:

* Do a **dry-run signature** locally (validate key format)
* Optionally attempt a **heartbeat against a known server_id** (if one already configured)
* If no server is configured yet, just validate key format and save config

**Step 3 — Add servers (multi-server form)**
This is where most of the UX quality lives.

Each server row needs:

* `Server Name` (local label only)
* `ASA Self-Hosted Server ID` (paste from your dashboard)
* `Map Name` (dropdown or free text)
* `Host` (default `127.0.0.1`)
* `Query Port` (Steam query / game query port)
* `Game Port` (optional; for display only)
* `RCON Port` (optional)
* `RCON Password` (optional; store encrypted at rest if you support it)

Buttons:

* “Auto-detect ports from common ASA patterns” (optional)
* “Test checks for this server”

**Step 4 — Heartbeat schedule**

* Heartbeat interval per server (default 60s)
* Jitter toggle (recommended ON to avoid synchronized bursts)
* Backoff policy (fixed + exponential)
* Show warning about backend rate limit if you exceed it (your backend is 12/min/server right now—keep default ≤ 1/min)

**Step 5 — Install as service**

* Windows: “Install service” (admin required)
* Linux: “Generate systemd unit”
* Docker: show compose snippet (optional)

Exit wizard → Operational Dashboard.

---

#### B) Operational Dashboard (what you look at daily)

Top banner:

* Agent version
* Last successful heartbeat (overall)
* “Config status: OK / key mismatch / cannot reach API / upgrade required”

Main table (one row per server):

* Server label
* Server ID (copy)
* Status (online/offline/unknown)
* Last local check time
* Last heartbeat time (local)
* Last heartbeat accepted time (if you capture response)
* Map
* Players current/capacity (if available)
* Fail reason (if failing)

Row actions:

* “Run checks now”
* “Send heartbeat now”
* “View logs”
* “Edit config”
* “Disable server” (agent stops reporting it)

---

#### C) Logs & Diagnostics

Split into tabs:

1. **Heartbeat log**

* request id / heartbeat_id
* response status (202, 409, 401, etc.)
* rejection message if any (key_version_mismatch, invalid_signature, agent_version_too_old, etc.)
* latency

2. **Local checks**

* process check result
* port check result
* optional RCON check result
* last exception

3. **Export bundle**

* “Download diagnostics zip” (no secrets)

  * config (redacted)
  * last 500 log lines
  * environment summary

---

#### D) Settings

* API base URL
* Cluster key (rotate here)
* Heartbeat cadence defaults
* Minimum log level
* Update channel (stable/beta)

---

## 3) Health checks (how the agent decides “online”)

You want checks that are:

* Reliable
* Fast
* Not invasive
* Don’t require ASA mods

### 3.1 Recommended check ladder (MVP)

Per server, compute a final status using a simple ladder:

1. **Process check** (optional but very useful)

* If running server on same host, check:

  * Windows: process name / command line match
  * Linux: PID file or process scan
* If process exists → proceed; if not → likely offline

2. **UDP/TCP port reachability**

* If query port reachable → good sign
* If unreachable → degrade

3. **Game query (best if available)**

* If ASA exposes a query endpoint you can hit without mods, do it.
* If not, keep it at port + process for MVP.

4. **Optional RCON**

* If owner configures it, query lightweight info (map/players)
* If not configured, heartbeat still works (status-only)

### 3.2 Output normalization

Agent produces:

* `status`: online/offline/unknown
* `map_name`: from config or detected
* `players_current/capacity`: only if detected; else null

---

## 4) Cryptography & key lifecycle

### 4.1 What exists today (and you should build around)

* Cluster keypair generation/rotation exists on backend
* Heartbeat signature verification uses cluster public key + key_version

### 4.2 Agent requirements

Agent must:

* Store cluster private key **locally**
* Include `key_version` in every heartbeat
* Sign canonical heartbeat envelope (exact field set/order rules)

### 4.3 Rotation UX (local agent)

When you rotate keys on the website:

* Cluster `key_version` increments and `public_key_ed25519` changes
* Old agent signatures start failing with key mismatch or invalid signature

Agent UI should handle this cleanly:

* Detect response `409 key_version_mismatch` or `401 invalid_signature`
* Show **banner**: “Key rotation detected. Update your cluster private key.”
* Provide a Settings screen to paste new private key and set new key_version (or auto-derive key_version if you add a metadata endpoint—see backend prep)

---

## 5) Backend prep (to make the agent UX excellent)

You can ship MVP agent with *no new backend endpoints* beyond heartbeat. But if you want a smooth UX (especially around key_version and server mappings), add these:

### 5.1 Strongly recommended endpoints (owner-authenticated)

1. **List servers in cluster (owner)**

* `GET /api/v1/clusters/{cluster_id}/servers`
* Returns: `[{ server_id, name, map_name, is_self_hosted, ... }]`
* Purpose: agent UI can import server IDs instead of manual copy/paste hell

2. **Get cluster agent config (owner)**

* `GET /api/v1/clusters/{cluster_id}/agent-config`
* Returns:

  * `cluster_id`
  * `key_version`
  * `heartbeat_grace_seconds`
  * `min_agent_version`
* Purpose: agent UI always knows what key_version it should be using

**How to make this work without putting a Supabase JWT on the game host**

* Add a **short-lived “agent bootstrap token”** minted in dashboard:

  * `POST /api/v1/clusters/{id}/agent-bootstrap-token`
  * returns `token` (10 minutes)
* Agent UI accepts token once, exchanges it for:

  * cluster config + server list
* Token is then discarded; agent keeps only cluster private key + server IDs

This avoids storing a long-lived user auth token on the server machine.

### 5.2 Nice-to-have (post-MVP)

* `agent_instances` table:

  * instance id, hostname, created_at, last_seen_at, version
* “this agent is alive” view in dashboard

---

## 6) Local storage & security

### 6.1 Storage choices

**Option A (simple):** single JSON config file

* Pros: fast to build
* Cons: harder to securely store secrets

**Option B (recommended):** SQLite + encrypted secrets

* Store non-secret config in SQLite
* Store secrets encrypted using OS keychain:

  * Windows Credential Manager
  * macOS Keychain
  * Linux Secret Service / libsecret (or a file encryption key derived from machine identity)

### 6.2 Hard rules

* Never log the private key
* Redact secrets in exports
* Bind UI to `127.0.0.1` by default (no LAN exposure)
* Provide explicit “Allow LAN access” toggle with warnings

---

## 7) Packaging & install playbook

### 7.1 Windows-first (most ASA self-hosters)

* Package agent as:

  * `asa-selfhosted-agent.exe`
* Provide:

  * `--install-service`
  * `--uninstall-service`
  * `--start`
  * `--stop`
* Service runs under a restricted account
* UI still served locally

### 7.2 Linux support (optional but straightforward)

* Binary or Node bundle
* Systemd unit generator:

  * writes unit file
  * enables + starts

### 7.3 Update strategy (don’t get fancy)

MVP:

* UI shows “Update available” if agent_version < min_agent_version
* Manual download/install

Later:

* auto-updater (only after you trust your release pipeline)

---

## 8) Agent-to-backend contract (implementation checklist)

Agent must match your backend contract precisely:

### 8.1 Canonical signing checklist

* Build envelope object containing only signed fields
* Normalize timestamp to RFC3339 `YYYY-MM-DDTHH:MM:SSZ`
* JSON stringify with:

  * sorted keys
  * no whitespace
  * include nulls (don’t omit)
* Ed25519 sign
* Base64 signature

### 8.2 Heartbeat scheduling checklist

* Default interval: 60s
* Per-server jitter: ±10%
* Retry on network failure:

  * exponential backoff (cap at 5 minutes)
* On HTTP 202:

  * success; record last accepted
* On 401 invalid_signature:

  * stop spamming; show “key invalid”
* On 409 key_version_mismatch:

  * stop spamming; show “update key_version/private key”
* On “agent_version_too_old”:

  * stop; show “upgrade agent”

---

## 9) Testing & validation plan (don’t skip this)

### 9.1 Local test harness

* A CLI mode:

  * `agent doctor`
  * validates config
  * runs checks once
  * signs a heartbeat
  * prints canonical payload + signature length
* A dry-run mode:

  * outputs the exact JSON that would be POSTed

### 9.2 Integration test checklist

For each server:

1. Stop server process → expect offline
2. Start server → expect online within 2 cycles
3. Rotate cluster key → agent should fail with mismatch and not spam
4. Paste new private key + version → agent resumes
5. Disconnect internet → agent queues/retries without crashing

---

# Recommended build order (so you don’t thrash)

1. **Agent skeleton**

* local web UI + config persistence + scheduler

2. **Single-server heartbeat**

* sign + send to `/heartbeat`
* confirm backend updates server `status_source='agent'`

3. **Multi-server support**

* config + table view + per-server cadence

4. **Health checks**

* port/process ladder, then optional RCON later

5. **Diagnostics**

* logs, export bundle, clear rejection messages

6. **Packaging**

* service install + startup behavior

7. **Backend UX helpers**

* bootstrap token + cluster/server list endpoints (if you choose)

---

## Two key design decisions you should make now

1. **Does the agent “own” the cluster private key, or does each server have its own private key?**
   Your backend currently verifies with a **cluster public key**, so the agent holding the **cluster private key** is consistent and simplest. It also matches “cluster identity” and one-to-many operation. 

2. **Do you want the agent to require a web login/token at all?**
   You can do manual copy/paste (MVP), but the bootstrap-token approach dramatically improves UX without creating long-lived secrets on the host.
