# Sprint 9

**Status:** Completed (pre-launch log in FinalCheck.md). This doc is the playbook + historical context.

---

## Sprint 1–8 Review (Reality Check)

### What's solid and launch-worthy

**Architecture & boundaries**

* Clear separation of concerns: Supabase as source of truth, FastAPI for privileged ops, frontend purely consumer-facing. This is the right long-term shape 
* RLS-first mindset is consistent and correctly applied.
* Plugin consent model is exceptionally well thought out and defensible. This is not hand-wavy compliance; it's hard constraints 

**Trust & legality**

* Privacy Policy, Consent model, and Design Intent are aligned philosophically and technically.
* You can truthfully say "we cannot collect X" and mean it. That's rare.
* No pay-to-rank claims; ranking explicitly data-driven, which protects you later 

**Directory core**

* Directory schema, filters, favorites, and basic ranking inputs are present.
* Cursor pagination and seek predicates are the correct choice for scale.
* Manual vs verified status is clear and not misleading.

**Plugin & heartbeat pipeline**

* Cryptographic model is correct (Ed25519, signed payloads, offline verification).
* Cluster key model is sound and future-proof.
* Heartbeat ingestion exists and is sane.

---

### Where Sprints 1–8 stop short (important)

These are not failures—just natural MVP edges that Sprint 9 should close.

1. **Contact & data-rights are documented but not fully operational**

   * Policies reference "contact us" and data requests, but there's no guaranteed working intake path yet.
   * Account deletion is policy-described but not fully wired end-to-end.

2. **Abuse limits exist conceptually, not enforced**

   * Nothing prevents a single user from creating unlimited servers/clusters today.
   * This is a launch blocker, not a Phase 2 problem.

3. **Ranking truth vs UI implication**

   * `quality_score`, `rank_by`, and "Top/Hot" concepts exist, but without one canonical source of truth that both frontend and backend defer to.
   * Risk: accidental "implied global ranking" claims.

4. **Agent enablement still assumes manual steps**

   * Keys can exist, but owners don't yet have a clean self-service path to generate, rotate, and revoke them without DB access.

5. **Dashboard is still CRUD-oriented**

   * It needs to become a *hub*, not just a management screen, or users will keep bouncing back to the directory.

All of these are exactly what your proposed Sprint 9 targets—so your instinct is right.

---

## SPRINT 9 — PLAYBOOK (Edited & Final)

**Theme:** Launch readiness and agent enablement
**Sprint goal:** Ship a defensible, usable, and honest MVP that server owners can actually adopt.

> Sprint 9 is the line between "technically impressive" and "publicly shippable."

---

## 9.1 Launch blockers: contact & abuse limits

### Objective

Ensure legal contactability and prevent obvious platform abuse before launch.

### Deliverables

#### Contact & intake

* Implement a working **Contact page** (`/contact`)

  * Acceptable implementations:

    * Supabase-backed form (Edge Function + table)
    * Support email (mailto + documented SLA)
  * Must satisfy references from:

    * Privacy Policy
    * Data Rights page
    * Footer links
* Document handling flow:

  * Where messages land
  * Who reviews them
  * Retention window

#### Per-user limits (hard enforcement)

* Enforce **server-per-user limit** at backend create time

  * Example default: `MAX_SERVERS_PER_USER=10`
* Optional but recommended: **cluster-per-user limit**
* Limits must be:

  * Enforced in API
  * Reflected in UI ("7 of 10 servers used")
  * Configurable via env, not magic numbers

### Exit criteria

* All "contact us" references resolve to a working path.
* Exceeding limits produces a clear, user-facing error.
* Limits cannot be bypassed via direct API calls.

---

## 9.2 Data rights & compliance (truth alignment)

### Objective

Ensure policies describe *actual behavior*, not intended behavior.

### Deliverables

#### Account deletion & data rights

* Implement or explicitly document:

  * How a user requests deletion
  * How identity is verified
  * What data is deleted vs anonymized
