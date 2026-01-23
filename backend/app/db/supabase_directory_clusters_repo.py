"""
Supabase directory clusters repository.

Read-only repository that queries clusters table in Supabase.
Implements DirectoryClustersRepository for public cluster directory access.
"""

from datetime import datetime, timezone
from typing import Sequence

from app.core.config import get_settings
from app.core.errors import DomainValidationError
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
    def _map_sort_by_to_column(sort_by: str) -> str:
        """
        Map sort_by parameter to database column name.
        
        Args:
            sort_by: Sort key parameter ("updated" or "name")
            
        Returns:
            Database column name for sorting
        """
        mapping = {
            "updated": "updated_at",
            "name": "name",
        }
        return mapping.get(sort_by, "updated_at")  # Default to updated_at

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
            - If visibility is "unlisted": return only unlisted clusters (requires explicit filter)
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

        # Apply visibility filter
        # Default: only public clusters (unless explicitly filtered)
        if visibility is None:
            # Default behavior: only public clusters appear in directory listings
            query = query.eq("visibility", "public")
        else:
            # Explicit filter: return clusters with specified visibility
            query = query.eq("visibility", visibility)

        # Apply cursor seek predicate
        cursor_last_value = None
        cursor_last_id = None
        if parsed_cursor:
            cursor_last_value = parsed_cursor.last_value
            cursor_last_id = parsed_cursor.last_id
            
            if cursor_last_value is None:
                # NULL handling: if last_value is NULL, we're past all NULLs
                query = query.not_.is_(sort_column, "null")
            else:
                # For DESC: fetch sort_key <= last_value (exact matches filtered in Python)
                # For ASC: fetch sort_key >= last_value (exact matches filtered in Python)
                if order == "desc":
                    query = query.lte(sort_column, cursor_last_value)
                else:
                    query = query.gte(sort_column, cursor_last_value)

        # SQL ordering with tie-break
        # ORDER BY sort_column, id (id always ASC for tie-break)
        if order == "asc":
            query = query.order(sort_column, desc=False).order("id", desc=False)
        else:
            query = query.order(sort_column, desc=True).order("id", desc=False)

        # Cursor pagination: fetch limit + 1 to detect if there's a next page
        query = query.limit(limit + 1)

        # Execute query
        try:
            response = query.execute()
        except Exception as e:
            raise RuntimeError(f"Failed to query clusters: {str(e)}") from e

        # Extract data
        data = response.data if hasattr(response, "data") else []
        
        # Filter out cursor boundary items (exact matches that should be excluded)
        if parsed_cursor and cursor_last_value is not None and cursor_last_id:
            filtered_data = []
            for row in data:
                sort_value = row.get(sort_column)
                row_id = row.get("id")
                
                # Skip items that match cursor exactly but should be excluded
                if sort_value == cursor_last_value:
                    if order == "desc":
                        # For DESC: exclude if id >= last_id
                        if row_id >= cursor_last_id:
                            continue
                    else:
                        # For ASC: exclude if id <= last_id
                        if row_id <= cursor_last_id:
                            continue
                
                filtered_data.append(row)
            data = filtered_data
        
        # Check if there's a next page (we fetched limit + 1)
        has_next = len(data) > limit
        if has_next:
            data = data[:limit]  # Keep only limit items
        
        # Convert to DirectoryCluster objects
        clusters: list[DirectoryCluster] = []
        last_row = None
        for row in data:
            try:
                # Parse timestamps
                created_at_str = row.get("created_at")
                updated_at_str = row.get("updated_at")
                
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc)
                updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")) if updated_at_str else datetime.now(timezone.utc)
                
                # Ensure timezone-aware
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                
                cluster = DirectoryCluster(
                    id=str(row.get("id")),
                    name=str(row.get("name")),
                    slug=str(row.get("slug")),
                    visibility=row.get("visibility"),  # Should be "public" or "unlisted"
                    created_at=created_at,
                    updated_at=updated_at,
                    server_count=0,  # TODO: Add server count if needed
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
                    raise RuntimeError(f"Failed to parse cluster row from clusters table: {e}") from e

        # Generate next_cursor if there are more results
        next_cursor = None
        if has_next and last_row:
            last_sort_value = last_row.get(sort_column)
            last_id = last_row.get("id")
            
            if last_id:
                next_cursor = create_cursor(sort_by, order, last_sort_value, last_id)

        return clusters, next_cursor

    async def get_cluster(
        self,
        cluster_id: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """
        Get cluster by ID from Supabase.
        
        Visibility Rules:
            - public: returns cluster (readable by everyone via RLS)
            - unlisted: returns cluster if found (RLS allows owners to read unlisted clusters)
            - private: does not exist in DB enum, so not applicable
        
        Note: Current RLS policy allows:
            - Public clusters: readable by everyone
            - Unlisted clusters: only readable by owners
        This means unlisted clusters will only be returned if the request is authenticated
        as the owner. For public directory access, unlisted clusters may not be accessible
        unless RLS policies are adjusted or service_role key is used.
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
            
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc)
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")) if updated_at_str else datetime.now(timezone.utc)
            
            # Ensure timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            
            cluster = DirectoryCluster(
                id=str(row.get("id")),
                name=str(row.get("name")),
                slug=str(row.get("slug")),
                visibility=row.get("visibility"),
                created_at=created_at,
                updated_at=updated_at,
                server_count=0,  # TODO: Add server count if needed
            )
            return cluster

        except Exception as e:
            raise RuntimeError(f"Failed to query clusters table for cluster {cluster_id}: {str(e)}") from e
