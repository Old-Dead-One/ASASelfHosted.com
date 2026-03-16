# WRAP_IT_UP_GAMEPLAN

## 0) Lock the finish line (non-negotiable scope)

### Ship in v1 (public launch)

1. **Web directory MVP** (already largely done)
2. **Owner dashboard** (CRUD) + **cluster + key UX**
3. **Heartbeat ingestion** (already implemented) + **“unknown” status support**
4. **Local Agent v0.1** (runs on the same host as ASA servers; sends signed heartbeats)
5. **Launch hardening**: contact wiring + limits + FinalCheck pass

### Explicitly defer (v1.1 / Phase 1.5)

* Stripe/subscriptions endpoints + webhooks (currently stubbed)
* Consent/verification API endpoints (trust pages exist; API stubs are fine to defer)
* Server images moderation/upload
* Multi-select ruleset filter polish
* Cluster public pages (optional)

---

## 1) Fix the “known gaps” visible in this repo (1–2 short passes)

### 1.1 Contact page is still a placeholder (must fix)

**Current:** `frontend/src/pages/ContactPage.tsx` explicitly says it’s not wired.
**Finish:** pick one of these and implement now:

* **Simplest:** mailto + support email displayed (zero backend)
* **Better:** POST to backend endpoint → send email via provider (Resend/SendGrid) or store ticket in Supabase table

**Deliverable checklist**

* Footer `/contact` works
* Privacy Policy + Data Rights references are true (no “will be wired” language)

---

### 1.2 “Unknown” status (align schema + UI)

You already have heartbeat signing fields whitelisted in backend `core/crypto.py` including `status`. Make sure `"unknown"` is accepted and handled.

**Backend**

* Add `"unknown"` to the status enum in your schemas and DB constraints (if any).
* Directory “effective_status” logic: treat unknown as its own state (display distinct), and decide ranking behavior (recommend: worse than online, better than offline).

**Frontend**

* Add badge/label and styling for Unknown.
* Ensure filter UI includes Unknown if status filtering exists.

---

### 1.3 Heartbeat response codes (clean and consistent)

Your earlier question matters for agent UX.

**Recommended**

* **202** for accepted (including replay/no-op)
* **401** invalid signature / missing public key
* **409** key_version_mismatch (include expected/got)
* **426** agent_version_too_old
* **429** rate-limited

Make sure the agent can branch on these codes without guesswork.

---

## 2) Cluster + keys: finish the product loop in the web app (high priority)

You already have backend endpoints for clusters and `/clusters/{id}/generate-keys` and frontend API bindings (`generateClusterKeys()` exists). What’s missing is the UX.

### 2.1 Add “Clusters & Agent Keys” section to Dashboard (must ship)

**Goal:** no DB edits to onboard an agent.

**UI components to add**

1. **My Clusters list**

   * Name, visibility, slug, created/updated
   * Buttons: View / Edit
2. **Key block per cluster**

   * Cluster ID [Copy]
   * Key version [Copy]
   * Public key (optional to show) [Copy]
   * Heartbeat URL [Copy]
   * Rotate keys (calls generate-keys)
   * One-time private key reveal modal:

     * Warning text
     * Copy button
     * “I saved it” checkbox to close

**Minimum content on that page**

* “Install agent”
* “Paste cluster private key”
* “Set API base / heartbeat URL”
* “Add servers to monitor (server IDs + local ports)”

### 2.2 Add “Copy Server ID” in the dashboard server list (must ship)

Your agent needs server IDs. Add a “Copy ID” action on each server card/row.

### 2.3 Decide your “one agent per machine” model in UI copy (must be clear)

Write it plainly in the UI:

* “Run one agent per host/VM. Configure it to monitor all servers running on that host.”

---

## 3) Local Agent v0.1 Playbook (what you build next)

This is the minimum agent that gives you a real verified directory.

### 3.1 Agent goals (v0.1)

* Run as a background service on the server host (Windows-first)
* Maintain a local config file
* Every N seconds:

  * collect status for each configured server
  * sign heartbeat envelope with **cluster private key**
  * POST to `/api/v1/heartbeat`
* Provide a basic UI:

  * shows each server row with R/Y/G (online/unknown/offline)
  * shows last heartbeat time + last error
  * “Test now” button

### 3.2 Agent architecture (keep it boring)

**Recommended stack:** Node.js + TypeScript (matches your frontend skillset and packaging options)

**Processes**

* `agent-core` (service): scheduler, checks, signing, network calls
* `agent-ui` (local web UI on localhost) or a lightweight desktop shell (later)

