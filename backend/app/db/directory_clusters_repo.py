"""
Directory clusters repository interface.

Abstract interface for cluster read operations in the public directory.
Separate from DirectoryRepository to keep concerns separated.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from app.schemas.directory import ClusterVisibility, DirectoryCluster, SortOrder


class DirectoryClustersRepository(ABC):
    """
    Abstract repository for cluster directory read operations.
    
    Implementations:
    - MockDirectoryClustersRepository: Mock data for testing
    - SupabaseDirectoryClustersRepository: Real Supabase queries
    """

    @abstractmethod
    async def list_clusters(
        self,
        limit: int = 25,
        cursor: str | None = None,
        visibility: ClusterVisibility | None = None,  # Filter by visibility
        sort_by: str = "updated",  # "updated" or "name"
        order: SortOrder = "desc",
        now_utc: datetime | None = None,  # Request handling time for consistency
    ) -> tuple[Sequence[DirectoryCluster], str | None]:
        """
        List clusters from directory with cursor pagination.
        
        Args:
            limit: Maximum number of items to return (default 25, max 100)
            cursor: Opaque cursor string for pagination (from previous response)
            visibility: Filter by visibility. Only "public" is supported; "unlisted" is rejected.
            sort_by: Sort key ("updated" or "name")
            order: Sort order (asc/desc)
            now_utc: Request handling time for consistency (must be consistent across response)
            
        Returns:
            Tuple of (cluster list, next_cursor). next_cursor is None if no more results.
            
        Visibility Rules (public directory):
            - public-only exposure. Unlisted clusters are not accessible via directory endpoints.
            - list: returns only public clusters
            - get by id: returns only if cluster is public (unlisted → 404)
        """
        ...

    @abstractmethod
    async def get_cluster(
        self,
        cluster_id: str,
        now_utc: datetime | None = None,
    ) -> DirectoryCluster | None:
        """
        Get cluster by ID.
        
        Args:
            cluster_id: Cluster UUID
            now_utc: Request handling time for consistency
            
        Returns:
            DirectoryCluster if found and public, None otherwise.
            Unlisted clusters return None (public directory is public-only).
        """
        ...
