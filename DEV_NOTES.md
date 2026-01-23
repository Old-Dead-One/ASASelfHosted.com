# Development Notes

This file contains development context, decisions, and notes for the ASASelfHosted.com project.

**I will reference this file throughout our work together to maintain context and consistency.**

---

## Current Setup

### Port Configuration
- **Backend**: Running on port `5173`
- **Frontend**: Running on port `3000`
- **API Base URL**: `http://localhost:5173` (configured in frontend `.env`)

### Development Environment
- Backend: FastAPI + Python
- Frontend: Vite + React + TypeScript
- Both servers running successfully ✅
- CORS configured and working ✅

---

## Architecture Decisions

### API-First
- All functionality exposed via REST API
- Frontend is a thin client
- No business logic in React components

### Consent-First
- No data collection without explicit consent
- Consent is time-bound and revocable
- Both server owner AND player must agree where applicable

### Least Privilege
- Supabase RLS policies enforce permissions
- Backend uses service role key sparingly
- Most operations go through RLS, not service role

### Supabase as Source of Truth
- Authentication via Supabase Auth
- Database: Supabase Postgres
- Row Level Security (RLS) mandatory on all tables

---

## Development Workflow

### Before Starting New Features
1. Check this file for relevant context
2. Review `PROJECT_STRUCTURE.md` for file organization
3. Follow architectural principles above

### When Making Decisions
- Document significant decisions here
- Note any deviations from original architecture
- Record trade-offs and reasoning

### Git Commit Reminders
**IMPORTANT:** After making large changes or multiple file edits, prompt to commit:
- After completing a major step/feature
- After editing 5+ files
- After implementing a new component/endpoint
- After database schema changes
- At natural stopping points in development

**Commit workflow:**
1. `git add .` - Stage changes
2. `git commit -m "Descriptive message"` - Create local backup
3. `git push` - Upload to GitHub

Always remind to commit after significant work to prevent data loss.

---

## Official Decisions (Override Any Doc Mismatches)

### 1. Agent vs ASA Server API Plugin — MVP Scope
**Decision:** MVP builds the **Local Host Agent first**. Plugin is post-MVP/optional.

- **Agent (MVP):** Verification and heartbeat reporter (runs outside ASA ecosystem)
- **Plugin (post-MVP):** Deeper automation + in-game consent flows + richer telemetry

**Rationale:** Reliable server status verification without depending on in-game mod/plugin constraints.

### 2. Database Model Alignment
**Decision:** Sprint 0 schema includes only what Web MVP needs + minimal Verified plumbing.

**Sprint 0 includes:**
- Core directory tables (servers, clusters minimal, favorites, etc.)
- Single "heartbeats" table (generic) keyed by server_id with source field
- `directory_view` (public read model for directory)

**Sprint 2 includes:**
- Full agent tables (agents, agent_instances, agent_heartbeats)

**Rationale:** Keep schema stable, avoid rewrite later. Directory view needed for consistent public listing queries.

### 3. Subscription Model Timing
**Decision:** Subscription plumbing is in MVP, but minimal and "off by default."

**MVP scope:**
- Stripe webhook endpoint scaffolding
- DB tables for subscription state and license/key quota concept
- Minimal UI (placeholder/stub is fine)

**Not in MVP:**
- Full pricing UX, upgrades, invoices, etc.

**Rationale:** Feature List explicitly calls out "Subscription plumbing (even if minimal UI)" in MVP scope lock.

### 4. Cluster Model Timing
**Decision:** Cluster data model is MVP. Cluster pages are Phase 1.5.

**MVP scope (data-only):**
- `clusters` table
- Server-to-cluster association
- Cluster key metadata (no plaintext private keys)
- Display-only: show cluster name on server page, view-only association

**Not in MVP:**
- Cluster pages, dashboards, analytics, "Full map coverage" views

**Rationale:** Feature List shows cluster pages in Phase 1.5, but data model needed for MVP features.

### 5. Design Direction
**Decision:** Set up lightweight token structure now (Tailwind config + CSS variables), but don't over-engineer full design system.

**"Tactical Sci-Fi accents" means:**
- Base: Clean, classic SaaS registry (white/near-black, strong spacing, readable type)
- Accents: Subtle "ops console" vibe without neon gamer UI
- Use: Muted slate/graphite surfaces, thin separators/cards/panels, small mono/technical touches, lucide-style icons sparingly
- Avoid: Glowing gradients, heavy scanlines, "HUD overload"

**Rationale:** Classic registry foundation with personality, but not over-designed.

### 6. Payment Service Research
**Decision:** Wait. Don't research alternatives now.

**Use Stripe as default** until real traction and fee sensitivity is proven. Revisit alternatives post-launch.

**Rationale:** Subscriptions need proper recurring billing and webhooks. Many alternatives are messy for this.

### 7. Verification Model — Status Precedence
**Decision:** Implement only schema hooks in Sprint 0. Full RYG logic in Sprint 2.

**Sprint 0:**
- Schema: `servers.status` (manual) + fields for `status_source`, `last_seen_at`, `effective_status`
- Or: `server_status` table that view reads from (minimal)

**Sprint 2:**
- Full precedence logic: agent beats manual if fresh, stale = degrade confidence, compute R/Y/G

**Rationale:** Keep MVP moving without reworking data shape later.

### 8. MVP Scope — Definitive Source
**Decision:** Feature List "90% MVP Scope Lock (30 days, solo dev)" is the **definitive MVP scope**.

**Dev Plan is secondary:** Useful for sequencing and implementation notes, but does not override scope lock.

**MVP must include (from scope lock):**
- Website: Public directory, search, manual + verified status, favorites, player accounts, server pages + join instructions, one carousel (Newbie), basic badges, subscription plumbing (minimal), classy ad space
- Plugin/Agent: Secure key system, server verification, auto status, map identity, cluster grouping, heartbeat endpoint
- Discord: Optional / can slip

---

## Notes & Context

<!-- Add your development notes, decisions, and context below -->

---

## Quick Reference

### Key Files
- `DECISIONS.md` - **Official decisions (override any doc mismatches)**
- `PROJECT_STRUCTURE.md` - Complete file/folder structure
- `VERIFICATION.md` - Setup and verification checklist
- `INSTALL.md` - Installation instructions
- `README.md` - Project overview
- `1_DESCRIPTION.txt` - Project description
- `2_FEATURE_LIST.txt` - **Definitive MVP scope**
- `3_TECH_STACK.txt` - Technology stack
- `4_Dev_Plan.txt` - Development plan (secondary, for sequencing)

### Important Principles
1. **API-first**: Backend enforces rules, not UI
2. **Consent-first**: No silent data collection
3. **Least privilege**: RLS is the boss
4. **Supabase as source of truth**: Auth, DB, permissions

---

*Last updated: 2026-01-22 - Sprint 4 complete (agent pipeline, heartbeat processing, derived metrics)*
