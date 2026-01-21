"""
Cluster endpoints.

Handles operations for server clusters.
Clusters group multiple server instances together.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("/")
async def list_clusters():
    """
    List public clusters.

    Returns clusters with:
    - Valid verification
    - Public visibility
    - Owner consent
    """
    # TODO: Implement cluster listing
    return {"data": []}


@router.get("/{cluster_id}")
async def get_cluster(cluster_id: str):
    """
    Get cluster details by ID.
    """
    # TODO: Implement cluster retrieval
    from app.core.errors import NotFoundError

    raise NotFoundError("cluster", cluster_id)


@router.post("/")
async def create_cluster():
    """
    Create a new cluster.

    Requires:
    - Authenticated user
    - Cluster owner consent
    """
    # TODO: Implement cluster creation
    from app.core.errors import DomainValidationError

    raise DomainValidationError("Cluster creation not yet implemented")
