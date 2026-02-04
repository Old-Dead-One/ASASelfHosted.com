# Sprint 8 — Playbook and Status

**Theme:** Hardening, alignment, and trust completion.  
**Goal:** Make ASA Self-Hosted boringly reliable, legally defensible, and internally obvious.

**Status (as of 2026-02-03):** Playbook 8.1–8.8 is **complete**. See status tables below. Ongoing backlog is in [TODO.md](TODO.md).

---

## Playbook (8.1–8.8)

### 8.1 Architecture & Contract Hardening

**Deliverables:** Canonical ingest contract (versioned event schemas, allowed/rejected fields); consent resolution layer (“is this data allowed right now?”); drop-on-violation policy (silent drop vs audit log per class).

**Exit criteria:** Every ingest path calls consent gate; no data reaches storage without it; violations observable but non-leaky.

### 8.2 Plugin Verification & Abuse Defense

**Deliverables:** Strict signature validation (timestamp window, replay protection); plugin version enforcement (min version, soft-fail); invalid payload audit trail (stored separately).

**Exit criteria:** Replayed/malformed packets do nothing; owners can see why data was rejected.

### 8.3 Backend Logic Realignment

**Deliverables:** Responsibility map (Supabase vs FastAPI); service layer boundaries; background job review (idempotency, retry, dead-letter).

**Exit criteria:** A new dev could explain where logic belongs; no cross-layer assumptions.

### 8.4 Frontend Trust UX Pass

**Deliverables:** Consent state visualization (inactive/partial/active); disabled-state explanations; owner & player assurance copy (“Nothing is collected until you do X in-game”).

**Exit criteria:** Users never wonder if something is happening secretly; every locked action explains itself.

### 8.5 Admin & Moderation Foundations

**Deliverables:** Admin-only views (flagged servers, signature failures, anomaly spikes); manual overrides (hide, freeze badges, rate-limit); incident notes (internal annotations).

**Exit criteria:** Respond to abuse without DB surgery.

### 8.6 Data Lifecycle & Compliance Reality

**Deliverables:** Retention rules; purge mechanics (user deletion, consent revocation); backup & restore posture.

**Exit criteria:** Privacy policy maps to reality; deletion requests are boring, not scary.

### 8.7 Operational Readiness

**Deliverables:** Failure mode matrix; degraded-mode behavior; alerting thresholds (actionable only).

**Exit criteria:** First outage does not require improvisation.

### 8.8 Definition of Done

Sprint 8 complete when: platform defensible legally/technically/publicly; every data path consent-gated; predictable under failure; future work feels safe.

---

## Status Summary

| Section | Status | Notes |
|---------|--------|------|
| **8.1** | Done | [OPERATIONS.md](OPERATIONS.md) (Ingest Contract, Drop-on-Violation); consent gate in `app/middleware/consent.py`; malformed_payload and unknown_field recorded to ingest_rejections. |
| **8.2** | Done | Ed25519 in `core/crypto.py`; replay via UNIQUE(server_id, heartbeat_id); MIN_AGENT_VERSION; ingest_rejections for all audit paths. |
| **8.3** | Done | [OPERATIONS.md](OPERATIONS.md) (Responsibility Map, Background Jobs); ingest → consent → write; worker runs engines. |
| **8.4** | Mostly done | Consent state on Consent page and dashboard; ServerForm/Dashboard tooltips for disabled actions. |
| **8.5** | Done | `api/v1/admin.py`: rejections-summary, PATCH hidden_at/badges_frozen, incident-notes. |
| **8.6** | Documented | [OPERATIONS.md](OPERATIONS.md) §8; account deletion “by request” (Sprint 9). |
| **8.7** | Done | [OPERATIONS.md](OPERATIONS.md) (Failure Modes, Alerting). |
| **8.8** | Met | Contracts, consent gate, failure docs, responsibility map in place. |

**Next:** Backlog and Sprint 9 are in [TODO.md](TODO.md). For runbooks, wire [OPERATIONS.md](OPERATIONS.md) §5 and §6 into monitoring.
