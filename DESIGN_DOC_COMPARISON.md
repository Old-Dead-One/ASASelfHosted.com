# Design Document Comparison

**Date:** After Sprint 4 Completion  
**Purpose:** Compare current project state against original design documents

## Root Level Files

### Design Docs (Expected)
- `1_DESCRIPTION.txt` ✅ Present
- `2_FEATURE_LIST.txt` ✅ Present
- `3_TECH_STACK.txt` ✅ Present
- `4_Dev_Plan.txt` ✅ Present

### Documentation Files (Current)
- `DECISIONS.md` ✅ Present (Official decisions override design docs)
- `DEV_NOTES.md` ✅ Present
- `GIT_SETUP.md` ✅ Present
- `INSTALL.md` ✅ Present
- `PROJECT_STRUCTURE.md` ✅ Present (Updated after Sprint 2)
- `README.md` ✅ Present
- `VERIFICATION.md` ✅ Present

### Sprint Documentation (New)
- `SPRINT_1_COMPLETION_CHECKLIST.md` ✅ Present
- `SPRINT_ONE_PLAYBOOK.txt` ✅ Present
- `SPRINT_TWO_PLAYBOOK.md` ✅ Present

**Total Root Files:** 14 files (matches expected + sprint docs)

## Backend Structure Comparison

### API Endpoints (api/v1/)

**Design Docs Expected:**
- `router.py` ✅
- `servers.py` ✅
- `clusters.py` ✅
- `verification.py` ✅
- `heartbeat.py` ✅
- `consent.py` ✅
- `subscriptions.py` ✅
- `webhooks.py` ✅

**Sprint 1+ Additions:**
- `directory.py` ✅ **NEW** (Public directory read endpoints)

**Sprint 4 Additions:**
- `heartbeat.py` ✅ **UPDATED** (Agent heartbeat with Ed25519 signature verification)

**Status:** All expected + 1 new (directory API), 1 updated (heartbeat with crypto auth)

### Core Module

**Design Docs Expected:**
- `config.py` ✅
- `errors.py` ✅
- `supabase.py` ✅

**Sprint 1+ Additions:**
- `deps.py` ✅ **NEW** (FastAPI dependencies, auth)
- `security.py` ✅ **NEW** (JWT verification, JWKS)

**Sprint 4 Additions:**
- `crypto.py` ✅ **NEW** (Ed25519 signature verification, canonical envelope)
- `heartbeat.py` ✅ **NEW** (Grace window utilities)

**Status:** All expected + 4 new (auth infrastructure + agent crypto)

### Middleware

**Design Docs Expected:**
- `auth.py` ✅
- `consent.py` ✅

**Sprint 1+ Additions:**
- `rate_limit.py` ✅ **NEW** (Rate limiting)
- `request_id.py` ✅ **NEW** (Request correlation)

**Status:** All expected + 2 new (middleware enhancements)

### Schemas

**Design Docs Expected:**
- `base.py` ✅
- `servers.py` ✅
- `clusters.py` ✅
- `verification.py` ✅
- `heartbeat.py` ✅
- `consent.py` ✅
- `subscriptions.py` ✅

**Sprint 1+ Additions:**
- `directory.py` ✅ **NEW** (Directory schemas with filters, ranking)

**Sprint 4 Additions:**
- `heartbeat.py` ✅ **UPDATED** (HeartbeatRequest/Response with Ed25519 fields)

**Status:** All expected + 1 new (directory schemas), 1 updated (heartbeat schemas)

### Database Layer (db/)

**Design Docs Expected:**
- `queries.py` ✅
- `migrations/` ✅

**Sprint 1+ Additions:**
- `directory_repo.py` ✅ **NEW** (Repository interface)
- `mock_directory_repo.py` ✅ **NEW** (Mock implementation)
- `supabase_directory_repo.py` ✅ **NEW** (Supabase implementation - Sprint 3)
- `providers.py` ✅ **NEW** (Dependency injection)

**Sprint 4 Additions:**
- `heartbeat_repo.py` ✅ **NEW** (Heartbeat persistence interface)
- `heartbeat_jobs_repo.py` ✅ **NEW** (Durable queue interface)
- `servers_derived_repo.py` ✅ **NEW** (Derived state repository interface)
- `supabase_heartbeat_repo.py` ✅ **NEW** (Heartbeat persistence implementation)
- `supabase_heartbeat_jobs_repo.py` ✅ **NEW** (Durable queue implementation)
- `supabase_servers_derived_repo.py` ✅ **NEW** (Derived state implementation)

**Status:** All expected + 10 new (repository pattern + Sprint 4 heartbeat repos)

### Engines & Workers (Sprint 4)

**Sprint 4 Additions:**
- `engines/` ✅ **NEW** (Derived state computation engines)
  - `status_engine.py` (effective status)
  - `confidence_engine.py` (RYG confidence)
  - `uptime_engine.py` (uptime percentage)
  - `quality_engine.py` (quality score)
- `workers/` ✅ **NEW** (Background workers)
  - `heartbeat_worker.py` (durable worker for heartbeat processing)

**Status:** New engines and worker infrastructure

### Tests

**Sprint 1+ Additions:**
- `tests/test_auth_contract.py` ✅ **NEW** (Smoke tests)

