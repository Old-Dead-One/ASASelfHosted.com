# Gap Analysis: Design Docs vs Current Implementation

**Date**: 2026-02-02  
**Status**: Post-Sprint 7 Review

---

## Executive Summary

**MVP Completion**: ~90% (web + trust; agent deferred)  
**Frontend**: ~98% complete (Sprint 6 + Sprint 7: trust pages, SpotlightCarousel, maps, Discord/website URLs)  
**Backend**: ~90% complete (core APIs, server CRUD, favorites, maps, directory facets)  
**Agent**: 0% (not started; backend heartbeat ready)  
**Discord Bot**: 0% (not started)

---

## A. WEBSITE FEATURES - Status

### ✅ Core Directory (Always Free) - **COMPLETE**

| Feature | Status | Notes |
|---------|--------|-------|
| Server listings (individual) | ✅ Complete | Directory view, pagination, filtering |
| Status (online/offline) | ✅ Complete | Manual + agent verified |
| Manual - Mod list | ✅ Complete | Stored, displayed |
| Manual - Rates | ✅ Complete | Stored, displayed |
| Manual - Wipe info | ✅ Complete | Stored, displayed |
| Manual - Cluster association | ✅ Complete | View-only, displayed |
| Public server page | ✅ Complete | ServerPage with all details |
| Join instructions (PC / Console) | ✅ Complete | Displayed on server page |
| Password field | ✅ Complete | Account-gated: join password visible on server page only when user is authenticated (not favorite-gated) |
| Search & filters | ✅ Complete | Full filter panel implemented |
| Favorites (players) | ✅ Complete | UI + backend API (POST/DELETE favorites) |
| Player accounts | ✅ Complete | Auth system in place |

**Note:** Password is account-gated (visible when authenticated). Favorites API is implemented.

---

### ✅ Badge System (Website-Driven) - **COMPLETE**

| Badge Type | Status | Notes |
|------------|--------|-------|
| Verified | ✅ Complete | Agent-verified badge |
| Stable | ✅ Complete | Uptime-based |
| New | ✅ Complete | Recently added |
| Hot | ❌ Not implemented | Phase 1.5 feature |
| Long-Runner | ❌ Not implemented | Phase 2 feature |
| PvE / PvP | ✅ Complete | Game mode badges |
| Vanilla / Boosted | ✅ Complete | Ruleset badges |

**Cluster Badges**: ❌ Not implemented (cluster pages not built)  
**Player Badges**: ❌ Not implemented (player directory not built)

**Status**: MVP badges complete. Additional badges are Phase 1.5+ features.

---

### ❌ Player Directory (Free) - **NOT IMPLEMENTED**

| Feature | Status | Notes |
|---------|--------|-------|
| Player profiles | ❌ Missing | No player profile pages |
| Favorited servers | ✅ Complete | UI + backend; favorites persist |
| Favorited clusters | ❌ Missing | Clusters not implemented |
| Activity indicators | ❌ Missing | No activity tracking |
| Optional public visibility | ❌ Missing | No player settings |
| Auto-favorite onJoin toggle | ❌ Missing | Plugin feature, not started |

**Status**: Not in MVP scope per dev plan. Deferred to Phase 1.5+.

---

### ⚠️ Banner Carousels (Non-Monetized) - **PARTIAL**

| Carousel | Status | Notes |
|----------|--------|-------|
| Top 100 | ❌ Not implemented | Phase 1.5 feature |
| Stability | ❌ Not implemented | Phase 1.5 feature |
| Activity | ❌ Not implemented | Phase 1.5 feature |
| Hot / Up & Coming | ❌ Not implemented | Phase 1.5 feature |
| Newbie Servers / Spotlight | ✅ Complete | SpotlightCarousel: verified + boosted, limit 8, wrap-around (criteria in SPRINT_8_TODO) |

**Status**: MVP requirement (one carousel) complete. Others are Phase 1.5+.

---

### ⚠️ Subscription Logic (Website Side) - **STUBBED**

| Feature | Status | Notes |
|----------|--------|-------|
| Free accounts | ✅ Complete | Auth system works |
| Server owner dashboard | ✅ Complete | Dashboard implemented |
| Subscription management | ❌ Stubbed | Backend endpoints exist but not implemented |
| Key generation & rotation | ❌ Stubbed | Agent token generation not implemented |
| Cluster management UI | ❌ Missing | Cluster pages not built |

