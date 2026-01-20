"""
Supabase client initialization.

Supabase is the source of truth for:
- Authentication
- Database (Postgres)
- Row Level Security (RLS) enforcement

Backend uses service role key for operations that bypass RLS when necessary.
Most operations should go through RLS policies, not service role.
"""

from supabase import create_client, Client

from app.core.config import settings

# Supabase client using service role key
# Use this for backend operations that require elevated privileges
# Most operations should use RLS policies instead
# Will be None if SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY are not configured
supabase: Client | None = None

if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
