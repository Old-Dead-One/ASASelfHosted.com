# Gap Analysis: Design Docs vs Current Implementation

**Date**: 2026-01-26  
**Status**: Post-Sprint 6 Review

---

## Executive Summary

**MVP Completion**: ~75%  
**Frontend**: ~95% complete (Sprint 6 done)  
**Backend**: ~70% complete (core APIs done, CRUD stubbed)  
**Agent**: 0% (not started)  
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
| Password field | ⚠️ Partial | Moved to `server_secrets` (owner-only), no public password gating |
| Search & filters | ✅ Complete | Full filter panel implemented |
| Favorites (players) | ⚠️ Frontend only | UI exists, backend API missing |
| Player accounts | ✅ Complete | Auth system in place |

**Missing:**
- ❌ Favorites backend API (`POST /api/v1/servers/{id}/favorites`, `DELETE /api/v1/servers/{id}/favorites`)
- ⚠️ Password gating (favorite → reveal) - needs clarification on requirements

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
| Favorited servers | ⚠️ Partial | UI exists, backend missing |
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
| Newbie Servers | ✅ Complete | Implemented in Sprint 6 |

**Status**: MVP requirement (Newbie carousel) complete. Others are Phase 1.5+.

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

---

### ⚠️ Stubbed Endpoints (Not Implemented)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /api/v1/servers` | ❌ Stubbed | Returns empty array |
| `GET /api/v1/servers/{id}` | ❌ Stubbed | Returns 404 |
| `POST /api/v1/servers` | ❌ Stubbed | Returns "not yet implemented" |
| `PUT /api/v1/servers/{id}` | ❌ Stubbed | Returns "not yet implemented" |
| `DELETE /api/v1/servers/{id}` | ⚠️ Partial | Returns success but doesn't delete |
| `GET /api/v1/clusters` | ❌ Stubbed | Returns empty array |
| `GET /api/v1/clusters/{id}` | ❌ Stubbed | Returns 404 |
| `POST /api/v1/clusters` | ❌ Stubbed | Returns "not yet implemented" |
| `POST /api/v1/verification/initiate` | ❌ Stubbed | Not implemented |
| `POST /api/v1/verification/verify` | ❌ Stubbed | Not implemented |
| `GET /api/v1/verification/status/{id}` | ❌ Stubbed | Not implemented |
| `GET /api/v1/subscriptions` | ❌ Stubbed | Not implemented |
| `POST /api/v1/subscriptions/create-checkout` | ❌ Stubbed | Not implemented |
| `POST /api/v1/subscriptions/cancel` | ❌ Stubbed | Not implemented |
| `POST /api/v1/webhooks/stripe` | ❌ Stubbed | Not implemented |
| `POST /api/v1/servers/{id}/favorites` | ❌ Missing | Favorites API not created |
| `DELETE /api/v1/servers/{id}/favorites` | ❌ Missing | Favorites API not created |

---

## Frontend Pages Status

### ✅ Implemented Pages

| Page | Status | Notes |
|------|--------|-------|
| Home | ✅ Complete | Newbie carousel + directory |
| Directory | ✅ Complete | Integrated into HomePage |
| Server details | ✅ Complete | ServerPage with all features |
| Login | ✅ Complete | Email/password auth |
| Sign Up | ✅ Complete | Registration flow |
| Forgot Password | ✅ Complete | Password reset request |
| Reset Password | ✅ Complete | Password reset from email |
| Dashboard | ✅ Complete | Owner server CRUD |
| 404 | ✅ Complete | Not found page |

---

### ❌ Missing Pages (Per Design Docs)

| Page | Status | Notes |
|------|--------|-------|
| About | ❌ Missing | Not in MVP, but mentioned in dev plan |
| Pricing | ❌ Missing | Dev plan says "optional, can be stubbed" |
| FAQ | ❌ Missing | Not in MVP |
| Terms | ❌ Missing | Not in MVP |
| Privacy | ❌ Missing | Not in MVP |
| Player Dashboard | ❌ Missing | Favorites view (not in MVP) |
| Account Settings | ❌ Missing | User profile/settings page |
| Cluster Pages | ❌ Missing | Phase 1.5 feature |

---

## Critical Missing Features (MVP Blockers)

### 1. ❌ Server CRUD Backend Implementation

**Impact**: HIGH - Frontend ready, backend stubbed

**Required:**
- `POST /api/v1/servers` - Create server
- `PUT /api/v1/servers/{id}` - Update server
- `DELETE /api/v1/servers/{id}` - Delete server
- `GET /api/v1/servers` - List owner's servers (different from directory)

**Current State**: All endpoints return "not yet implemented" errors.

**Priority**: **CRITICAL** - Dashboard is unusable without this.

---

### 2. ❌ Favorites Backend API

**Impact**: MEDIUM - UI exists, backend missing

