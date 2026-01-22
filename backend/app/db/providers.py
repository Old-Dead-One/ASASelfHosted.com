"""
Repository dependency providers.

Centralized dependency injection for repository selection.
This keeps routes clean and makes environment-based switching trivial.
"""

from app.core.config import get_settings
from app.db.directory_repo import DirectoryRepository
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.heartbeat_repo import HeartbeatRepository
from app.db.mock_directory_repo import MockDirectoryRepository
from app.db.servers_derived_repo import ServersDerivedRepository
from app.db.supabase_directory_repo import SupabaseDirectoryRepository
from app.db.supabase_heartbeat_jobs_repo import SupabaseHeartbeatJobsRepository
from app.db.supabase_heartbeat_repo import SupabaseHeartbeatRepository
from app.db.supabase_servers_derived_repo import SupabaseServersDerivedRepository

# Reuse a single mock repo instance (stateless, so safe to share)
_mock_repo = MockDirectoryRepository()

# Reuse a single Supabase repo instance (stateless client, safe to share)
_supabase_repo: SupabaseDirectoryRepository | None = None


def get_directory_repo() -> DirectoryRepository:
    """
    Directory repository provider.

    Prefers Supabase if configured (SUPABASE_URL and SUPABASE_ANON_KEY set).
    Falls back to mock data in local/dev/test if Supabase not configured.
    In staging/production, Supabase is required (fails fast if not configured).
    """
    settings = get_settings()

    # Try to use Supabase if credentials are configured
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        global _supabase_repo
        if _supabase_repo is None:
            try:
                _supabase_repo = SupabaseDirectoryRepository()
            except RuntimeError as e:
                # In staging/production, Supabase is required - fail fast
                if settings.ENV in ("staging", "production"):
                    raise RuntimeError(
                        "Directory repository not configured for this environment (Sprint 2+)"
                    ) from e
                # In local/dev/test, fall back to mock if Supabase init fails
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Supabase repository initialization failed, falling back to mock: {e}")
                return _mock_repo
        
        # If Supabase repo is configured, use it
        if _supabase_repo._configured:
            return _supabase_repo
        # If Supabase repo exists but isn't configured, fall back to mock in local/dev/test
        elif settings.ENV in ("local", "development", "test"):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Supabase repository not configured ({_supabase_repo._config_error}), "
                "falling back to mock data"
            )
            return _mock_repo
        else:
            # In staging/production, must have Supabase
            raise RuntimeError(
                f"Directory repository not configured: {_supabase_repo._config_error}"
            )

    # No Supabase credentials - use mock in local/dev/test, fail in staging/production
    if settings.ENV in ("local", "development", "test"):
        return _mock_repo
    else:
        raise RuntimeError(
            "Supabase credentials required in staging/production. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in environment."
        )


# Heartbeat repository instances (stateless, safe to share)
_heartbeat_repo: HeartbeatRepository | None = None
_heartbeat_jobs_repo: HeartbeatJobsRepository | None = None
_servers_derived_repo: ServersDerivedRepository | None = None


def get_heartbeat_repo() -> HeartbeatRepository:
    """
    Heartbeat repository provider.
    
    Returns SupabaseHeartbeatRepository (requires service_role key).
    """
    global _heartbeat_repo
    if _heartbeat_repo is None:
        _heartbeat_repo = SupabaseHeartbeatRepository()
    return _heartbeat_repo


def get_heartbeat_jobs_repo() -> HeartbeatJobsRepository:
    """
    Heartbeat jobs repository provider.
    
    Returns SupabaseHeartbeatJobsRepository (requires service_role key).
    """
    global _heartbeat_jobs_repo
    if _heartbeat_jobs_repo is None:
        _heartbeat_jobs_repo = SupabaseHeartbeatJobsRepository()
    return _heartbeat_jobs_repo


def get_servers_derived_repo() -> ServersDerivedRepository:
    """
    Servers derived state repository provider.
    
    Returns SupabaseServersDerivedRepository (requires service_role key).
    """
    global _servers_derived_repo
    if _servers_derived_repo is None:
        _servers_derived_repo = SupabaseServersDerivedRepository()
    return _servers_derived_repo
