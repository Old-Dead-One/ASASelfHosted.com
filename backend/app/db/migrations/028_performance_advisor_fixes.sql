-- ASASelfHosted.com - Performance Advisor fixes (scale-ready)
-- Addresses Supabase Performance Advisor: auth RLS initplan, multiple permissive policies,
-- duplicate indexes, unindexed foreign key.
-- Run after 027_ingest_rejections_server_id_nullable.sql
--
-- 1. Auth RLS initplan: use (select auth.uid()) so Postgres evaluates once per query, not per row.
-- 2. Merge multiple permissive SELECT policies on clusters and heartbeats into one policy each.
-- 3. Drop duplicate indexes (keep one per pair).
-- 4. Add index on incident_notes(cluster_id) for FK/join performance.

-- ============================================================================
-- 1. DROP DUPLICATE INDEXES (keep one per pair)
-- ============================================================================

-- favorites: idx_favorites_server and idx_favorites_server_id are identical
DROP INDEX IF EXISTS public.idx_favorites_server;

-- favorites: UNIQUE(user_id, server_id) in 001 created favorites_user_id_server_id_key;
-- 010 added uq_favorites_user_server. Drop the redundant constraint (drops its index).
ALTER TABLE public.favorites DROP CONSTRAINT IF EXISTS uq_favorites_user_server;

-- servers: idx_servers_cluster and idx_servers_cluster_id are identical
DROP INDEX IF EXISTS public.idx_servers_cluster;

-- ============================================================================
-- 2. ADD INDEX FOR UNINDEXED FOREIGN KEY
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_incident_notes_cluster_id
    ON public.incident_notes (cluster_id)
    WHERE cluster_id IS NOT NULL;

COMMENT ON INDEX public.idx_incident_notes_cluster_id IS 'Index for FK and queries filtering by cluster_id.';

-- ============================================================================
-- 3. RLS: PROFILES (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile"
    ON public.profiles FOR SELECT
    USING ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING ((select auth.uid()) = id);

-- ============================================================================
-- 4. RLS: CLUSTERS (auth initplan + merge two SELECT policies into one)
-- ============================================================================

DROP POLICY IF EXISTS "Public clusters are readable" ON public.clusters;
DROP POLICY IF EXISTS "Owners can read own clusters" ON public.clusters;
CREATE POLICY "Clusters readable: public or owner"
    ON public.clusters FOR SELECT
    USING (
        visibility = 'public'
        OR (select auth.uid()) = owner_user_id
    );

DROP POLICY IF EXISTS "Owners can create clusters" ON public.clusters;
CREATE POLICY "Owners can create clusters"
    ON public.clusters FOR INSERT
    WITH CHECK ((select auth.uid()) = owner_user_id);

DROP POLICY IF EXISTS "Owners can update own clusters" ON public.clusters;
CREATE POLICY "Owners can update own clusters"
    ON public.clusters FOR UPDATE
    USING ((select auth.uid()) = owner_user_id);

DROP POLICY IF EXISTS "Owners can delete own clusters" ON public.clusters;
CREATE POLICY "Owners can delete own clusters"
    ON public.clusters FOR DELETE
    USING ((select auth.uid()) = owner_user_id);

-- ============================================================================
-- 5. RLS: SERVERS (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Owners can read own servers" ON public.servers;
CREATE POLICY "Owners can read own servers"
    ON public.servers FOR SELECT
    USING ((select auth.uid()) = owner_user_id);

DROP POLICY IF EXISTS "Owners can create servers" ON public.servers;
CREATE POLICY "Owners can create servers"
    ON public.servers FOR INSERT
    WITH CHECK ((select auth.uid()) = owner_user_id);

DROP POLICY IF EXISTS "Owners can update own servers" ON public.servers;
CREATE POLICY "Owners can update own servers"
    ON public.servers FOR UPDATE
    USING ((select auth.uid()) = owner_user_id);

DROP POLICY IF EXISTS "Owners can delete own servers" ON public.servers;
CREATE POLICY "Owners can delete own servers"
    ON public.servers FOR DELETE
    USING ((select auth.uid()) = owner_user_id);

-- ============================================================================
-- 6. RLS: HEARTBEATS (auth initplan + merge two SELECT policies into one)
-- ============================================================================

DROP POLICY IF EXISTS "Public can read recent heartbeats (sanitized)" ON public.heartbeats;
DROP POLICY IF EXISTS "Owners can read own server heartbeats" ON public.heartbeats;
CREATE POLICY "Heartbeats readable: recent public or owner"
    ON public.heartbeats FOR SELECT
    USING (
        received_at > NOW() - INTERVAL '24 hours'
        OR EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = heartbeats.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

-- ============================================================================
-- 7. RLS: FAVORITES (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Users can read own favorites" ON public.favorites;
CREATE POLICY "Users can read own favorites"
    ON public.favorites FOR SELECT
    USING ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can create own favorites" ON public.favorites;
CREATE POLICY "Users can create own favorites"
    ON public.favorites FOR INSERT
    WITH CHECK ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own favorites" ON public.favorites;
CREATE POLICY "Users can delete own favorites"
    ON public.favorites FOR DELETE
    USING ((select auth.uid()) = user_id);

-- ============================================================================
-- 8. RLS: SUBSCRIPTIONS (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Users can read own subscription" ON public.subscriptions;
CREATE POLICY "Users can read own subscription"
    ON public.subscriptions FOR SELECT
    USING ((select auth.uid()) = user_id);

-- ============================================================================
-- 9. RLS: SERVER_SECRETS (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Owners can read own server secrets" ON public.server_secrets;
CREATE POLICY "Owners can read own server secrets"
    ON public.server_secrets FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_secrets.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can create own server secrets" ON public.server_secrets;
CREATE POLICY "Owners can create own server secrets"
    ON public.server_secrets FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_secrets.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can update own server secrets" ON public.server_secrets;
CREATE POLICY "Owners can update own server secrets"
    ON public.server_secrets FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_secrets.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

DROP POLICY IF EXISTS "Owners can delete own server secrets" ON public.server_secrets;
CREATE POLICY "Owners can delete own server secrets"
    ON public.server_secrets FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = server_secrets.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

-- ============================================================================
-- 10. RLS: HEARTBEAT_JOBS (auth initplan)
-- ============================================================================

DROP POLICY IF EXISTS "Owners can read own server heartbeat jobs" ON public.heartbeat_jobs;
CREATE POLICY "Owners can read own server heartbeat jobs"
    ON public.heartbeat_jobs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.servers s
            WHERE s.id = heartbeat_jobs.server_id
            AND s.owner_user_id = (select auth.uid())
        )
    );

-- ============================================================================
-- DONE
-- ============================================================================
-- After running: re-check Supabase Performance Advisor. Auth initplan and
-- multiple permissive policy warnings should be resolved; duplicate index
-- and unindexed FK (incident_notes.cluster_id) addressed.
-- Unused-index suggestions remain informational; keep indexes unless you
-- confirm they are redundant for your query patterns.
