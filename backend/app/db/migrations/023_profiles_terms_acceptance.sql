-- ASASelfHosted.com - Track ToS acceptance on profiles (legal audit)
-- Run after 022. Adds terms_accepted_at (account signup) and server_listing_terms_accepted_at (first server).

-- ============================================================================
-- ADD COLUMNS TO profiles
-- ============================================================================
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS server_listing_terms_accepted_at TIMESTAMPTZ NULL;

COMMENT ON COLUMN public.profiles.terms_accepted_at IS 'When the user accepted ToS at account creation (legal record).';
COMMENT ON COLUMN public.profiles.server_listing_terms_accepted_at IS 'When the user accepted ToS before adding their first server (legal record).';
