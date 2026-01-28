# Security Fixes Migration - Test Guide

This guide helps verify that the security fixes in `012_security_fixes.sql` are working correctly.

## Prerequisites

- Supabase project with all previous migrations applied
- Supabase Dashboard access
- Anon key and Service Role key from Supabase Settings → API

## Test 1: join_password is not accessible via anon key

### Expected Result: ❌ FAIL (should fail - column doesn't exist or access denied)

```sql
-- Using anon key, try to read join_password from servers table
-- This should FAIL (column doesn't exist after migration)
SELECT join_password FROM servers LIMIT 1;
```

**Expected Error:**
- Column `join_password` does not exist (if column was dropped)
- OR: Permission denied (if RLS blocks access)

### Expected Result: ✅ PASS (should work - owner can access)

```sql
-- Using owner JWT token, try to read from server_secrets
-- This should WORK (owner can read their own secrets)
SELECT * FROM server_secrets WHERE server_id = '<your-server-id>';
```

**Expected Result:** Returns join_password for servers owned by the authenticated user.

## Test 2: heartbeat payload/signature is not accessible via anon key

### Expected Result: ❌ FAIL (should fail - access denied)

```sql
-- Using anon key, try to read payload and signature from heartbeats table
-- This should FAIL (access denied)
SELECT payload, signature FROM heartbeats LIMIT 1;
```

**Expected Error:** Permission denied (RLS blocks access)

### Expected Result: ✅ PASS (should work - public view available)

```sql
-- Using anon key, try to read from heartbeats_public view
-- This should WORK (public can read sanitized view)
SELECT * FROM heartbeats_public 
WHERE received_at > NOW() - INTERVAL '24 hours' 
LIMIT 1;
```

**Expected Result:** Returns heartbeat data WITHOUT `payload` and `signature` columns.

### Expected Result: ✅ PASS (should work - service-role can access)

```sql
-- Using service-role key, try to read from heartbeats table
-- This should WORK (service-role bypasses RLS)
SELECT payload, signature FROM heartbeats LIMIT 1;
```

**Expected Result:** Returns heartbeat data INCLUDING `payload` and `signature` columns.

## Test 3: directory_view is still publicly accessible

### Expected Result: ✅ PASS (should work)

```sql
-- Using anon key, try to read from directory_view
-- This should WORK (public can read directory)
SELECT id, name, join_address FROM directory_view LIMIT 1;
```

**Expected Result:** Returns server data (without join_password).

## Test 4: servers table is not directly accessible via anon key

### Expected Result: ❌ FAIL (should fail - access denied)

```sql
-- Using anon key, try to read directly from servers table
-- This should FAIL (access denied)
SELECT * FROM servers LIMIT 1;
```

**Expected Error:** Permission denied (RLS blocks access)

## Test 5: Owners can still manage their servers

### Expected Result: ✅ PASS (should work)

```sql
-- Using owner JWT token, try to read own servers
-- This should WORK (owners can read their own servers)
SELECT * FROM servers WHERE owner_user_id = auth.uid() LIMIT 1;
```

**Expected Result:** Returns server data for servers owned by the authenticated user.

## Quick Verification Script

Run these in Supabase SQL Editor with different keys:

### With Anon Key:
```sql
-- Should FAIL
SELECT join_password FROM servers LIMIT 1;

-- Should FAIL  
SELECT payload, signature FROM heartbeats LIMIT 1;

-- Should FAIL
SELECT * FROM servers LIMIT 1;

-- Should PASS
SELECT * FROM directory_view LIMIT 1;

-- Should PASS (but no payload/signature columns)
SELECT * FROM heartbeats_public 
WHERE received_at > NOW() - INTERVAL '24 hours' 
LIMIT 1;
```

### With Service Role Key:
```sql
-- Should PASS (service-role bypasses RLS)
SELECT * FROM servers LIMIT 1;
SELECT payload, signature FROM heartbeats LIMIT 1;
SELECT * FROM server_secrets LIMIT 1;
```

### With Owner JWT:
```sql
-- Should PASS (owner can read own servers)
SELECT * FROM servers WHERE owner_user_id = auth.uid() LIMIT 1;

-- Should PASS (owner can read own secrets)
SELECT * FROM server_secrets 
WHERE EXISTS (
    SELECT 1 FROM servers 
    WHERE servers.id = server_secrets.server_id 
    AND servers.owner_user_id = auth.uid()
) LIMIT 1;
```

## Success Criteria

✅ **Security Fix 1 (join_password):**
- Anon key cannot read `join_password` from `servers` table
- Anon key cannot read from `servers` table directly
- Owners can read `join_password` from `server_secrets` table
- `directory_view` is still publicly accessible (without join_password)

✅ **Security Fix 2 (heartbeat payload/signature):**
- Anon key cannot read `payload` or `signature` from `heartbeats` table
- Anon key can read from `heartbeats_public` view (sanitized, recent only)
- Service-role can read full `heartbeats` table (for backend operations)
- Owners can read full `heartbeats` for their servers (via RLS)

## Notes

- Service-role key **bypasses RLS** automatically - this is expected and required for backend operations
- Views inherit RLS from the base table, so `heartbeats_public` respects the RLS policy (recent heartbeats only)
- The migration is idempotent - safe to run multiple times
