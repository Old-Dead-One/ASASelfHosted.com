# Working Docs Index

Single entry point for ASA Self-Hosted documentation. Use this to find the right doc.

**Last updated:** 2026-02-02

---

## Design (canonical product scope)

| Doc | Purpose |
|-----|---------|
| **docs/design/1_DESCRIPTION.txt** | Project vision, registry, discovery, trust. |
| **docs/design/2_FEATURE_LIST.txt** | Feature list and 90% MVP scope lock. |
| **docs/design/3_TECH_STACK.txt** | Tech stack. |
| **docs/design/4_Dev_Plan.txt** | Development plan, sprints, MVP scope. |
| **docs/design/5_Appendix.txt** | Competitive reference, page architecture, account model. |
| **DECISIONS.md** (root) | Official decisions that override design-doc mismatches. |
| **docs/design/README.md** | Short index of the design docs in this folder. |

---

## Current work (sprints and backlog)

**Single TODO list:** **SPRINT_8_TODO.md** — all open items (no other TODO lists).

| Doc | Purpose |
|-----|---------|
| **SPRINT_8_TODO.md** (root) | **Only backlog** — all open items from all sprints. |
| **FinalCheck.md** (root) | Pre-launch checklist (env, DB, auth, trust pages, contact, post-deploy). |
| **GAP_ANALYSIS.md** (root) | Implementation vs design; MVP complete analysis; what’s done and what’s not. |

---

## Reference (how things work)

| Doc | Purpose |
|-----|---------|
| **docs/RANKING.md** | Ranking/sort contract: rank_by options, quality score, backend/frontend behavior. |
| **docs/TRUST_PAGES.md** | Trust pages (/verification, /consent) content and acceptance criteria. |
| **docs/SERVER_IMAGES.md** | Server images feature spec (banner upload, moderation). |
| **docs/REFERENCE_SCHEMA_SPRINT0_TO_5.md** | Schema reference. |
| **docs/MVP_VS_DESIGN_SUMMARY.md** | One-page status vs original design docs; complete vs beyond MVP. |
| **docs/Trust_Claims_Audit.md** | Trust claims vs enforcement (for audits). |
| **docs/STEAM_OAUTH_TODO.md** | Steam OAuth implementation notes (when needed). |

---

## Setup and development

| Doc | Purpose |
|-----|---------|
| **README.md** (root) | Project overview, mission, tech stack, getting started. |
| **INSTALL.md** (root) | Installation (backend + frontend). |
| **SUPABASE_SETUP.md** (root) | Supabase setup. |
| **DEV_NOTES.md** (root) | Ports, workflow, principles; links to DECISIONS. |
| **docs/design/PROJECT_STRUCTURE.md** | File and folder layout. |
| **frontend/SETUP.md** | Frontend setup, shadcn, env. |
| **frontend/STYLE_GUIDE.md** | Frontend style and components. |
| **frontend/TESTING.md** | Frontend testing. |
| **backend/README.md** | Backend overview. |
| **backend/TEST_RUNNING_GUIDE.md** | How to run backend tests. |
| **backend/app/db/migrations/README.md** | Migrations overview. |

---

## What was removed or merged

- **BACKEND_CLEANUP_COMPLETE.md** — Deleted (one-time completion report).
- **docs/CURRENT_PROGRESS_AND_SPRINT_7.md** — Deleted (superseded by GAP_ANALYSIS and Sprint 7/8 TODOs).
- **docs/REVIEW_5_Appendix_vs_Design_Docs.md** — Deleted (one-time review; recommendations applied).
- **frontend/CODE_REVIEW.md** — Deleted (one-time review; fixes applied).
- **EMAIL_VERIFICATION_TODO.md** — Merged into FinalCheck; deleted as standalone.
- **6_Trust_Claims_Audit.txt** — Deleted; content in docs/Trust_Claims_Audit.md.
- **frontend/STEAM_OAUTH_TODO.md** — Moved to docs/STEAM_OAUTH_TODO.md.
- **Root 1–5 .txt design docs** — Moved to docs/design/.
- **frontend/SPRINT_6_CHECKLIST.md** — Was moved to docs/sprints/, then deleted; completion status in GAP_ANALYSIS.
- **frontend/src/lib/tokens.md** — Merged into frontend/STYLE_GUIDE.md.
- **SPRINT_7_TODO.md** — Deleted; single backlog is SPRINT_8_TODO.md.
- **SPRINT_7_PLAYBOOK.md** — Deleted; trust content moved to docs/TRUST_PAGES.md.
- **docs/SPRINT_7_SPOTLIGHT.md** — Deleted; criteria in SPRINT_8_TODO Spotlight section.
- **docs/SPRINT_7_SERVER_IMAGES.md** — Renamed to docs/SERVER_IMAGES.md.
- **docs/sprints/SPRINT_6_CHECKLIST.md** — Deleted; completion status in GAP_ANALYSIS.
