"""
Repository dependency providers.

Centralized dependency injection for repository selection.
This keeps routes clean and makes environment-based switching trivial.
"""

from app.core.config import get_settings
from app.db.directory_repo import DirectoryRepository
from app.db.mock_directory_repo import MockDirectoryRepository
from app.db.supabase_directory_repo import SupabaseDirectoryRepository

# Reuse a single mock repo instance (stateless, so safe to share)
_mock_repo = MockDirectoryRepository()

# Reuse a single Supabase repo instance (stateless client, safe to share)
_supabase_repo: SupabaseDirectoryRepository | None = None


def get_directory_repo() -> DirectoryRepository:
    """
    Directory repository provider.

    local/development/test -> MockDirectoryRepository (Sprint 1)
    staging/production -> SupabaseDirectoryRepository (Sprint 2+) (fail fast if not configured)
    """
    settings = get_settings()

    # Local-ish environments use mock data
    if settings.ENV in ("local", "development", "test"):
        return _mock_repo

    # Non-local must never fall back to mock data.
    # Return Supabase repository (will fail fast if not configured)
    global _supabase_repo
    if _supabase_repo is None:
        try:
            _supabase_repo = SupabaseDirectoryRepository()
        except RuntimeError as e:
            raise RuntimeError(
                "Directory repository not configured for this environment (Sprint 2+)"
            ) from e

    return _supabase_repo
