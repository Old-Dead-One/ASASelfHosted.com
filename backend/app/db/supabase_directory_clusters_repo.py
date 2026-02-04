"""
Supabase directory clusters repository.

Read-only repository that queries clusters table in Supabase.
Implements DirectoryClustersRepository for public cluster directory access.
"""

from datetime import datetime, timezone
from typing import Sequence

from app.core.config import get_settings
from app.core.errors import DomainValidationError
from app.core.supabase import get_supabase_admin
from app.db.directory_clusters_repo import DirectoryClustersRepository
from app.schemas.directory import ClusterVisibility, DirectoryCluster, SortOrder
from app.utils.cursor import create_cursor, parse_cursor


class SupabaseDirectoryClustersRepository(DirectoryClustersRepository):
    """
    Supabase-based directory clusters repository.

    Queries from clusters table (read-only, public-safe).
    Fails fast if Supabase is not configured.
    """

    def __init__(self):
        settings = get_settings()

        # Always initialize state explicitly
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None

        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseDirectoryClustersRepository requires SUPABASE_URL and SUPABASE_ANON_KEY in non-local environments"
                )
            # In local/dev/test, allow unconfigured state (will raise on actual use)
            self._config_error = "Supabase credentials not configured"
        else:
            # Credentials exist - attempt to initialize client
            try:
                from app.core.supabase import get_supabase_anon

                self._supabase = get_supabase_anon()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_anon() returned None")
                self._configured = True
            except Exception as e:
                # In non-local, client init failure is a hard error
                if settings.ENV not in ("local", "development", "test"):
                    raise RuntimeError(
                        f"Failed to initialize Supabase client: {str(e)}"
                    ) from e
                # In local/dev/test, allow failure but record it
                self._config_error = f"Supabase client initialization failed: {str(e)}"

    @staticmethod
    def _format_cursor_value_for_postgrest(value: object) -> str:
        """Format cursor last_value for PostgREST or_ filter."""
        if hasattr(value, "isoformat"):
            s = value.isoformat()
        elif value is None:
            s = "null"
        else:
            s = str(value)
        if any(c in s for c in ",:()"):
            return f'"{s}"'
        return s

    @staticmethod
    def _map_sort_by_to_column(sort_by: str) -> str:
        """
        Map sort_by parameter to database column name.

        Args:
            sort_by: Sort key parameter ("updated" or "name")
            Note: "server_count" is not yet supported (requires aggregation/view)

        Returns:
            Database column name for sorting

        Raises:
            DomainValidationError: If sort_by is not supported
        """
        if sort_by not in ("updated", "name"):
            from app.core.errors import DomainValidationError

            raise DomainValidationError(
                f"sort_by must be 'updated' or 'name', got '{sort_by}'. "
                "server_count sorting is not yet supported."
            )
        mapping = {
            "updated": "updated_at",
            "name": "name",
        }
        if sort_by not in mapping:
            from app.core.errors import DomainValidationError

            raise DomainValidationError(
                f"sort_by must be 'updated' or 'name', got '{sort_by}'. "
                "server_count sorting is not yet supported."
            )
        return mapping[sort_by]

    async def list_clusters(
        self,
        limit: int = 25,
        cursor: str | None = None,
        visibility: ClusterVisibility | None = None,
        sort_by: str = "updated",
        order: SortOrder = "desc",
        now_utc: datetime | None = None,
    ) -> tuple[Sequence[DirectoryCluster], str | None]:
        """
        List clusters from Supabase with cursor pagination.

        Visibility Rules:
            - If visibility is None: return only public clusters (default for directory listing)
            - If visibility is "public": return only public clusters
            - If visibility is "unlisted": raise DomainValidationError (unlisted clusters not accessible via public directory)

        Note: This repository uses anon key, so unlisted clusters are RLS-blocked for anonymous requests.
        Public directory endpoints only support public clusters.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryClustersRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        # Enforce max limit (400 error if > 100)
        if limit > 100:
            raise DomainValidationError(f"limit must be <= 100, got {limit}")

        # Parse and validate cursor
        parsed_cursor = None
        if cursor:
            parsed_cursor = parse_cursor(cursor)
            # Validate cursor matches request parameters
            parsed_cursor.validate_match(sort_by, order)

        # Get request handling time (consistent across response)
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        # Map sort_by to database column
        sort_column = self._map_sort_by_to_column(sort_by)

        # Build query
        select_columns = "id,name,slug,visibility,created_at,updated_at"
        query = self._supabase.table("clusters").select(select_columns)

        # Apply visibility filter: public-only (reject unlisted)
        if visibility == "unlisted":
            raise DomainValidationError(
                "Unlisted clusters are not accessible via public directory. Only 'public' is supported."
            )
        # visibility is None or "public" → return only public clusters
        query = query.eq("visibility", "public")

        # Apply cursor seek predicate if cursor provided
        # Seek: (sort_col < last_value) OR (sort_col = last_value AND id > last_id) for DESC;
        #       (sort_col > last_value) OR (sort_col = last_value AND id > last_id) for ASC.
        # Use PostgREST or_() with nested and(); then limit(limit+1). No OFFSET, no Python filter.
        if parsed_cursor:
            v = self._format_cursor_value_for_postgrest(parsed_cursor.last_value)
            lid = str(parsed_cursor.last_id)
            if any(c in lid for c in ",:()"):
                lid = f'"{lid}"'
            if order == "desc":
                seek = f"{sort_column}.lt.{v},and({sort_column}.eq.{v},id.gt.{lid})"
            else:
                seek = f"{sort_column}.gt.{v},and({sort_column}.eq.{v},id.gt.{lid})"
            query = query.or_(seek)

        # ORDER BY sort_column, id (tie-break)
        if order == "asc":
            query = query.order(sort_column, desc=False).order("id", desc=False)
        else:
            query = query.order(sort_column, desc=True).order("id", desc=False)

        query = query.limit(limit + 1)

        # Execute query
        try:
            response = query.execute()
        except Exception as e:
            raise RuntimeError(f"Failed to query clusters: {str(e)}") from e

        data = response.data if hasattr(response, "data") else []

        # Check if there's a next page (we have limit + 1 rows)
        has_next = len(data) > limit
        if has_next:
            data = data[:limit]  # Keep only limit items

        # Server counts: use admin client (anon may not have SELECT on servers)
        cluster_ids = [str(r.get("id")) for r in data if r.get("id")]
        counts_by_id = await self._get_server_counts_for_clusters(cluster_ids)

        # Convert to DirectoryCluster objects
        clusters: list[DirectoryCluster] = []
        last_row = None
        for row in data:
            try:
                cid = str(row.get("id"))
                # Parse timestamps
                created_at_str = row.get("created_at")
                updated_at_str = row.get("updated_at")

                created_at = (
                    datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if created_at_str
                    else datetime.now(timezone.utc)
                )
                updated_at = (
                    datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                    if updated_at_str
                    else datetime.now(timezone.utc)
                )

                # Ensure timezone-aware
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)

                cluster = DirectoryCluster(
                    id=cid,
                    name=str(row.get("name")),
                    slug=str(row.get("slug")),
                    visibility=row.get(
                        "visibility"
                    ),  # Should be "public" or "unlisted"
                    created_at=created_at,
                    updated_at=updated_at,
                    server_count=counts_by_id.get(cid, 0),
                )
                clusters.append(cluster)
                last_row = row
            except Exception as e:
                import logging
                from app.core.config import get_settings

                logger = logging.getLogger(__name__)
                settings = get_settings()

                error_msg = f"Failed to parse cluster row: {e}"

                # In local/dev/test: log and skip
                if settings.ENV in ("local", "development", "test"):
                    logger.warning(error_msg)
                    continue
                else:
                    # Production: fail fast
                    logger.error(error_msg)
                    raise RuntimeError(
                        f"Failed to parse cluster row from clusters table: {e}"
                    ) from e

        # Generate next_cursor if there are more results
        next_cursor = None
        if has_next and last_row:
            last_sort_value = last_row.get(sort_column)
            last_id = last_row.get("id")

            if last_id:
                next_cursor = create_cursor(sort_by, order, last_sort_value, last_id)

        return clusters, next_cursor

    async def _get_server_counts_for_clusters(
        self, cluster_ids: list[str]
    ) -> dict[str, int]:
        """Return map of cluster_id -> server count. Uses admin client."""
        if not cluster_ids:
            return {}
        admin = get_supabase_admin()
        if not admin:
            return {cid: 0 for cid in cluster_ids}
        try:
            r = (
                admin.table("servers")
                .select("cluster_id")
                .in_("cluster_id", cluster_ids)
                .execute()
            )
            data = r.data if hasattr(r, "data") else []
            counts: dict[str, int] = {cid: 0 for cid in cluster_ids}
            for row in data:
                cid = row.get("cluster_id")
                if cid:
                    cid_str = str(cid)
                    if cid_str in counts:
                        counts[cid_str] = counts[cid_str] + 1
            return counts
        except Exception:
            return {cid: 0 for cid in cluster_ids}

    async def get_cluster(
        self,
        cluster_id: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """
        Get cluster by ID from Supabase.

        Visibility Rules:
            - public: Returns cluster if found (readable by everyone)
            - unlisted: Returns None (404 in route layer) - unlisted clusters not accessible via public directory
            - private: Does not exist in DB enum, so not applicable

        CONTRACT DECISION (Sprint 5):
        - Public directory endpoints only support public clusters
        - Unlisted clusters are owner-only (RLS-enforced) and cannot be accessed via public endpoints
        - Anonymous requests to unlisted cluster IDs return 404

        This implementation uses anon key, so RLS policies block unlisted cluster access.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryClustersRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        try:
            select_columns = "id,name,slug,visibility,created_at,updated_at"
            response = (
                self._supabase.table("clusters")
                .select(select_columns)
                .eq("id", cluster_id)
                .eq("visibility", "public")
                .limit(1)
                .execute()
            )

            data = response.data if hasattr(response, "data") else []
            if not data:
                # Cluster not found or RLS blocked access (e.g., unlisted cluster for non-owner)
                return None

            # Convert to DirectoryCluster
            row = data[0]

            # Parse timestamps
            created_at_str = row.get("created_at")
            updated_at_str = row.get("updated_at")

            created_at = (
                datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_at_str
                else datetime.now(timezone.utc)
            )
            updated_at = (
                datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                if updated_at_str
                else datetime.now(timezone.utc)
            )

            # Ensure timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)

            cid = str(row.get("id"))
            count = 0
            try:
                counts = await self._get_server_counts_for_clusters([cid])
                count = counts.get(cid, 0)
            except Exception:
                pass
            cluster = DirectoryCluster(
                id=cid,
                name=str(row.get("name")),
                slug=str(row.get("slug")),
                visibility=row.get("visibility"),
                created_at=created_at,
                updated_at=updated_at,
                server_count=count,
            )
            return cluster

        except Exception as e:
            raise RuntimeError(
                f"Failed to query clusters table for cluster {cluster_id}: {str(e)}"
            ) from e

    async def get_cluster_by_slug(
        self,
        slug: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """
        Get cluster by slug from Supabase (public directory).

        Returns cluster if found and visibility is public; None otherwise.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryClustersRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        try:
            select_columns = "id,name,slug,visibility,created_at,updated_at"
            response = (
                self._supabase.table("clusters")
                .select(select_columns)
                .eq("slug", slug)
                .eq("visibility", "public")
                .limit(1)
                .execute()
            )

            data = response.data if hasattr(response, "data") else []
            if not data:
                return None

            row = data[0]
            created_at_str = row.get("created_at")
            updated_at_str = row.get("updated_at")

            created_at = (
                datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_at_str
                else datetime.now(timezone.utc)
            )
            updated_at = (
                datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                if updated_at_str
                else datetime.now(timezone.utc)
            )
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)

            cid = str(row.get("id"))
            count = 0
            try:
                counts = await self._get_server_counts_for_clusters([cid])
                count = counts.get(cid, 0)
            except Exception:
                pass

            return DirectoryCluster(
                id=cid,
                name=str(row.get("name")),
                slug=str(row.get("slug")),
                visibility=row.get("visibility"),
                created_at=created_at,
                updated_at=updated_at,
                server_count=count,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to query clusters by slug {slug}: {str(e)}"
            ) from e
