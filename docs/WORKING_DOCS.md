# Working Docs Index

Single entry point for ASA Self-Hosted documentation.

**Last updated:** 2026-02-03

---

## Design (canonical product scope)

| Doc | Purpose |
|-----|---------|
| **docs/design/1_DESCRIPTION.txt** | Project vision, registry, discovery, trust. |
| **docs/design/2_FEATURE_LIST.txt** | Feature list and 90% MVP scope lock. |
| **docs/design/3_TECH_STACK.txt** | Tech stack. |
| **docs/design/4_Dev_Plan.txt** | Development plan, sprints, MVP scope. |
| **docs/design/5_Appendix.txt** | Competitive reference, page architecture, account model. |
| **docs/DECISIONS.md** | Official decisions (override design-doc mismatches). |
| **docs/design/README.md** | Index of design docs. |
| **docs/design/PROJECT_STRUCTURE.md** | File and folder layout. |

---

## Current work and status

| Doc | Purpose |
|-----|---------|
| **docs/RELEASE_READINESS.md** | **Must / Should / Optional** for initial release (closed-group testing). Single list to get to test-ready. |
| **docs/TODO.md** | Single backlog — all open items (Sprint 9 done; Phase 1.5, images, etc.). |
| **docs/FinalCheck.md** | Pre-launch checklist (env, DB, auth, trust pages, post-deploy). |
| **docs/REMAINING_VS_DESIGN.md** | What’s left vs original design docs; complete vs not done; priority summary. |
| **docs/SPRINT_8.md** | Sprint 8 playbook + completion status (hardening, trust, ops). |
| **docs/SPRINT_9.md** | Sprint 9 playbook + status (launch readiness, contact, limits, key UI). |

---

## Reference (how things work)

| Doc | Purpose |
|-----|---------|
| **docs/RANKING.md** | Ranking/sort contract: rank_by, quality_score, backend/frontend behavior. |
| **docs/TRUST_PAGES.md** | Trust pages (/verification, /consent) content and acceptance criteria. |
| **docs/OPERATIONS.md** | Ingest contract, drop-on-violation, responsibility map, background jobs, failure modes, alerting. |
| **docs/SERVER_IMAGES.md** | Server images feature spec (banner upload, moderation). |
| **docs/OPERATIONS.md** | Contact handling, data lifecycle, ingest, jobs, failure modes (see §7–§8). |
| **docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md** | Historical schema reference (Sprint 0–5); current schema in migrations/README. |
| **docs/TRUST_PAGES.md** | Trust pages content + audit table (claims vs enforcement). |
| **docs/STEAM_OAUTH_TODO.md** | Steam OAuth implementation notes (when needed). |

---

## Setup and development

| Doc | Purpose |
|-----|---------|
| **README.md** (root) | Project overview, mission, tech stack, getting started. |
| **INSTALL.md** (root) | Installation (backend + frontend). |
| **SUPABASE_SETUP.md** (root) | Supabase setup. |
| **docs/DEV_NOTES.md** | Ports, workflow, principles; links to DECISIONS. |
| **frontend/SETUP.md** | Frontend setup, shadcn, env. |
| **frontend/STYLE_GUIDE.md** | Frontend style and components. |
| **frontend/TESTING.md** | Frontend testing. |
| **backend/README.md** | Backend overview. |
| **backend/TEST_RUNNING_GUIDE.md** | How to run backend tests. |
| **backend/app/db/migrations/README.md** | Migrations overview. |

---

## Removed or merged (2026-02-03)

- **ALERTING.md, BACKGROUND_JOBS.md, FAILURE_MODES.md, DROP_ON_VIOLATION.md, INGEST_CONTRACT.md, RESPONSIBILITY_MAP.md** — Merged into **docs/OPERATIONS.md**.
- **SPRINT_8_PLAYBOOK.md, SPRINT_8_STATUS.md** — Merged into **docs/SPRINT_8.md**.
- **MVP_VS_DESIGN_SUMMARY.md** — Superseded by **docs/REMAINING_VS_DESIGN.md**.
- **CONTACT.md, DATA_LIFECYCLE.md** — Merged into **docs/OPERATIONS.md** (§7 Contact handling, §8 Data lifecycle).
- **Trust_Claims_Audit.md** — Merged into **docs/TRUST_PAGES.md** (Audit section).
- **SPRINT_9_PLAYBOOK.md** — Renamed to **docs/SPRINT_9.md** (playbook + status).

Earlier removals (EMAIL_VERIFICATION_TODO, SPRINT_7_TODO, etc.) are in git history.