**Required:**
- `POST /api/v1/servers/{id}/favorites` - Add favorite
- `DELETE /api/v1/servers/{id}/favorites` - Remove favorite
- `GET /api/v1/servers/{id}/favorites` - Check favorite status (optional)

**Current State**: Frontend has optimistic updates, but no persistence.

**Priority**: **HIGH** - Core MVP feature per feature list.

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
- ✅ Directory listing with filters
- ✅ Server detail pages
- ✅ Authentication (email/password)
- ✅ Badge system (MVP badges)
- ✅ Newbie carousel
- ✅ Heartbeat ingestion (backend)
- ✅ Agent verification (backend)
- ✅ Error handling & loading states
- ✅ Responsive design
- ✅ Accessibility

### ⚠️ Partial (Needs Backend)
- ⚠️ Server CRUD (frontend ready, backend stubbed)
- ⚠️ Favorites (UI ready, backend missing)
- ⚠️ Agent token generation (UI placeholder, backend may exist)

### ❌ Missing (MVP Blockers)
- ❌ Server CRUD backend implementation
- ❌ Favorites backend API
- ❌ Local host agent client
- ❌ Agent token generation UI

### ❌ Missing (Phase 1.5+)
- ❌ Cluster pages
- ❌ Top 100 / Hot carousels
- ❌ Player directory
- ❌ Account settings page
- ❌ About/FAQ/Terms/Privacy pages

---

## Recommended Next Steps

### Priority 1: MVP Completion (Critical)

1. **Implement Server CRUD Backend** (2-3 days)
   - `POST /api/v1/servers` - Create
   - `PUT /api/v1/servers/{id}` - Update
   - `DELETE /api/v1/servers/{id}` - Delete
   - `GET /api/v1/servers` - List owner's servers (different from directory)
   - Wire to Supabase `servers` table
   - Add ownership checks (RLS already in place)
   - Handle `hosting_provider` validation (must be 'self_hosted')

2. **Implement Favorites Backend** (1-2 days)
   - `POST /api/v1/servers/{id}/favorites` - Add favorite
   - `DELETE /api/v1/servers/{id}/favorites` - Remove favorite
   - `GET /api/v1/servers/{id}/favorites` - Check favorite status (optional)
   - Wire to `favorites` table (exists in schema)
   - RLS policies already in place
   - Update `directory_view` favorite counts (already computed)

3. **Agent Token/Key Generation** (2-3 days)
   - **Backend**: Cluster key pair generation endpoint
     - `POST /api/v1/clusters/{id}/generate-keys` - Generate Ed25519 key pair
     - Store `public_key_ed25519` in clusters table
     - Return private key to owner (one-time display)
   - **Backend**: Agent instance management
     - `POST /api/v1/clusters/{id}/instances` - Create agent instance
     - `GET /api/v1/clusters/{id}/instances` - List instances
     - Link instances to servers
   - **Frontend**: Dashboard UI
     - Token/key generation UI
     - Key display (one-time)
     - Instance management
     - Agent setup instructions
   - **Note**: Agent authentication uses cluster keys, not tokens. Need to clarify token vs key model.

### Priority 2: Agent Client (High)

4. **Build Local Host Agent** (1-2 weeks)
   - Node.js/TypeScript agent service
   - Local web UI
   - Process/port checks
   - Heartbeat sending
   - Windows packaging

### Priority 3: Polish (Medium)

5. **Additional Pages** (1-2 days)
   - About page
   - FAQ page
   - Terms/Privacy (can be stubbed)

6. **Account Settings** (2-3 days)
   - User profile page
   - Email change
   - Password change
   - Account deletion

---

## Database Schema Status

### ✅ Tables Implemented
- ✅ `servers` - Core server data
- ✅ `clusters` - Cluster grouping (with Ed25519 keys for agent auth)
- ✅ `heartbeats` - Heartbeat log (append-only, with replay protection)
- ✅ `heartbeat_jobs` - Async processing queue (durable worker queue)
- ✅ `server_secrets` - Owner-only secrets (join_password moved here for security)
- ✅ `directory_view` - Public read model (denormalized for performance)
- ✅ `favorites` - User favorites (table exists, API missing)
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

## Conclusion

**MVP Status**: ~75% complete

**Strengths:**
- ✅ Frontend is production-ready
- ✅ Core directory functionality complete
- ✅ Heartbeat/verification backend complete
- ✅ Security boundaries in place
- ✅ Excellent test coverage

**Critical Gaps:**
- ❌ Server CRUD backend (blocking dashboard) - **HIGHEST PRIORITY**
- ❌ Favorites backend API (blocking favorites feature) - **HIGH PRIORITY**
- ❌ Agent key/instance management (blocking agent setup) - **MEDIUM PRIORITY**
- ❌ Agent client (blocking verification workflow) - **HIGH PRIORITY** (but can be parallel)

**Recommendation**: Focus on Priority 1 items to complete MVP. Agent client can be built in parallel or after MVP launch.

---

**Last Updated**: 2026-01-26