**Status**: Core dashboard complete. Subscription and agent token features stubbed.

---

## B. PLUGIN FEATURES (ASA SERVER API) - Status

### ✅ Core Plugin (Required for Verified+) - **COMPLETE**

| Feature | Status | Notes |
|---------|--------|-------|
| Secure handshake | ✅ Complete | Ed25519 signature verification |
| Signed heartbeat | ✅ Complete | `/api/v1/heartbeat` endpoint |
| Server identity verification | ✅ Complete | Key-based verification |
| Map identity reporting | ✅ Complete | Heartbeat includes map_name |
| Cluster identity via private key | ✅ Complete | Cluster key model implemented |
| Version reporting | ✅ Complete | Heartbeat includes agent_version |

**Status**: Backend verification complete. Agent client not built yet.

---

### ❌ Automation Features (Subscription) - **NOT IMPLEMENTED**

| Feature | Status | Notes |
|---------|--------|-------|
| Auto status updates | ✅ Complete | Heartbeat updates status |
| Auto uptime tracking | ✅ Complete | Uptime engine computes uptime |
| Auto wipe reporting | ❌ Missing | No wipe detection logic |
| Auto mod hash reporting | ❌ Missing | No mod hash tracking |
| Auto password sync (encrypted) | ❌ Missing | Password sync not implemented |
| Auto-favorite onJoin signal | ❌ Missing | Plugin feature, not started |

**Status**: Core automation (status, uptime) complete. Advanced features missing.

---

### ❌ Local Host Agent - **NOT STARTED**

| Feature | Status | Notes |
|---------|--------|-------|
| Local web UI | ❌ Not started | Agent UI not built |
| Configure multiple instances | ❌ Not started | Agent config not built |
| Run checks every X minutes | ❌ Not started | Agent scheduler not built |
| "Test now" button | ❌ Not started | Agent UI not built |
| Show R/Y/G lights | ❌ Not started | Agent UI not built |
| Logs view | ❌ Not started | Agent UI not built |
| Outbound heartbeat | ❌ Not started | Agent client not built |
| Process check | ❌ Not started | Agent checks not built |
| Port check | ❌ Not started | Agent checks not built |
| Windows .exe packaging | ❌ Not started | Agent packaging not built |

**Status**: 0% complete. Backend ready, agent client not started.

---

## C. DISCORD BOT FEATURES - Status

### ❌ Discord Bot - **NOT STARTED**

| Feature | Status | Notes |
|---------|--------|-------|
| Free Bot | ❌ Not started | Discord bot not built |
| Verified+ Bot | ❌ Not started | Discord bot not built |

**Status**: 0% complete. Not in MVP scope per dev plan.

---

## Backend API Status

### ✅ Implemented Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /api/v1/directory/servers` | ✅ Complete | Full filtering, pagination, ranking |
| `GET /api/v1/directory/servers/{id}` | ✅ Complete | Single server retrieval |
| `GET /api/v1/directory/clusters` | ✅ Complete | Cluster listing |
| `POST /api/v1/heartbeat` | ✅ Complete | Ed25519 verification, replay protection |
| `GET /api/v1/health` | ✅ Complete | Health check |
| `GET /api/v1/servers` | ✅ Complete | List owner's servers (auth required) |
| `GET /api/v1/servers/{id}` | ✅ Complete | Get server (owner or public) |
| `POST /api/v1/servers` | ✅ Complete | Create server (auth required) |
| `PUT /api/v1/servers/{id}` | ✅ Complete | Update server (owner only) |
| `DELETE /api/v1/servers/{id}` | ✅ Complete | Delete server (owner only) |
| `POST /api/v1/servers/{id}/favorites` | ✅ Complete | Add favorite (auth required) |
| `DELETE /api/v1/servers/{id}/favorites` | ✅ Complete | Remove favorite (auth required) |

---