**Config**

* `config.json` stored in a predictable location (Windows ProgramData)
* Contains:

  * `api_base`
  * `heartbeat_url` (or derived)
  * `cluster_private_key_b64`
  * `cluster_id` (optional but nice)
  * `key_version`
  * `servers[]`: `{ server_id, label, host, query_port, rcon_port?, protocol?, notes? }`
  * `interval_seconds`

### 3.3 What the agent checks (v0.1)

Do not overreach. Pick checks that work reliably without RCON complexity.

**Suggested**

1. **Port open check** (TCP/UDP depending on what ASA exposes)
2. Optional: “query endpoint” if ASA provides one you can hit reliably
3. If checks fail due to permissions/network: set `status = "unknown"` not offline

**Mapping**

* Check passes → `online`
* Check definitively fails (connection refused, process absent if you implement local process check) → `offline`
* Any ambiguous failure (timeout, permission denied, host unreachable) → `unknown`

### 3.4 Heartbeat signing rules (must match backend canonicalization)

Backend signs only whitelisted fields. Agent must send exactly those fields correctly:

**Envelope**

* `server_id`
* `key_version`
* `timestamp` (RFC3339 UTC, `Z`, no ms)
* `heartbeat_id` (uuid)
* `status`
* `map_name` (optional but good if you can collect)
* `players_current`, `players_capacity` (optional; send null if unknown)
* `agent_version`

**Signature**

* Base64 Ed25519 signature over canonical JSON

### 3.5 Agent error handling (must be deliberate)

* `409 key_version_mismatch` → stop spamming, show banner: “Key rotation required, update key_version/private key”
* `401 invalid_signature` → stop spamming, show “bad key”
* `426` → stop and prompt update
* `429` → exponential backoff per server
* `5xx` → retry with jitter

### 3.6 Packaging (Windows v0.1)

* Use a Windows service wrapper (e.g., NSSM or node-windows) initially
* Provide “Install service / Uninstall service” helper commands
* UI can be a localhost page; later you can wrap it with Tauri/Electron if desired

---

## 4) Backend prep specifically for the Local Agent (do before agent ships)

### 4.1 Make heartbeat contract explicit and testable

* Add a `docs/AGENT_PROTOCOL.md` (single page)

  * request schema
  * signing/canonicalization
  * response codes
  * example payloads
* Add unit tests for:

  * canonicalization equivalence
  * signature verification
  * key_version mismatch behavior
  * replay detection

### 4.2 Rate limiting (current middleware is in-memory)

You have TODOs about Redis-based limiting. For launch:

* If you’re single-instance: in-memory is fine (just be honest)
* If you’re multi-instance behind a load balancer: you need Redis or Supabase-backed throttling

### 4.3 Cluster key rotation grace window (optional but high value)

Implement “accept previous public key for X minutes” after rotation to avoid outages.

* Store `previous_public_key` + `previous_key_expires_at`
* Verify against current; if fails and within window, verify against previous

This is small complexity with big reliability payoff.

---

## 5) Strip or quarantine “stubs” so they don’t look half-shipped

In the backend there are obvious stubs:

* subscriptions/stripe/webhooks
* consent endpoints
* verification endpoints

If they’re not shipping in v1:

* Ensure routes are either:

  * not mounted
  * return a clear 404
  * or are behind a feature flag
* Do not leave “TODO: implement” routes discoverable in prod unless you’re fine with that.

---

## 6) Launch hardening checklist (finish line)

Use this as your “done means done” gate.

### 6.1 Legal/trust surface

* Contact page wired (no placeholder language)
* Trust pages match reality (no “future” claims)
* Data rights request path is real and actionable

### 6.2 Abuse and limits

* Per-user server limit enforced backend-side
* Friendly UI error when limit hit

### 6.3 Pre-deploy smoke

Run `docs/FinalCheck.md` end-to-end:

* auth
* directory filters
* create/edit/delete
* favorites
* password hidden when logged out
* Spotlight carousel
* server page
* cluster selection in ServerForm
* heartbeat ingestion for at least one server

### 6.4 Production readiness

* env vars complete
* CORS locked down
* migrations applied
* error logging at least to stdout + structured logs

---

## 7) Suggested execution order (fastest path to “real”)

1. **Dashboard: Clusters + key generation UI + Copy buttons**
2. **Contact wiring**
3. **Unknown status end-to-end**
4. **Heartbeat response code cleanup**
5. **Agent protocol doc + backend tests**
6. **Local Agent v0.1 (core service + basic UI)**
7. **FinalCheck pass + deploy**