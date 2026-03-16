# Sprint 10 — Agent Bootstrap + Opt-In Keys + API Hardening

**Theme:** Make Local Agent v0.1 possible without “server ID copy/paste.”  
**Sprint goal:** Add the missing backend + docs so a Windows-first agent can handshake using an **account key**, then (opt-in) register **cluster/server keys**, and only then transmit heartbeats.

**Status:** Planned.

---

## Scope lock (non-negotiable)

### In scope (must ship in Sprint 10)

- **Account Agent Key (per account)**: one-time private key reveal; backend stores public key.
- **Agent Bootstrap handshake**: agent can discover the owner’s clusters/servers **without the user copying server IDs**.
- **Opt-in key registration** (initial setup): user pastes **cluster/server private keys** into the agent; agent registers derived public keys.
- **Local Agent protocol doc**: one short canonical spec the agent implements against.
- **Stub endpoint quarantine**: Stripe/subscriptions/webhooks must not be “TODO endpoints” in production.

### Explicitly not in scope (Sprint 11)

- Building the actual agent executable and UI (that’s Sprint 11).
- Any “auto-monitor all servers everywhere” behavior (multi-host needs explicit opt-in per host).
- Stripe billing behavior (webhooks stay disabled).

---

## Playbook (10.1–10.8)

### 10.1 Account Agent Key (Generate Private Key)

**Objective:** The user can generate one **account agent private key** (shown once) and copy/paste it into the agent.

**Deliverables**

- **DB/Model**
  - Store **account agent public key** (base64 Ed25519) and key metadata.
  - Recommended fields on `profiles`:
    - `agent_public_key_ed25519 TEXT NULL`
    - `agent_key_version INTEGER NOT NULL DEFAULT 1` (optional but future-proof)
    - `agent_rotated_at TIMESTAMPTZ NULL` (optional)
- **API**
  - `POST /api/v1/me/generate-agent-key` (owner JWT)
    - Stores the derived public key.
    - Returns `{ public_key, private_key, key_version }` with “shown once” warning.
- **Frontend**
  - Add a **Generate Private Key** button (dashboard “Agent setup” or account/settings area).
  - One-time private key reveal + copy UX consistent with cluster/server key UX.

**Exit criteria**

- Owner can generate/rotate account agent key without DB access.
- Private key is only shown once in UI responses (no retrieval endpoint).

---

### 10.2 Agent Bootstrap handshake (keys-only discovery)

**Objective:** Agent learns **which servers/clusters exist** on the account from an agent-signed request.

**Deliverables**

- **Endpoint**
  - `POST /api/v1/agent/bootstrap` (no JWT; authenticated by signature)
- **Request contract**
  - `agent_public_key_ed25519` (base64)
  - `timestamp` (RFC3339 UTC `Z`, no ms)
  - `nonce` (uuid)
  - `agent_version`
  - `signature` (Ed25519 over canonical JSON of the above)
- **Auth rules**
  - Look up profile by `agent_public_key_ed25519`
  - Verify signature using stored public key
  - Enforce timestamp window (same philosophy as heartbeat)
  - Enforce replay protection via nonce (see 10.3)
- **Response**
  - Account-level:
    - `api_base`, `heartbeat_url`
    - `min_agent_version`, `rate_limit_hints` (human-readable OK)
  - Cluster inventory (owner-only)
    - `cluster_id`, `name`, `slug`, `visibility`
    - `key_version`, `has_public_key` (and optionally `public_key` if you decide it’s safe)
  - Server inventory (owner-only)
    - `server_id`, `name`, `map_name`, `join_address`
    - `cluster_id` (nullable)
    - `server_key_status`: `{ has_public_key, key_version }`
    - `monitoring_hints` (optional): last_seen/status_source/effective_status

**Exit criteria**

- Agent can list servers/clusters without any “copy server ID” UX.
- Bootstrap fails fast with explicit errors (401/409/426/429 patterns align with heartbeat where relevant).

---

### 10.3 Replay defense + rate limits for bootstrap

**Objective:** Prevent abuse (replay spam) and keep predictable semantics.

**Deliverables**

- Store `nonce` for a short TTL (e.g. 10–30 minutes) to prevent replay.
  - Minimal approach: `agent_bootstrap_nonces` table with `nonce`, `profile_user_id`, `created_at`, TTL cleanup.