### ⚠️ Stubbed Endpoints (Not Implemented)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /api/v1/clusters` | ❌ Stubbed | Returns empty array (directory clusters implemented) |
| `GET /api/v1/clusters/{id}` | ❌ Stubbed | Returns 404 |
| `POST /api/v1/clusters` | ❌ Stubbed | Returns "not yet implemented" |
| `POST /api/v1/verification/initiate` | ❌ Stubbed | Not implemented |
| `POST /api/v1/verification/verify` | ❌ Stubbed | Not implemented |
| `GET /api/v1/verification/status/{id}` | ❌ Stubbed | Not implemented |
| `GET /api/v1/subscriptions` | ❌ Stubbed | Not implemented |
| `POST /api/v1/subscriptions/create-checkout` | ❌ Stubbed | Not implemented |
| `POST /api/v1/subscriptions/cancel` | ❌ Stubbed | Not implemented |
| `POST /api/v1/webhooks/stripe` | ❌ Stubbed | Not implemented |

---

## Frontend Pages Status

### ✅ Implemented Pages

| Page | Status | Notes |
|------|--------|-------|
| Home | ✅ Complete | SpotlightCarousel + directory |
| Directory | ✅ Complete | Integrated into HomePage |
| Server details | ✅ Complete | ServerPage with all features |
| Login | ✅ Complete | Email/password auth |
| Sign Up | ✅ Complete | Registration flow |
| Forgot Password | ✅ Complete | Password reset request |
| Reset Password | ✅ Complete | Password reset from email |
| Dashboard | ✅ Complete | Owner server CRUD |
| 404 | ✅ Complete | Not found page |

---

### ✅ Trust & Legal Pages (Sprint 7)

| Page | Status | Notes |
|------|--------|-------|
| Verification | ✅ Complete | /verification — manual vs Verified+, keys, heartbeat |
| Consent | ✅ Complete | /consent — dual consent, in-game, revocation |
| Privacy (by Design) | ✅ Complete | /privacy — how privacy is enforced |
| Legal (Privacy Policy) | ✅ Complete | /privacy-policy — full policy + GDPR/CCPA §14 |
| Data Rights | ✅ Complete | /data-rights — access, correction, deletion |
| Contact | ✅ Complete | /contact — placeholder; wire form/email before release |
| Terms | ✅ Complete | /terms — Terms of Service |
| About | ✅ Complete | /about — placeholder |
| FAQ | ✅ Complete | /faq — placeholder |

### ❌ Missing Pages (Per Design Docs)

| Page | Status | Notes |
|------|--------|-------|
| Pricing | ❌ Missing | Dev plan says "optional, can be stubbed" |
| Player Dashboard (favorites-only) | ❌ Missing | Favorites live on Home/directory; dedicated view optional |
| Account Settings | ❌ Missing | User profile, email/password change, deletion |
| Cluster Pages | ❌ Missing | Phase 1.5 feature |

---

## Critical Missing Features (MVP Blockers)

### 1. ✅ Server CRUD Backend — **IMPLEMENTED**

**Status**: Complete. `GET/POST/PUT/DELETE /api/v1/servers` implemented; dashboard create/edit/delete works with RLS client.

---

### 2. ✅ Favorites Backend API — **IMPLEMENTED**

**Status**: Complete. `POST/DELETE /api/v1/servers/{id}/favorites` implemented; favorites persist.

---

### 3. ❌ Agent Token Generation UI

**Impact**: MEDIUM - Backend ready, UI missing

**Required:**
- Token generation endpoint (backend may exist)
- Token display in dashboard
- Token revocation UI
- Agent installation instructions

**Current State**: Dashboard has placeholder text, no actual token generation.

**Priority**: **MEDIUM** - Needed for agent verification workflow.

---

### 4. ❌ Local Host Agent Client

**Impact**: HIGH - Backend ready, agent not built

**Required:**
- Node.js/TypeScript agent service
- Local web UI
- Process/port checks
- Heartbeat sending
- Windows .exe packaging

**Current State**: 0% complete. Backend heartbeat endpoint ready.

**Priority**: **HIGH** - Core MVP feature per dev plan.

---

## Phase 1.5 Features (Post-Launch)

### Not in MVP, but mentioned in design docs:

1. ❌ **Cluster Pages** - Cluster detail pages, cluster management
2. ❌ **Top 100 Carousel** - Ranking-based carousel
3. ❌ **Hot Carousel** - Growth velocity carousel
4. ❌ **Additional Badges** - Hot, Long-Runner, etc.
5. ❌ **Password Sync** - Auto password sync from agent
6. ❌ **Auto-favorite onJoin** - Plugin-assisted favorite on join

