-- ASASelfHosted.com - Mods Catalog Table
-- Stores minimal mod metadata (id, name) for Ark: Survival Ascended mods from CurseForge
-- Run after 015. Creates mods_catalog table for mod ID to name resolution.

-- ============================================================================
-- CREATE mods_catalog TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.mods_catalog (
    mod_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NULL,  -- Optional convenience field
    source TEXT NOT NULL DEFAULT 'curseforge',  -- 'curseforge' or 'user'
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.mods_catalog IS 'Minimal mod catalog for ASA mods. Stores only id->name mapping for display purposes.';
COMMENT ON COLUMN public.mods_catalog.mod_id IS 'CurseForge mod ID (BIGINT primary key)';
COMMENT ON COLUMN public.mods_catalog.name IS 'Mod display name';
COMMENT ON COLUMN public.mods_catalog.slug IS 'Optional mod slug for convenience';
COMMENT ON COLUMN public.mods_catalog.source IS 'Source of mod data: curseforge or user';
COMMENT ON COLUMN public.mods_catalog.updated_at IS 'Last update timestamp';
COMMENT ON COLUMN public.mods_catalog.created_at IS 'Creation timestamp';

-- ============================================================================
-- INDEXES
-- ============================================================================
-- Index for fast name search/autocomplete
CREATE INDEX IF NOT EXISTS idx_mods_catalog_name_lower ON public.mods_catalog (lower(name));

-- Index for updated_at (useful for cleanup/refresh operations)
CREATE INDEX IF NOT EXISTS idx_mods_catalog_updated_at ON public.mods_catalog (updated_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE public.mods_catalog ENABLE ROW LEVEL SECURITY;

-- Public read access (anon can SELECT) - it's just id->name mapping
CREATE POLICY "Public read access for mods_catalog"
    ON public.mods_catalog
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Service role can insert/update (backend writes only)
CREATE POLICY "Service role can upsert mods_catalog"
    ON public.mods_catalog
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- GRANT PERMISSIONS FOR PostgREST
-- ============================================================================
-- Grant SELECT to anon and authenticated (public read)
GRANT SELECT ON public.mods_catalog TO anon, authenticated;

-- Grant ALL to service_role (backend writes)
GRANT ALL ON public.mods_catalog TO service_role;

-- ============================================================================
-- NOTIFY PostgREST TO RELOAD SCHEMA
-- ============================================================================
NOTIFY pgrst, 'reload schema';
