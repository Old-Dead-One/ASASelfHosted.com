"""
Supabase mods catalog repository.

Mod ID to name resolution using Supabase.
Uses service_role key for writes (upserts).
"""

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin
from app.db.mods_catalog_repo import ModCatalogEntry, ModsCatalogRepository


class SupabaseModsCatalogRepository(ModsCatalogRepository):
    """
    Supabase-based mods catalog repository.

    Uses service_role key for writes (upserts).
    Public read access via anon key is available but not used here.
    """

    def __init__(self):
        settings = get_settings()

        self._supabase = None
        self._configured = False
        self._config_error: str | None = None

        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseModsCatalogRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
                )
            self._config_error = "Supabase service_role credentials not configured"
        else:
            try:
                self._supabase = get_supabase_admin()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_admin() returned None")
                self._configured = True
            except Exception as e:
                if settings.ENV not in ("local", "development", "test"):
                    raise RuntimeError(
                        f"Failed to initialize Supabase admin client: {str(e)}"
                    ) from e
                self._config_error = (
                    f"Supabase admin client initialization failed: {str(e)}"
                )

    async def get_many(self, mod_ids: list[int]) -> dict[int, str]:
        """
        Get mod names for multiple mod IDs.

        Args:
            mod_ids: List of mod IDs to look up

        Returns:
            Dictionary mapping mod_id -> name. Missing IDs are omitted.
        """
        if not self._configured:
            error_msg = "SupabaseModsCatalogRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        if not mod_ids:
            return {}

        # Query mods_catalog table
        try:
            response = (
                self._supabase.table("mods_catalog")
                .select("mod_id,name")
                .in_("mod_id", mod_ids)
                .execute()
            )

            # Build mapping
            result: dict[int, str] = {}
            for row in response.data:
                mod_id = int(row["mod_id"])
                name = str(row["name"])
                result[mod_id] = name

            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch mod names: {str(e)}") from e

    async def upsert_many(self, entries: list[ModCatalogEntry]) -> None:
        """
        Upsert multiple mod catalog entries.

        Args:
            entries: List of mod catalog entries to upsert
        """
        if not self._configured:
            error_msg = "SupabaseModsCatalogRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        if not entries:
            return

        # Prepare upsert data
        upsert_data = []
        for entry in entries:
            upsert_data.append(
                {
                    "mod_id": entry["mod_id"],
                    "name": entry["name"],
                    "slug": entry.get("slug"),
                    "source": entry.get("source", "curseforge"),
                }
            )

        # Upsert using mod_id as primary key
        try:
            self._supabase.table("mods_catalog").upsert(
                upsert_data, on_conflict="mod_id"
            ).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to upsert mod catalog entries: {str(e)}") from e

    async def search_by_prefix(
        self, query: str, limit: int = 20
    ) -> list[ModCatalogEntry]:
        """
        Search mods by name prefix (for autocomplete).

        Args:
            query: Search query (prefix)
            limit: Maximum number of results

        Returns:
            List of matching mod catalog entries
        """
        if not self._configured:
            error_msg = "SupabaseModsCatalogRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        if not query:
            return []

        # Search using ILIKE on name (case-insensitive prefix match)
        try:
            response = (
                self._supabase.table("mods_catalog")
                .select("mod_id,name,slug,source")
                .ilike("name", f"{query}%")
                .limit(limit)
                .execute()
            )

            result: list[ModCatalogEntry] = []
            for row in response.data:
                result.append(
                    {
                        "mod_id": int(row["mod_id"]),
                        "name": str(row["name"]),
                        "slug": row.get("slug"),
                        "source": str(row.get("source", "curseforge")),
                    }
                )

            return result
        except Exception as e:
            raise RuntimeError(f"Failed to search mods: {str(e)}") from e