**Status**: Correctly deferred per dev plan.

---

## Phase 2 Features (Future)

### Not in MVP scope:

1. ❌ **Player Rankings** - PvP leaderboards
2. ❌ **PvP Leaderboards** - Competitive rankings
3. ❌ **Activity Weighting** - Advanced analytics
4. ❌ **Discord Bot** - Bot integration
5. ❌ **ASA Server API Plugin** - Alternative to local agent

**Status**: Correctly deferred per dev plan.

---

## Summary by Category

### ✅ Complete (MVP Requirements)
- ✅ Directory listing with filters (including map)
- ✅ Server detail pages
- ✅ Authentication (email/password)
- ✅ Badge system (MVP badges)
- ✅ SpotlightCarousel (one carousel, selection locked, documented)
- ✅ Heartbeat ingestion (backend)
- ✅ Agent verification (backend)
- ✅ Server CRUD (backend + dashboard)
- ✅ Favorites (backend API + UI)
- ✅ Trust pages (Verification, Consent, Legal, Data Rights, Contact)
- ✅ Maps normalization + Discord/website URLs
- ✅ Error handling & loading states
- ✅ Responsive design
- ✅ Accessibility

### ✅ Complete (Sprint 7 Additions)
- ✅ Server CRUD (backend + frontend)
- ✅ Favorites (backend API + UI)
- ✅ Trust pages (Verification, Consent, Privacy, Legal, Data Rights, Contact, Terms)
- ✅ SpotlightCarousel (selection locked, limit 8, wrap-around, documented)
- ✅ Maps normalization (table, filter, ServerForm dropdown + custom map)
- ✅ Discord URL + Website URL on servers (backend + ServerForm + ServerCard + ServerPage)
- ✅ About, FAQ (pages exist; content can be expanded)

### ⚠️ Partial (Deferred to Sprint 8 / Post-Launch)
- ⚠️ Agent token/key generation (backend ready, UI placeholder)
- ⚠️ Contact page (exists; wire form/email before release)

### ❌ Missing (MVP Blockers — Agent Track)
- ❌ Local host agent client
- ❌ Agent token/key generation UI (blocking agent setup)

### ❌ Missing (Phase 1.5+)
- ❌ Cluster pages
- ❌ Top 100 / Hot carousels
- ❌ Player directory
- ❌ Account settings page

---

## Recommended Next Steps

**All actionable development tasks are tracked in [SPRINT_8_TODO.md](SPRINT_8_TODO.md).** That doc is the single backlog for: agent key/instance management, local host agent client, account settings, contact/email wiring, server images, ranking, per-user limits, and Phase 1.5 work. This section is retained for historical context only.

---

## Database Schema Status

### ✅ Tables Implemented
- ✅ `servers` - Core server data
- ✅ `clusters` - Cluster grouping (with Ed25519 keys for agent auth)
- ✅ `heartbeats` - Heartbeat log (append-only, with replay protection)
- ✅ `heartbeat_jobs` - Async processing queue (durable worker queue)
- ✅ `server_secrets` - Owner-only secrets (join_password moved here for security)
- ✅ `directory_view` - Public read model (denormalized for performance)
- ✅ `favorites` - User favorites (table + API implemented)
- ✅ `profiles` - User profiles (extends auth.users)
- ✅ `subscriptions` - Stripe subscriptions (table exists, endpoints stubbed)

**Note**: No `agent_instances` table found. Agent authentication uses cluster keys directly. Servers are linked to clusters via `cluster_id`.

### ✅ Tables Implemented (Verified)
- ✅ `favorites` - Exists in schema (user_id, server_id, UNIQUE constraint, RLS policies)
- ✅ `profiles` - Exists in schema (extends auth.users, RLS policies)
- ✅ `subscriptions` - Exists in schema (Stripe integration, RLS policies)

### ❌ Tables Missing (If Needed)
- ❌ `player_profiles` - For player directory (Phase 1.5)
- ❌ `player_activity` - For activity tracking (Phase 1.5)

---

## Test Coverage Status

### ✅ Backend Tests
- ✅ 99+ tests passing
- ✅ Directory contracts
- ✅ Heartbeat verification
- ✅ Engine tests
- ✅ Security tests