**Sprint 4 Additions:**
- `tests/test_crypto.py` ✅ **NEW** (Ed25519 crypto tests)
- `tests/test_heartbeat_endpoint.py` ✅ **NEW** (Heartbeat endpoint tests)
- `tests/test_status_engine.py` ✅ **NEW** (Status engine tests)
- `tests/test_confidence_engine.py` ✅ **NEW** (Confidence engine tests)
- `tests/test_uptime_engine.py` ✅ **NEW** (Uptime engine tests)
- `tests/test_quality_engine.py` ✅ **NEW** (Quality engine tests)

**Status:** Comprehensive test suite (26 tests passing)

## Frontend Structure Comparison

### Components

**Design Docs Expected:**
- `ui/` ✅ (shadcn/ui components)
- `servers/` ✅ (ServerCard, ServerList)
- `layout/` ✅ (Header, Footer, Layout)

**Removed (Consolidated):**
- `badges/Badge.tsx` ❌ **REMOVED** (Consolidated into `ui/Badge.tsx`)
- `verification/VerificationBadge.tsx` ❌ **REMOVED** (Functionality in Badge)

**Status:** Cleaner structure, consolidated components

### Library Files

**Design Docs Expected:**
- `api.ts` ✅
- `query-client.ts` ✅
- `utils.ts` ✅

**Sprint 1+ Additions:**
- `dev-auth.ts` ✅ **NEW** (Dev auth bypass)
- `tokens.md` ✅ **NEW** (Documentation)

**Status:** All expected + 2 new (dev tools)

### Types

**Design Docs Expected:**
- `types/index.ts` ✅

**Status:** Present and fully aligned with backend (Sprint 2)

## Alignment with Design Documents

### ✅ Aligned Areas

1. **Tech Stack** - Matches `3_TECH_STACK.txt` exactly
2. **Feature Scope** - Aligned with `2_FEATURE_LIST.txt` MVP scope
3. **Architecture** - Follows `4_Dev_Plan.txt` principles
4. **File Structure** - Matches expected structure + Sprint additions

### 📝 Changes from Design Docs

1. **Repository Pattern** - Added abstraction layer (not in original design, but aligns with best practices)
2. **Directory API** - Separate read-only endpoint (cleaner separation than original)
3. **Component Consolidation** - Badge components consolidated (cleaner structure)
4. **Sprint Documentation** - Added playbooks and checklists (project management)
5. **Agent Authentication** - Used Ed25519 (cluster-based) instead of HMAC (agent token-based)
   - **Rationale:** Aligns with cluster key model in `2_FEATURE_LIST.txt` (lines 95-97)
   - **Benefit:** More secure, supports cluster identity, better for key rotation
   - **Note:** Dev Plan mentions HMAC with agent token, but cluster Ed25519 is the correct long-term approach

### 🎯 Design Doc Compliance

**All design documents are respected:**
- `DECISIONS.md` explicitly states which decisions override design docs
- Sprint work aligns with `4_Dev_Plan.txt` sequencing
- MVP scope from `2_FEATURE_LIST.txt` is maintained
- Tech stack from `3_TECH_STACK.txt` is unchanged

## File Count Summary

**Root Level:** 14 files (4 design docs + 7 documentation + 3 sprint docs)

**Backend:**
- API endpoints: 9 files (8 expected + 1 new)
- Core: 7 files (3 expected + 4 new: deps, security, crypto, heartbeat)
- Middleware: 4 files (2 expected + 2 new)
- Schemas: 8 files (7 expected + 1 new)
- DB layer: 12 files (2 expected + 10 new: directory repos + Sprint 4 heartbeat repos)
- Engines: 4 files (new in Sprint 4)
- Workers: 1 file (new in Sprint 4)
- Tests: 7 files (1 new in Sprint 1, 6 new in Sprint 4)

**Frontend:**
- Components: Consolidated (removed 2, added to ui/)
- Library: 5 files (3 expected + 2 new)
- Types: 1 file (aligned with backend)

## Conclusion

✅ **Project structure is aligned with design documents**  
✅ **Sprint additions are documented and justified**  
✅ **No breaking changes to design doc expectations**  
✅ **File count is reasonable and organized**  
✅ **Empty directories removed**  
✅ **PROJECT_STRUCTURE.md updated to reflect current state**

### Design Doc Alignment Summary

**Sprint 4 Implementation vs Design Docs:**
- ✅ **Agent heartbeat endpoint** - Implemented (matches `4_Dev_Plan.txt` line 105-117)
- ✅ **Signature verification** - Implemented with Ed25519 (better than HMAC in Dev Plan)
- ✅ **Replay protection** - Implemented via `UNIQUE(server_id, heartbeat_id)`
- ✅ **Status computation** - Implemented (matches RYG logic in `4_Dev_Plan.txt` lines 63-67)
- ✅ **Cluster key model** - Implemented (aligns with `2_FEATURE_LIST.txt` lines 95-97)
- ✅ **Derived metrics** - Implemented (uptime, quality, confidence)
- ✅ **Durable worker** - Implemented (matches "background jobs" in `3_TECH_STACK.txt`)

**Improvements over Design Docs:**
- Ed25519 instead of HMAC (more secure, supports cluster identity)
- Row-level job claiming (multi-worker safety)
- Explicit field whitelist in crypto (schema freeze protection)
- Python-based engines (no SQL triggers, explicit logic)

**Ready for Sprint 5!**
