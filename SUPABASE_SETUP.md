# Supabase Setup Guide

This guide walks you through setting up a Supabase project and applying the database migrations for ASASelfHosted.com.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Access to your Supabase project dashboard

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in project details:
   - **Name**: `asa-self-hosted-directory` (or your preferred name)
   - **Database Password**: Choose a strong password (save this securely)
   - **Region**: Choose the region closest to your users
   - **Pricing Plan**: Free tier is fine for development
4. Click "Create new project"
5. Wait for the project to be provisioned (2-3 minutes)

## Step 2: Get Project Credentials

Once your project is ready:

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy the following values (you'll need them for environment variables):
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (under "Project API keys")
   - **service_role** key (under "Project API keys" - keep this secret!)

## Step 3: Run Database Migrations

1. Go to **SQL Editor** in your Supabase dashboard
2. Click "New query"

### Migration 1: Sprint 0 Schema

1. Open `backend/app/db/migrations/001_sprint_0_schema.sql` in your editor
2. Copy the entire contents
3. Paste into the SQL Editor
4. Click "Run" (or press Cmd/Ctrl + Enter)
5. Wait for execution to complete
6. Verify success: Check that tables appear in **Database** → **Tables**

### Migration 2: Sprint 3 Directory View

1. Open `backend/app/db/migrations/003_sprint_3_directory_view.sql` in your editor
2. Copy the entire contents
3. Paste into Supabase SQL Editor
4. Click "Run" (or press Cmd/Ctrl + Enter)
5. Verify success (should see "Success. No rows returned")

### Migration 3: Sprint 4 Agent Authentication

1. Open `backend/app/db/migrations/006_sprint_4_agent_auth.sql` in your editor
2. Copy the entire contents
3. Paste into the SQL Editor
4. Click "Run"
5. Wait for execution to complete
6. Verify success:
   - Check that new columns exist in `servers` table
   - Check that `directory_view` has been updated
   - Check that indexes have been created

## Step 4: Configure Environment Variables

Add the following to your backend `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT Verification (optional for local development)
SUPABASE_JWT_ISSUER=https://xxxxx.supabase.co/auth/v1
SUPABASE_JWKS_URL=https://xxxxx.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_JWT_AUDIENCE=authenticated
```

**Important Security Notes:**
- `SUPABASE_ANON_KEY` is safe to expose (used in frontend)
- `SUPABASE_SERVICE_ROLE_KEY` must be kept secret (backend only)
- Never commit `.env` files to version control

## Step 5: Verify Setup

### Check Tables

1. Go to **Database** → **Tables** in Supabase dashboard
2. Verify these tables exist:
   - `profiles`
   - `clusters`
   - `servers`
   - `heartbeats`
   - `favorites`
   - `subscriptions`

### Check View

1. Go to **Database** → **Views** in Supabase dashboard
2. Verify `directory_view` exists
3. Click on `directory_view` and verify it has all expected columns

### Check Indexes

1. Go to **Database** → **Indexes** in Supabase dashboard
2. Verify these indexes exist on `servers` table:
   - `idx_servers_updated_at_id_desc`
   - `idx_servers_ruleset`
   - `idx_servers_game_mode`
   - `idx_servers_effective_status`
   - `idx_servers_cluster_id`
   - `idx_servers_is_verified`
   - `idx_servers_players_current`

### Test Query

1. Go to **SQL Editor** in Supabase dashboard
2. Run this test query:

```sql
SELECT * FROM directory_view LIMIT 5;
```

3. If the query succeeds, your setup is correct!

## Step 6: Test Backend Connection

1. Start your backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. Test the directory endpoint:
   ```bash
   curl http://localhost:5173/api/v1/directory/servers
   ```

3. If you get a response (even if empty), the connection is working!

## Troubleshooting

### "SupabaseDirectoryRepository not configured" Error

- Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in your `.env` file
- Verify the values are correct (no extra spaces, correct format)
- Restart your backend server after changing `.env`

### "Failed to query directory_view" Error

- Verify `directory_view` exists in Supabase (Database → Views)
- Check that all migrations ran successfully (001, 003, 006)
- Verify RLS policies allow public read access

### Migration Errors

- If a migration fails, check the error message in SQL Editor
- Common issues:
  - Enum types already exist: This is OK, you can skip creating them
  - Columns already exist: You may have run the migration before
  - Permission errors: Check that you're using the correct database user

### Index Creation Warnings

- Some indexes may show warnings if they already exist - this is OK
- You can safely ignore "already exists" errors for indexes

## Next Steps

After setup is complete:

1. **Add test data** (optional): Insert some test servers to verify filtering works
2. **Test filters**: Try different filter combinations via the API
3. **Monitor performance**: Check query performance in Supabase dashboard
4. **Set up backups**: Configure automatic backups in Supabase dashboard

## Optional: Fix Supabase security advisories

If the Supabase dashboard shows security warnings, you can address them as follows.

### 1. Views (directory_view, heartbeats_public) – SECURITY DEFINER warning

The backend **directory** API uses the **service_role** key to query these views, so they can stay **SECURITY INVOKER** (no warning) without granting anon SELECT on base tables.

**To clear the advisory:** Run `020_views_security_invoker.sql` in SQL Editor. It runs:

```sql
ALTER VIEW directory_view SET (security_invoker = true);
ALTER VIEW heartbeats_public SET (security_invoker = true);
```

1. Open `backend/app/db/migrations/020_views_security_invoker.sql`
2. Copy its contents into Supabase SQL Editor and run it

The advisory should disappear. Directory listing keeps working (backend uses service_role).

### 2. Function `update_updated_at_column` – mutable search_path

Run this migration in **SQL Editor** so the function has an explicit `search_path`:

1. Open `backend/app/db/migrations/018_function_search_path.sql`
2. Copy its contents into SQL Editor and run it

That sets `search_path = public` on the function and clears the “role mutable search_path” advisory.

### 3. Auth – Leaked password protection (HaveIBeenPwned)

Supabase can check passwords against HaveIBeenPwned.org to block compromised passwords. **This requires a Pro (or Teams/Enterprise) plan**; it is not available on the free tier.

When you upgrade to Pro you can enable it (e.g. via **Authentication** → **Hooks** or the Auth settings for leaked-password checks). The app works fine without it on the free plan.

## Production Considerations

For production deployments:

1. **Enable backups**: Set up automatic daily backups in Supabase
2. **Monitor usage**: Watch database size and query performance
3. **Set up alerts**: Configure alerts for errors and performance issues
4. **Review RLS policies**: Ensure RLS policies are correctly configured
5. **Use connection pooling**: Consider using Supabase connection pooling for high traffic

## Support

If you encounter issues:

1. Check the Supabase documentation: https://supabase.com/docs
2. Review migration files for syntax errors
3. Check Supabase dashboard logs for detailed error messages
4. Verify your environment variables are correctly set