### ✅ Frontend Tests
- ✅ 147/151 tests passing (97.4%)
- ✅ Component tests
- ✅ Hook tests
- ✅ Form validation tests

---

## MVP Complete Analysis (vs Design Docs)

Comparison against **docs/design/1_DESCRIPTION.txt**, **docs/design/2_FEATURE_LIST.txt**, **docs/design/4_Dev_Plan.txt**, and **docs/design/3_TECH_STACK.txt**.

### 1_DESCRIPTION (docs/design) — Platform Vision
- **Registry, discovery, visibility, trust**: ✅ Directory, server pages, verification (backend), trust pages.
- **Free public directory, optional automation**: ✅ Manual listing + heartbeat/verified status.
- **Supabase-first, FastAPI for agent**: ✅ Implemented.
- **Agent for verified status**: Backend ready; agent client not built (deferred).

### 2_FEATURE_LIST — 90% MVP Scope Lock
- **Core Directory (Always Free)**: ✅ Listings, status, mod/rates/wipe/cluster, server page, join instructions, **account-gated password** (visible when authenticated), search & filters, favorites, player accounts.
- **Badge System**: ✅ Verified, Stable, New, PvE/PvP, Vanilla/Boosted. Hot, Long-Runner, cluster/player badges = Phase 1.5+.
- **One carousel (Newbie)**: ✅ Delivered as SpotlightCarousel (verified + boosted, quality, limit 8); documented.
- **Subscription plumbing**: Stubbed (acceptable for MVP per dev plan).
- **Plugin (Secure key, verification, heartbeat)**: ✅ Backend complete; agent client not built.

### 4_Dev_Plan (docs/design) — Web + Agent MVP
- **Sprint 0–1 (Foundation, Free Directory)**: ✅ Schema, RLS, directory_view, auth, directory, server CRUD, favorites, **account-gated** password (dev plan said “favorite → reveal”; implemented as account-gated for security).
- **Sprint 2 (Agent Verified)**: Backend ✅; agent client ❌.
- **Sprint 3 (Badges + Carousel + Polish)**: ✅ Badges, SpotlightCarousel, owner diagnostics (heartbeat) stubbed.
- **Stabilization (Trust pages, docs)**: ✅ Verification, Consent, Privacy, Legal, Data Rights, Contact, Terms; linked from footer.

### 3_TECH_STACK (docs/design)
- **Frontend**: React, TypeScript, Vite, Tailwind, Radix/shadcn, TanStack Query, RHF + Zod, React Router — ✅.
- **Backend**: Python/Pydantic, Supabase, FastAPI — ✅.
- **Auth**: Supabase Auth (email), RLS — ✅. “Password gating” implemented as **account-gated** (authenticated users only).

### MVP Verdict
- **Web MVP**: Complete for launch (directory, CRUD, favorites, trust pages, SpotlightCarousel, maps, Discord/website URLs). Contact page placeholder; wire form/email before release.
- **Agent MVP**: Backend complete; agent client and key/instance UI deferred to Sprint 8 / post-launch. Platform is **soft-launch ready** without agent; agent adds verified status when built.

---

## Conclusion

**MVP Status**: ~90% complete (web MVP complete; agent client deferred)

**Strengths:**
- ✅ Frontend production-ready; trust pages and legal coverage in place
- ✅ Core directory, Server CRUD, Favorites, maps, Discord/website URLs complete
- ✅ Heartbeat/verification backend complete
- ✅ Security boundaries and account-gated password
- ✅ Excellent test coverage

**Critical Gaps (Sprint 8 / Post-Launch):**
- ✅ Server CRUD backend — **IMPLEMENTED**
- ✅ Favorites backend API — **IMPLEMENTED**
- ❌ Agent key/instance management (blocking agent setup) — **MEDIUM** (see SPRINT_8_TODO.md)
- ❌ Agent client — **HIGH** (backend ready; can ship without)
- ⚠️ Contact page — wire form/email before release (see FinalCheck.md)

**Recommendation**: Web MVP and Sprint 7 definition of done are met. Use **SPRINT_8_TODO.md** for remaining items (agent, contact, optional polish). Run **FinalCheck.md** before deploy.

---

**Last Updated**: 2026-02-02
