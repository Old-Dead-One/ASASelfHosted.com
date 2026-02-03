-- ASASelfHosted.com - Maps Table
-- Reference table for official ASA map names. Used for directory filter and form dropdown.
-- servers.map_name remains free text; this table provides normalized options.
-- Run after 020.

-- ============================================================================
-- CREATE maps TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.maps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.maps IS 'Reference list of known ASA map names for filter and form dropdown. servers.map_name is not FK.';
COMMENT ON COLUMN public.maps.name IS 'Display name (e.g. The Island, Ragnarok)';
COMMENT ON COLUMN public.maps.sort_order IS 'Display order in dropdowns (lower first)';

-- ============================================================================
-- INDEX
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_maps_sort_order ON public.maps (sort_order);

-- ============================================================================
-- RLS
-- ============================================================================
ALTER TABLE public.maps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read maps"
    ON public.maps FOR SELECT
    TO anon, authenticated
    USING (true);

-- Service role can manage (for seed/backfill)
CREATE POLICY "Service role manage maps"
    ON public.maps FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

GRANT SELECT ON public.maps TO anon, authenticated;
GRANT ALL ON public.maps TO service_role;

-- ============================================================================
-- SEED OFFICIAL ASA MAPS
-- ============================================================================
INSERT INTO public.maps (name, sort_order) VALUES
    ('The Island', 1),
    ('Scorched Earth', 2),
    ('Aberration', 3),
    ('Extinction', 4),
    ('Genesis Part 1', 5),
    ('Genesis Part 2', 6),
    ('Ragnarok', 7),
    ('Valguero', 8),
    ('The Center', 9),
    ('Lost Island', 10),
    ('Fjordur', 11),
    ('Crystal Isles', 12)
ON CONFLICT (name) DO NOTHING;
