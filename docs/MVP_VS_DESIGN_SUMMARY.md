# Status vs Original Design Docs — Summary

One-page view of where we are against **docs/design/** (1_DESCRIPTION, 2_FEATURE_LIST, 4_Dev_Plan, 3_TECH_STACK) and what is beyond the original MVP.

**Last updated:** 2026-02-02

---

## Original MVP Scope (Design Docs)

- **90% scope lock (2_FEATURE_LIST):** Public directory, search, server listings, manual/verified status, favorites, player accounts, server pages, join instructions, **one carousel (Newbie)**, basic badges (Verified / New / PvE/PvP / Cluster), subscription plumbing (minimal), plugin secure key + verification + heartbeat.
- **Dev plan (4_Dev_Plan):** Sprints 0–2 (foundation, free directory, agent verified); Sprint 3 (badges + carousel + polish); stabilization (trust pages, docs). Local agent: UI, R/Y/G lights, heartbeat, Windows packaging. Password: dev plan said “favorite → reveal”; we use **account-gated** (authenticated only) per DECISIONS.

---

## ✅ Complete or Near Complete (vs Original MVP)

### Website — Core Directory (Always Free)

| Original design | Status |
|-----------------|--------|
| Server listings (individual) | ✅ Done — directory, pagination, filters |
| Status (online/offline) | ✅ Done — manual + agent-verified path |
| Manual: mod list, rates, wipe info, cluster (view-only) | ✅ Done |
| Public server page | ✅ Done — ServerPage with all details |
| Join instructions (PC / Console) | ✅ Done |
| Password field | ✅ Done — account-gated (authenticated users only) |
| Search & filters | ✅ Done — full panel (status, verification, game mode, ruleset, map, sort, limit) |
| Favorites (players) | ✅ Done — API + UI, persists |
| Player accounts | ✅ Done — auth (email/password, reset, session) |

### Website — Badge System (MVP set)

| Original design | Status |
|-----------------|--------|
| Verified | ✅ Done — agent-verified badge |
| Stable | ✅ Done — uptime-based |
| New | ✅ Done — recently added |
| PvE / PvP | ✅ Done |
| Vanilla / Boosted | ✅ Done |

*Hot, Long-Runner, cluster/player badges = Phase 1.5+ per design.*

### Website — One Carousel (Newbie)

| Original design | Status |
|-----------------|--------|
| One carousel: Newbie | ✅ Done — SpotlightCarousel (verified + boosted, rank by quality, limit 8, wrap-around) |

### Website — Subscription / Owner Side (MVP level)

| Original design | Status |
|-----------------|--------|
| Free accounts | ✅ Done |
| Server owner dashboard | ✅ Done — CRUD, manual status |
| Subscription plumbing | ⚠️ Stubbed — tables/endpoints exist, no checkout/UI |
| Key generation & rotation | ⚠️ Backend-ready; UI in backlog (SPRINT_8_TODO) |

### Plugin / Backend (Verified+ path)

| Original design | Status |
|-----------------|--------|
| Secure handshake (keys) | ✅ Done — Ed25519, cluster key model |
| Signed heartbeat | ✅ Done — `/api/v1/heartbeat`, replay protection |
| Server identity verification | ✅ Done |
| Map identity reporting | ✅ Done — heartbeat includes map_name |
| Cluster identity via private key | ✅ Done |
| Version reporting | ✅ Done — agent_version in heartbeat |
| Auto status updates | ✅ Done — heartbeat updates status |
| Auto uptime tracking | ✅ Done — uptime engine |

### Trust & Legal (Stabilization in dev plan)

| Original design | Status |
|-----------------|--------|
| Terms / Privacy | ✅ Done — Terms, Privacy Policy, Privacy (by Design), Data Rights |
| About | ✅ Done |
| FAQ | ✅ Done |
| Verification / Consent pages | ✅ Done — /verification, /consent (content per docs/TRUST_PAGES.md) |
| Contact | ✅ Done — page exists; wire form/email in backlog |

### Tech Stack (3_TECH_STACK)

| Original design | Status |
|-----------------|--------|
| Frontend: React, TypeScript, Vite, Tailwind, Radix/shadcn, TanStack Query, RHF, Zod, React Router | ✅ Done |
| Backend: Python, Pydantic, Supabase, FastAPI | ✅ Done |
| Auth: Supabase (email), RLS | ✅ Done |
| Storage (post-MVP: logos/banners) | Not in MVP — see “Beyond MVP” below |

---

## ❌ Not Done (Within or Beyond MVP)

- **Local host agent client** — 0% (backend ready). Original MVP included it; we deferred; platform is soft-launch ready without it.
- **Agent key/instance UI** — Backend ready; dashboard UI and key generation in SPRINT_8_TODO.
- **Player directory** — Not in MVP; Phase 1.5+ (player profiles, favorited clusters, activity).
- **Cluster pages / cluster management UI** — Phase 1.5+.
- **Extra carousels** — Top 100, Stability, Activity, Hot = Phase 1.5+.
- **Discord bot** — Post-MVP in design.
- **Pricing page** — Optional per dev plan; not built.

---

## Beyond Original MVP (Done or Planned)

Things the original 90% lock or dev plan did not require (or marked post-MVP) that we have done or will do:

| Item | Status | Note |
|------|--------|------|
| **Maps as first-class filter + table** | ✅ Done | Maps table, `GET /api/v1/maps`, directory filter by map, ServerForm dropdown + custom map. Not in original 90% lock. |
| **Discord URL + Website URL on servers** | ✅ Done | Backend + ServerForm + ServerCard + ServerPage. Not in original scope. |
| **Full trust & legal surface** | ✅ Done | Verification, Consent, Privacy (by Design), Legal (Privacy Policy + GDPR/CCPA §14), Data Rights, Contact, Terms, About, FAQ. Design had “Terms / Privacy”; we added full set for launch readiness. |
| **ToS acceptance at signup and before first server** | ✅ Done | TermsAcceptanceModal, profiles terms fields, `/api/v1/me/terms-acceptance`. Legal/audit. |
| **Hosting provider filter (self-hosted only)** | ✅ Done | Directory excludes non–self-hosted; “ASASelfHosted lists self-hosted servers only.” |
| **Server images (banner upload, moderation)** | 📋 Backlog | Design: “Storage (post-MVP: logos/banners)”. Spec in docs/SERVER_IMAGES.md; SPRINT_8_TODO. |
| **Account settings page** | 📋 Backlog | Profile, email/password change, deletion. Design had “Account settings” in tree; we have it in backlog. |
| **Contact form/email wiring** | 📋 Backlog | Page exists; form/email in SPRINT_8_TODO. |
| **Ranking clarity (rank_by, quality_score, docs)** | 📋 Backlog | docs/RANKING.md; backend/frontend alignment in SPRINT_8_TODO. |
| **Per-user limits (servers/clusters)** | 📋 Backlog | Pre-launch hardening in SPRINT_8_TODO. |
| **Favorites section on dashboard** | 📋 Backlog | Design had “Dashboard (favorites)”; we have favorites on home/directory; dedicated dashboard section in backlog. |

---

## Verdict

- **Web MVP vs design:** **Complete** for launch (directory, CRUD, favorites, one carousel, MVP badges, trust pages, maps, Discord/website URLs). Contact wiring and optional polish in SPRINT_8_TODO.
- **Agent MVP:** **Backend complete**; agent client and key/instance UI deferred; platform can ship without agent.
- **Beyond MVP already shipped:** Maps normalization, Discord/website URLs, full trust & legal set, ToS acceptance, self-hosted-only directory.
- **Single backlog:** **SPRINT_8_TODO.md** (agent UI, contact, images, account settings, ranking, limits, Phase 1.5).

For detailed gap tables and API status, see **GAP_ANALYSIS.md**.