- Apply rate limiting on bootstrap (per agent_public_key or per profile id).
- Return consistent status codes:
  - `202` success is not required here; `200` is fine.
  - `401` invalid signature / unknown key
  - `409` replayed nonce
  - `426` agent too old (min version)
  - `429` rate limited

**Exit criteria**

- Same request cannot be replayed successfully.
- Rate-limited behavior is stable and documented.

---

### 10.4 Opt-in key registration (cluster/server keys)

**Objective:** Support “opt-in first policy”: user pastes private keys into the agent; backend stores public keys.

**Deliverables**

- **Agent-auth endpoints** (authenticated by account agent key signature)
  - `POST /api/v1/agent/clusters/{cluster_id}/register-public-key`
  - `POST /api/v1/agent/servers/{server_id}/register-public-key`
- **Behavior**
  - Accept `{ public_key_ed25519, key_version? }`
  - Validate ownership (cluster/server belongs to the authenticated profile)
  - Store public key + version, set `rotated_at` timestamps
  - Return a minimal status object (has_key/version)

**Exit criteria**

- Agent can register public keys without JWT and without server IDs typed by user (agent chooses from bootstrap list).
- All writes are ownership-enforced.

---

### 10.5 Heartbeat verification policy (server keys + optional cluster key)

**Objective:** “Fully supported” key model without surprise breakage:

- **Server key** is the primary per-server auth mechanism.
- **Cluster key is optional**; it can provide cluster UX/badges and (optionally) a fallback verify path.

**Deliverables**

- Decide and document v1 behavior:
  - **Recommended v1:** accept server-key signatures for servers with server keys; cluster key not required to transmit.
  - Optional fallback: allow cluster-key signature when server key missing (default OFF, explicit setting).
- Ensure backend verification logic matches the chosen policy.
- If you implement fallback, the error messages should clearly indicate “expected server key” vs “cluster key missing.”

**Exit criteria**

- A user can paste only server keys and still transmit heartbeats.
- Cluster key presence can be surfaced as a UX badge without being required.

---

### 10.6 `docs/AGENT_PROTOCOL.md` (single canonical contract)

**Objective:** One authoritative spec the agent implements.

**Deliverables**

- `docs/AGENT_PROTOCOL.md` includes:
  - Bootstrap request/response schemas + examples
  - Canonicalization + signing rules (reference backend canonicalization)
  - Heartbeat request schema + examples
  - Response codes and how the agent should branch
  - Key registration endpoints + examples
  - Privacy/opt-in semantics: “Transmit Heartbeats” gating

**Exit criteria**

- Agent developer can implement without reading backend code.

---

### 10.7 Quarantine stub endpoints (Stripe/subscriptions/webhooks)

**Objective:** Keep Stripe plumbing in the repo, but do not ship discoverable “TODO endpoints.”

**Deliverables**

- Add feature flags in backend settings (examples):
  - `ENABLE_STRIPE_WEBHOOKS=false` default
  - `ENABLE_SUBSCRIPTIONS_API=false` default
- If disabled:
  - Do not mount routers **or** return `404` (preferred) from those endpoints.
  - Ensure docs + README don’t promise billing features in v1.

**Exit criteria**

- Hitting `/api/v1/webhooks/stripe` does not return “not yet implemented”.
- No stub endpoint becomes a “mystery 400” for scanners or curious users.

---

### 10.8 Test plan (Sprint 10)

**Backend tests**

- Generate account agent key returns one-time private key; stores public key.
- Bootstrap:
  - valid signature → returns inventory
  - invalid signature → 401
  - replayed nonce → 409
  - too old version → 426
  - rate limit → 429
- Key registration:
  - registers public key for owned server/cluster
  - rejects non-owned resources

**Documentation checks**

- `docs/AGENT_PROTOCOL.md` matches actual request shapes and status codes.

---

## Sprint 10 definition of done

- An agent can be built in Sprint 11 that requires **no manual server ID copy**.
- User can generate an **account key** and complete a first handshake.
- User can opt-in by pasting server keys; then enable transmit.
- Stripe/subscriptions/webhook stubs are safe in production (disabled/404).

