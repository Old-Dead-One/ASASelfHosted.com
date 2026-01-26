"""
Supabase client initialization.

Supabase is the source of truth for:
- Authentication
- Database (Postgres)
- Row Level Security (RLS) enforcement

Two clients are provided:
- supabase_anon: Uses anon key, respects RLS policies
- supabase_admin: Uses service role key, bypasses RLS (admin operations only)

Most operations should use the anon client with user JWT tokens to enforce RLS.
Admin client is only for operations that require elevated privileges:
- Stripe webhooks updating subscription state
- Internal maintenance jobs
- Verification reconciliation (if absolutely required)

Directory reads and user-owned writes should use anon client with user's JWT.
Later, you'll likely build request-scoped clients with user JWT attached
so PostgREST enforces RLS as that user.
"""

from supabase import create_client, Client

from app.core.config import get_settings

# Supabase anon client (respects RLS)
# Use this for directory reads and user-owned writes.
# When making requests, attach user's JWT token for RLS enforcement.
# Will be None if SUPABASE_URL or SUPABASE_ANON_KEY are not configured.
# Note: Initialized lazily to avoid import-time side effects.
supabase_anon: Client | None = None

# Supabase admin client (bypasses RLS)
# Use ONLY for:
# - Stripe webhooks updating subscription state
# - Internal maintenance jobs
# - Verification reconciliation (if absolutely required)
# Will be None if SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY are not configured.
# Note: Initialized lazily to avoid import-time side effects.
supabase_admin: Client | None = None


def get_supabase_anon() -> Client | None:
    """
    Get or initialize anon client (lazy initialization).

    Use this instead of accessing supabase_anon directly to avoid import-time side effects.
    """
    global supabase_anon
    if supabase_anon is None:
        settings = get_settings()
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            supabase_anon = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
            )
    return supabase_anon


def get_supabase_admin() -> Client | None:
    """
    Get or initialize admin client (lazy initialization).

    Use this instead of accessing supabase_admin directly to avoid import-time side effects.
    """
    global supabase_admin
    if supabase_admin is None:
        settings = get_settings()
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            supabase_admin = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY
            )
    return supabase_admin


def get_rls_client(user_jwt: str) -> Client:
    """
    Create a request-scoped Supabase client with user JWT attached for RLS enforcement.

    Use this for authenticated operations where RLS should be enforced as the user.
    PostgREST will enforce RLS policies based on the user identity in the JWT.

    Args:
        user_jwt: User's JWT token (from Authorization header, without "Bearer " prefix)

    Returns:
        Supabase client configured with user JWT for RLS enforcement

    Raises:
        RuntimeError if Supabase configuration is missing

    Usage:
        # Public read (no auth required)
        result = supabase_anon.table("servers").select("*").execute()

        # Authenticated RLS read/write (user's permissions enforced)
        client = get_rls_client(user_jwt)
        result = client.table("servers").select("*").eq("owner_user_id", user_id).execute()

        # Admin operation (bypasses RLS)
        result = supabase_admin.table("subscriptions").update(...).execute()
    """
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise RuntimeError("Supabase anon client not configured")

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    client.postgrest.auth(user_jwt)
    return client
