# Sprint 1 Completion Checklist

## Phase 0 — Baseline snapshot
- [x] **Status**: Implicitly completed (we've been working on the codebase)
- [x] Backend and frontend run
- [x] Health endpoints work
- [x] CORS behavior documented
- [x] Auth behavior documented
- [x] ENV usage documented

## Phase 1 — Settings become trustworthy

### 1.1 Convert settings to stable access pattern
- [x] **Status**: ✅ COMPLETE
- [x] `get_settings()` with `@lru_cache` implemented
- [x] All imports updated to use `get_settings()`
- [x] Backward compatibility maintained with global `settings` variable
- **File**: `backend/app/core/config.py`

### 1.2 Fix auth model shape
- [x] **Status**: ✅ COMPLETE
- [x] `SUPABASE_JWT_SECRET` removed
- [x] `SUPABASE_JWT_ISSUER` added
- [x] `SUPABASE_JWKS_URL` added
- [x] `SUPABASE_JWT_AUDIENCE = "authenticated"` added
- [x] All optional/empty for now
- **File**: `backend/app/core/config.py`

### 1.3 Hard-wall local auth bypass
- [x] **Status**: ✅ COMPLETE
- [x] `validate_non_local()` enforces: `AUTH_BYPASS_LOCAL` only allowed when `ENV == "local"`
- [x] Raises `ValueError` if bypass enabled in non-local env
- **File**: `backend/app/core/config.py` (line 63-75)

### 1.4 Startup config banner
- [x] **Status**: ✅ COMPLETE
- [x] Logs ENV
- [x] Logs "AUTH MODE: BYPASS" vs "AUTH MODE: REAL"
- [x] Logs directory view name
- [x] Logs CORS origins (count + list)
- **File**: `backend/app/main.py` (lines 30-43)

## Phase 2 — Define auth contract

### 2.1 Create single "request user" model
- [x] **Status**: ✅ COMPLETE
- [x] `UserIdentity` class created with:
  - `user_id` (maps to `sub`)
  - `email: str | None`
  - `role: str` (from claims)
  - `claims: dict` (raw claims)
- [x] `get_current_user()` dependency (alias: `require_user`)
- [x] `get_optional_user()` dependency
- **Files**: `backend/app/core/security.py`, `backend/app/core/deps.py`

### 2.2 Implement token extraction
- [x] **Status**: ✅ COMPLETE
- [x] Parses `Authorization: Bearer <token>`
- [x] `get_optional_user()` → `None` if missing
- [x] `require_user()` → 401 if missing
- [x] Malformed token → 401
- **File**: `backend/app/core/deps.py`

### 2.3 Implement local bypass behavior
- [x] **Status**: ✅ COMPLETE
- [x] `create_local_bypass_user()` function
- [x] Returns stable fake user: `sub="local-dev"`
- [x] `X-Dev-User` header support for override
- [x] Only works when `ENV == "local"` and `AUTH_BYPASS_LOCAL == True`
- **File**: `backend/app/core/security.py`

## Phase 3 — Implement "real auth" path (JWKS verification)

### 3.1 JWKS fetch + cache
- [x] **Status**: ✅ COMPLETE
- [x] `_fetch_jwks()` implemented with httpx
- [x] `_get_jwks_keys()` with in-memory TTL cache (1 hour)
- [x] Response shape validation
- [x] Error handling for request/HTTP errors
- [x] Missing JWKS in local mode doesn't crash
- **File**: `backend/app/core/security.py`

### 3.2 Verify JWT signature + issuer + audience
- [x] **Status**: ✅ COMPLETE
- [x] Signature verification via JWKS (RS256)
- [x] Issuer verification (`iss` matches `SUPABASE_JWT_ISSUER`)
- [x] Expiration check (`exp` not expired)
- [x] Audience verification (handles both string and list forms)
- [x] All validation done via `jwt.decode()` parameters
- **File**: `backend/app/core/security.py`

### 3.3 Normalize errors and logging
- [x] **Status**: ✅ COMPLETE
- [x] 401 for missing/invalid auth (`UnauthorizedError`)
- [x] 403 for valid auth but forbidden (`ForbiddenError`)
- [x] No raw tokens logged
- [x] Consistent error format with `request_id`
- **File**: `backend/app/core/errors.py`

## Phase 4 — Lock Directory Read Contract

### 4.1 Create dedicated directory router
- [x] **Status**: ✅ COMPLETE
- [x] `GET /api/v1/directory/servers` endpoint
- [x] `GET /api/v1/directory/servers/{id}` endpoint
- [x] Uses `get_optional_user()` (public, no forced auth)
- [x] Returns `DirectoryResponse` with pagination
- **File**: `backend/app/api/v1/directory.py`

### 4.2 Add repository layer
- [x] **Status**: ✅ COMPLETE
- [x] `DirectoryRepository` abstract interface
- [x] `MockDirectoryRepository` implementation
- [x] `list_servers()` with pagination and filters
- [x] `get_server(id)` function
- [x] Routes call repo functions, not inline SQL
- **Files**: `backend/app/db/directory_repo.py`, `backend/app/db/mock_directory_repo.py`

### 4.3 Bind "directory_view" name as constant
- [x] **Status**: ✅ COMPLETE
- [x] `DIRECTORY_VIEW_NAME = "directory_view"` in config
- [x] Configurable for future migrations
- **File**: `backend/app/core/config.py`

## Phase 5 — Frontend handshake

### 5.1 Standardize API client behavior
- [x] **Status**: ✅ COMPLETE
- [x] Single fetch client (`apiRequest()`)
- [x] Attaches JWT if present
- [x] 401 → treated as logged out
- [x] 403 → shows "not allowed"
- [x] No business logic in UI beyond status codes
- **File**: `frontend/src/lib/api.ts`

### 5.2 Add dev auth toggle
- [x] **Status**: ✅ COMPLETE
- [x] `dev-auth.ts` utilities
- [x] `enableDevAuth()` / `disableDevAuth()` functions
- [x] Sends `X-Dev-User` header when enabled
- [x] Only works in dev mode
- **Files**: `frontend/src/lib/dev-auth.ts`, `frontend/src/lib/api.ts`

## Phase 6 — Guardrails for future

### 6.1 Make validation automatic in non-local envs
- [x] **Status**: ✅ COMPLETE
- [x] `validate_non_local()` method
- [x] Enforces when `ENV in ("staging", "production")`:
  - CORS not empty
  - Supabase URL + anon key present
  - Issuer + JWKS URL present
  - `AUTH_BYPASS_LOCAL` must be false
- [x] Called automatically in `create_app()`
- **Files**: `backend/app/core/config.py`, `backend/app/main.py`

## Phase 7 — Smoke tests

### 7.1 Add smoke tests for auth contract
- [x] **Status**: ✅ COMPLETE
- [x] `test_directory_servers_public()` - GET /directory/servers returns 200
- [x] `test_directory_server_public()` - GET /directory/servers/{id} works
- [x] `test_protected_endpoint_without_auth()` - Protected endpoint returns 401
- [x] `test_health_endpoint()` - Health endpoints are public
- **File**: `backend/tests/test_auth_contract.py`

## Additional Improvements (Beyond Playbook)

### Code Quality
- [x] Removed duplicate validation logic
- [x] Consistent error handling with `request_id`
- [x] Type safety: filter parameters use `Literal` types
- [x] Repository pattern with explicit dependency injection
- [x] Mock data matches `DirectoryServer` schema exactly
- [x] Realistic join addresses in mock data
- [x] Optimized provider to reuse single mock repo instance

### Architecture
- [x] Clean separation: read model (`/directory`) vs write model (`/servers`)
- [x] Explicit import paths (`app.db.providers` not `app.db`)
- [x] Consistent naming: `NotFoundError("Server", id)` with Title Case

## Summary

**All 7 phases complete! ✅**

- **Phase 0**: Baseline established
- **Phase 1**: Settings trustworthy ✅
- **Phase 2**: Auth contract defined ✅
- **Phase 3**: JWKS verification implemented ✅
- **Phase 4**: Directory read contract locked ✅
- **Phase 5**: Frontend handshake complete ✅
- **Phase 6**: Production guardrails in place ✅
- **Phase 7**: Smoke tests added ✅

**Sprint 1 is complete and ready for Sprint 2!**