* If automated deletion is deferred:

  * Provide a documented manual process
  * Ensure policies say "by request" not "automatic"

#### Trust claims audit

* Reconcile:

  * Privacy Policy
  * Consent page
  * TRUST_PAGES.md
  * Actual backend behavior
* Remove or soften any claim that implies:

  * Automatic collection
  * Retroactive data
  * Server-side enablement

### Exit criteria

* No page claims functionality that does not exist.
* A reasonable person could read the policies and not be misled.

---

## 9.3 Directory ranking: single source of truth

### Objective

Prevent accidental misrepresentation of ranking and quality signals.

### Deliverables

#### Canonical ranking documentation

* `docs/RANKING.md` becomes authoritative:

  * Meaning of each `rank_by` option
  * How `quality_score` is calculated
  * Explicit statement: **rankings are not sold**
  * How NULLs are handled
  * Pagination behavior
* Backend and frontend must conform to this doc.

#### Frontend alignment

* Sort labels match `RANKING.md` language.
* `quality_score` displays clearly or as "—" when absent.
* No UI implies "global rank" unless computed.

#### Backend alignment

* Consistent ordering:

  * Primary: selected rank column
  * Secondary: stable tie-break (id or created_at)
  * NULLs last for numeric sorts
* `rank_position` / `rank_delta_24h` explicitly documented as **not yet computed**.

### Exit criteria

* No ranking ambiguity.
* You could defend ranking behavior publicly without caveats.

---

## 9.4 Dashboard as a real hub

### Objective

Make the dashboard the logged-in home, not a detour.

### Deliverables

#### Favorites section

* Display user's favorited servers on dashboard.
* Allow unfavorite directly from dashboard.
* Reuse directory card/row patterns where possible.

#### Privacy & consent placeholder

* Add a visible section:

  * "Privacy & Consent (In-Game)"
  * Link to Consent page
  * Mark advanced controls as "Coming soon"
* This reinforces trust even before plugin rollout.

### Exit criteria

* Logged-in users immediately see *their* data.
* Consent story is discoverable without digging.

---

## 9.5 Agent enablement: key generation & rotation

### Objective

Remove all manual DB steps from heartbeat onboarding.

### Deliverables

#### Backend

* Endpoint to generate Ed25519 keypairs:

  * Scope: cluster (preferred) or server
  * Store public key
  * Return private key **once**
* Support:

  * Revocation
  * Rotation (invalidate old, issue new)
* Log key lifecycle events.

#### Frontend

* Dashboard UI to:

  * Generate key
  * Copy private key (one-time warning)
  * View key status (active / revoked)
  * Rotate key
* Provide minimal setup instructions.

### Exit criteria

* Owner can go from dashboard → heartbeat without admin help.
* Lost keys are recoverable via rotation, not support tickets.

---

## 9.6 Pre-launch verification

### Objective

Final honesty and stability pass before public launch.

### Deliverables

* Run **FinalCheck.md** end-to-end:

  * Auth states
  * Directory visibility
  * Favorites
  * Password handling
  * Trust pages
* Repeat **trust claims audit**
* Log:

  * Known gaps
  * Deferred items
  * Explicit Phase 1.5 scope

### Exit criteria

* FinalCheck completed or exceptions documented.
* No unresolved trust contradictions.

---

## Explicitly Out of Scope (Locked)

* Server image uploads
* Cluster pages & cluster-scoped UX
* Local agent binary
* Multi-select ruleset filters
* Full account settings UI
* Auto map creation on server add

These are Phase 1.5+ and should **not** leak into Sprint 9.

---

## Sprint 9 Definition of Done

Sprint 9 is complete when:

* Contact and data-rights paths work in practice.
* Abuse limits are enforced, visible, and configurable.
* Ranking behavior is documented, honest, and consistent.
* Dashboard feels like "home" for logged-in users.
* Server owners can self-service agent keys.
* A public launch would not embarrass you six months later.
