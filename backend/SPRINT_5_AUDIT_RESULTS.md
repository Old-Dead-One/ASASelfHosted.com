# Sprint 5 Audit Results - Task 5.1.1

**Date:** 2026-01-23  
**Task:** 5.1.1 - Audit Directory Endpoints & Pagination Determinism

## Findings

### ✅ Read-Only Verification
- **Status:** PASS
- `/directory/servers` - Read-only (no mutations)
- `/directory/servers/{id}` - Read-only (no mutations)
- `/directory/filters` - Read-only (no mutations)

### ✅ No Direct Supabase Calls
- **Status:** PASS
- No `.table()` calls found in `backend/app/api/v1/`
- No `get_supabase_admin()` calls found in routes
- All data access goes through repositories ✅

### ⚠️ Pagination Determinism Issues
- **Status:** FAIL - Needs Migration
- **Current:** Page-based pagination (`page`, `page_size`)
- **Problem:** Not deterministic under write churn (new/updated servers shift pages)
- **Action Required:** Migrate to cursor pagination (Task 5.1.2)

### ✅ Tie-Break Ordering
- **Status:** PARTIAL
- **Current:** `ORDER BY updated_at, id` (id as tie-breaker) ✅
- **Issue:** Ordering is hardcoded to `updated_at` regardless of `rank_by` parameter
- **Action Required:** Support all sort keys with tie-break (Task 5.1.2)

### ✅ Directory View Fields
- **Status:** PASS
- `directory_view` includes:
  - `id` (for tie-break) ✅
  - `updated_at` (for sorting) ✅
  - All sort keys available: `updated_at`, `players_current`, `quality_score`, `uptime_percent` ✅
  - `last_seen_at` is available (for `seconds_since_seen`) ✅
- No per-row joins needed ✅

### ⚠️ Sort Key Support
- **Status:** PARTIAL
- **Current:** Only `updated_at` is used for sorting (hardcoded)
- **Required Sort Keys:**
  - `updated` ✅ (available as `updated_at`)
  - `players` ✅ (available as `players_current`)
  - `quality` ✅ (available as `quality_score`)
  - `uptime` ✅ (available as `uptime_percent`)
- **Action Required:** Implement dynamic sort key selection based on `rank_by` parameter

### ⚠️ NULL Handling
- **Status:** NOT DEFINED
- **Current:** PostgREST default behavior (NULLS LAST for DESC)
- **Action Required:** Explicitly define NULL handling for each sort key (Task 5.1.2)

## Recommendations

1. **Immediate:** Migrate to cursor pagination (Task 5.1.2)
2. **Immediate:** Support all sort keys dynamically (not just `updated_at`)
3. **Immediate:** Define NULL handling explicitly
4. **Immediate:** Add `seconds_since_seen` computation (using `last_seen_at` from view)

## Next Steps

- [x] Complete audit
- [ ] Start Task 5.1.2: Migrate to cursor pagination
- [ ] Start Task 5.4.2: Audit routes (already done - no issues found)
