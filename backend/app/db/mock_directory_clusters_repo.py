"""
Mock directory clusters repository for local development and testing.

Returns mock cluster data matching DirectoryCluster schema.
This allows hermetic tests and local development without Supabase.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

from app.core.errors import DomainValidationError
from app.db.directory_clusters_repo import DirectoryClustersRepository
from app.schemas.directory import ClusterVisibility, DirectoryCluster, SortOrder
from app.utils.cursor import create_cursor, parse_cursor

_NOW = datetime.now(timezone.utc)

# Mock clusters matching DirectoryCluster schema
# Note: ClusterVisibility is a Literal["public", "unlisted"], not an Enum
MOCK_CLUSTERS: list[DirectoryCluster] = [
    DirectoryCluster(
        id="cluster-001",
        name="Sun Bros Cluster",
        slug="sun-bros",
        visibility="public",  # ClusterVisibility is Literal["public", "unlisted"]
        created_at=_NOW - timedelta(days=30),
        updated_at=_NOW - timedelta(hours=2),
        server_count=3,
    ),
    DirectoryCluster(
        id="cluster-002",
        name="Ark Survival Community",
        slug="ark-survival-community",
        visibility="public",
        created_at=_NOW - timedelta(days=60),
        updated_at=_NOW - timedelta(hours=5),
        server_count=5,
    ),
    DirectoryCluster(
        id="cluster-003",
        name="Private Test Cluster",
        slug="private-test",
        visibility="unlisted",
        created_at=_NOW - timedelta(days=10),
        updated_at=_NOW - timedelta(days=1),
        server_count=1,
    ),
]


class MockDirectoryClustersRepository(DirectoryClustersRepository):
    """Mock implementation of DirectoryClustersRepository for testing and local development."""

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
        List clusters with cursor pagination.

        Args:
            limit: Maximum items to return (max 100)
            cursor: Opaque cursor for pagination
            visibility: Filter by visibility (public/unlisted)
            sort_by: Sort key ("updated" or "name")
            order: Sort order (asc/desc)
            now_utc: Current UTC time (for seconds_since_seen computation)

        Returns:
            Tuple of (clusters list, next_cursor string or None)
        """
        if limit > 100:
            raise DomainValidationError(f"limit must be <= 100, got {limit}")

        # Parse and validate cursor
        parsed_cursor = None
        if cursor:
            parsed_cursor = parse_cursor(cursor)
            if parsed_cursor:
                parsed_cursor.validate_match(sort_by, order)

        # Filter by visibility
        # Reject unlisted: public directory is public-only
        if visibility == "unlisted":
            raise DomainValidationError(
                "Unlisted clusters are not accessible via public directory. Only 'public' is supported."
            )

        filtered_clusters = list(MOCK_CLUSTERS)
        if visibility is not None:
            # visibility is "public" (unlisted already rejected above)
            filtered_clusters = [
                c for c in filtered_clusters if c.visibility == visibility
            ]
        else:
            # Default: public only
            filtered_clusters = [
                c for c in filtered_clusters if c.visibility == "public"
            ]

        # Sort clusters
        def _get_sort_value(cluster: DirectoryCluster, sort_key: str) -> Any:
            """Get sort value for a cluster."""
            if sort_key == "updated":
                return cluster.updated_at
            elif sort_key == "name":
                return cluster.name.lower()
            else:
                # Default to updated_at
                return cluster.updated_at

        # Sort by sort_key and id (tie-breaker)
        reverse = order == "desc"
        filtered_clusters.sort(
            key=lambda c: (_get_sort_value(c, sort_by), c.id), reverse=reverse
        )

        # Apply cursor seek predicate
        if parsed_cursor:
            cursor_last_value = parsed_cursor.last_value
            cursor_last_id = parsed_cursor.last_id

            # Filter based on cursor (seek predicate)
            seeked_clusters = []
            for cluster in filtered_clusters:
                sort_value = _get_sort_value(cluster, sort_by)
                cluster_id = cluster.id

                if order == "desc":
                    # DESC: skip if sort_value > last_value, or (sort_value == last_value and id >= last_id)
                    if sort_value > cursor_last_value:
                        continue
                    if sort_value == cursor_last_value and cluster_id >= cursor_last_id:
                        continue
                else:
                    # ASC: skip if sort_value < last_value, or (sort_value == last_value and id <= last_id)
                    if sort_value < cursor_last_value:
                        continue
                    if sort_value == cursor_last_value and cluster_id <= cursor_last_id:
                        continue

                seeked_clusters.append(cluster)

            filtered_clusters = seeked_clusters

        # Take limit + 1 to detect next page
        has_next = len(filtered_clusters) > limit
        paginated_clusters = filtered_clusters[:limit]

        # Generate next_cursor if there are more results
        next_cursor = None
        if has_next and paginated_clusters:
            last_cluster = paginated_clusters[-1]
            last_sort_value = _get_sort_value(last_cluster, sort_by)
            next_cursor = create_cursor(
                sort_by=sort_by,
                order=order,
                last_value=last_sort_value,
                last_id=last_cluster.id,
            )

        return paginated_clusters, next_cursor

    async def get_cluster(
        self,
        cluster_id: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """
        Get a single cluster by ID.

        Args:
            cluster_id: Cluster UUID
            now_utc: Current UTC time (for seconds_since_seen computation, not used for clusters)

        Returns:
            DirectoryCluster if found, None otherwise
        """
        for cluster in MOCK_CLUSTERS:
            if cluster.id == cluster_id:
                return cluster
        return None

    async def get_cluster_by_slug(
        self,
        slug: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """Get a single cluster by slug (public directory). Returns None if not found or unlisted."""
        for cluster in MOCK_CLUSTERS:
            if cluster.slug == slug and cluster.visibility == "public":
                return cluster
        return None
