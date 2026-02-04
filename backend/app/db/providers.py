"""
Repository dependency providers.

Centralized dependency injection for repository selection.
This keeps routes clean and makes environment-based switching trivial.
"""

from app.core.config import get_settings
from app.db.directory_clusters_repo import DirectoryClustersRepository
from app.db.directory_repo import DirectoryRepository
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.heartbeat_repo import HeartbeatRepository
from app.db.ingest_rejections_repo import IngestRejectionsRepository
from app.db.maps_repo import MapsRepository
from app.db.mock_directory_clusters_repo import MockDirectoryClustersRepository
from app.db.mock_directory_repo import MockDirectoryRepository
from app.db.mods_catalog_repo import ModsCatalogRepository
from app.db.servers_derived_repo import ServersDerivedRepository
from app.db.servers_repo import ServersRepository
from app.db.supabase_directory_clusters_repo import SupabaseDirectoryClustersRepository
from app.db.supabase_directory_repo import SupabaseDirectoryRepository
from app.db.supabase_heartbeat_jobs_repo import SupabaseHeartbeatJobsRepository
from app.db.supabase_heartbeat_repo import SupabaseHeartbeatRepository
from app.db.supabase_ingest_rejections_repo import SupabaseIngestRejectionsRepository
from app.db.supabase_maps_repo import SupabaseMapsRepository
from app.db.supabase_mods_catalog_repo import SupabaseModsCatalogRepository
from app.db.supabase_servers_derived_repo import SupabaseServersDerivedRepository
from app.db.supabase_servers_repo import SupabaseServersRepository

# Reuse a single mock repo instance (stateless, so safe to share)
_mock_repo = MockDirectoryRepository()
_mock_clusters_repo = MockDirectoryClustersRepository()

# Reuse a single Supabase repo instance (stateless client, safe to share)
_supabase_repo: SupabaseDirectoryRepository | None = None
_supabase_clusters_repo: SupabaseDirectoryClustersRepository | None = None


def get_directory_repo() -> DirectoryRepository:
    """
    Directory repository provider.

    Prefers Supabase if configured (SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY set).
    Uses service_role so directory_view can stay SECURITY INVOKER without granting anon SELECT on base tables.
    Falls back to mock data in local/dev/test if Supabase not configured.
    In staging/production, Supabase is required (fails fast if not configured).
    """
    settings = get_settings()

    # Try to use Supabase if credentials are configured (service_role for directory so INVOKER views work)
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
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
                logger.warning(
                    f"Supabase repository initialization failed, falling back to mock: {e}"
                )
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


# Heartbeat and ingest rejections repository instances (stateless, safe to share)
_heartbeat_repo: HeartbeatRepository | None = None
_heartbeat_jobs_repo: HeartbeatJobsRepository | None = None
_servers_derived_repo: ServersDerivedRepository | None = None
_ingest_rejections_repo: IngestRejectionsRepository | None = None


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


def get_ingest_rejections_repo() -> IngestRejectionsRepository:
    """
    Ingest rejections repository provider.

    Returns SupabaseIngestRejectionsRepository (requires service_role key).
    """
    global _ingest_rejections_repo
    if _ingest_rejections_repo is None:
        _ingest_rejections_repo = SupabaseIngestRejectionsRepository()
    return _ingest_rejections_repo


def get_directory_clusters_repo() -> DirectoryClustersRepository:
    """
    Directory clusters repository provider.

    Returns SupabaseDirectoryClustersRepository (uses anon key for public access).
    Falls back behavior similar to get_directory_repo() if needed.
    """
    settings = get_settings()

    # Try to use Supabase if credentials are configured
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        global _supabase_clusters_repo
        if _supabase_clusters_repo is None:
            try:
                _supabase_clusters_repo = SupabaseDirectoryClustersRepository()
            except RuntimeError as e:
                # In staging/production, Supabase is required - fail fast
                if settings.ENV in ("staging", "production"):
                    raise RuntimeError(
                        "Directory clusters repository not configured for this environment"
                    ) from e
                # In local/dev/test, allow failure but will raise on use
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Supabase clusters repository initialization failed: {e}"
                )

        # If Supabase repo is configured, use it
        if _supabase_clusters_repo and _supabase_clusters_repo._configured:
            return _supabase_clusters_repo
        # If Supabase repo exists but isn't configured, fall back to mock in local/dev/test
        elif settings.ENV in ("local", "development", "test"):
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Supabase clusters repository not configured ({_supabase_clusters_repo._config_error if _supabase_clusters_repo else 'not initialized'}), "
                "falling back to mock data"
            )
            return _mock_clusters_repo
        else:
            # In staging/production, must have Supabase
            raise RuntimeError(
                f"Directory clusters repository not configured: {_supabase_clusters_repo._config_error if _supabase_clusters_repo else 'not initialized'}"
            )

    # No Supabase credentials - use mock in local/dev/test, fail in staging/production
    if settings.ENV in ("local", "development", "test"):
        return _mock_clusters_repo
    else:
        raise RuntimeError(
            "Supabase credentials required in staging/production. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in environment."
        )


def get_servers_repo(user_jwt: str) -> ServersRepository:
    """
    Servers repository provider.
    
    Creates a request-scoped repository with RLS client.
    Requires user JWT token for RLS enforcement.
    
    Args:
        user_jwt: User's JWT token (from Authorization header)
    
    Returns:
        SupabaseServersRepository with RLS client configured
    """
    return SupabaseServersRepository(user_jwt)


# Maps repository instance (stateless, safe to share)
_maps_repo: MapsRepository | None = None


def get_maps_repo() -> MapsRepository:
    """
    Maps repository provider.

    Returns SupabaseMapsRepository (uses anon key; maps table has public read).
    If Supabase anon is not configured, list_all returns empty.
    """
    global _maps_repo
    if _maps_repo is None:
        _maps_repo = SupabaseMapsRepository()
    return _maps_repo


# Mods catalog repository instance (stateless, safe to share)
_mods_catalog_repo: ModsCatalogRepository | None = None


def get_mods_catalog_repo() -> ModsCatalogRepository:
    """
    Mods catalog repository provider.

    Returns SupabaseModsCatalogRepository (requires service_role key).
    """
    global _mods_catalog_repo
    if _mods_catalog_repo is None:
        _mods_catalog_repo = SupabaseModsCatalogRepository()
    return _mods_catalog_repo
