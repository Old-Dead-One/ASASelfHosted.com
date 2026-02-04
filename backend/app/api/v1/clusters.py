"""
Cluster endpoints.

Handles operations for server clusters.
Clusters group multiple server instances together.
"""

from fastapi import APIRouter, Depends, Query, Request

from app.core.deps import extract_bearer_token, require_user
from app.core.errors import APIError, NotFoundError, UnauthorizedError
from app.core.limits import get_effective_limits
from app.core.security import UserIdentity
from app.core.supabase import get_rls_client, get_supabase_admin
from app.core.crypto import generate_ed25519_key_pair
from app.schemas.base import SuccessResponse
from app.core.config import get_settings
from app.schemas.clusters import (
    AgentConfigResponse,
    AssignAllServersResponse,
    ClusterCreateRequest,
    ClusterResponse,
    ClusterServerItem,
    ClusterUpdateRequest,
    KeyPairResponse,
)

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.post("/", response_model=ClusterResponse)
async def create_cluster(
    cluster_data: ClusterCreateRequest,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Create a new cluster.

    Requires authentication.
    Creates a cluster owned by the authenticated user.
    Enforces per-user cluster limit (default 1; admin can override per user).
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    _, clusters_limit = get_effective_limits(user.user_id)
    admin = get_supabase_admin()
    clusters_used = 0
    if admin:
        try:
            r = (
                admin.table("clusters")
                .select("id")
                .eq("owner_user_id", user.user_id)
                .execute()
            )
            clusters_used = len(r.data) if r.data else 0
        except Exception:
            pass
    if clusters_used >= clusters_limit:
        raise APIError(
            message=f"You have reached the maximum number of clusters ({clusters_limit}). Delete a cluster to add another, or contact us to request a higher limit.",
            status_code=403,
            error_code="cluster_limit_reached",
        )

    client = get_rls_client(token)

    # Generate slug from name if not provided
    slug = cluster_data.slug
    if not slug:
        # Simple slug generation: lowercase, replace spaces with hyphens, remove special chars
        slug = cluster_data.name.lower().replace(" ", "-")
        # Remove non-alphanumeric except hyphens
        slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)
        # Remove consecutive hyphens
        while "--" in slug:
            slug = slug.replace("--", "-")
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
    
    # Insert cluster
    insert_data = {
        "owner_user_id": user.user_id,
        "name": cluster_data.name.strip(),
        "slug": slug,
        "visibility": cluster_data.visibility,
        "key_version": 1,  # Start at version 1
    }
    
    result = (
        client.table("clusters")
        .insert(insert_data)
        .execute()
    )
    
    if not result.data or len(result.data) == 0:
        raise RuntimeError("Failed to create cluster")
    
    # Return cluster response
    cluster = result.data[0]
    return ClusterResponse(
        id=cluster["id"],
        name=cluster["name"],
        slug=cluster["slug"],
        owner_user_id=cluster["owner_user_id"],
        visibility=cluster["visibility"],
        key_version=cluster["key_version"],
        public_fingerprint=cluster.get("public_fingerprint"),
        public_key_ed25519=cluster.get("public_key_ed25519"),
        heartbeat_grace_seconds=cluster.get("heartbeat_grace_seconds"),
        rotated_at=cluster.get("rotated_at"),
        created_at=cluster["created_at"],
        updated_at=cluster["updated_at"],
    )


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(
    cluster_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Get cluster details by ID.

    Requires authentication and ownership.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    client = get_rls_client(token)
    
    # Get cluster (RLS will enforce ownership)
    result = (
        client.table("clusters")
        .select("*")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)  # Extra ownership check
        .limit(1)
        .execute()
    )
    
    if not result.data or len(result.data) == 0:
        raise NotFoundError("cluster", cluster_id)
    
    cluster = result.data[0]
    return ClusterResponse(
        id=cluster["id"],
        name=cluster["name"],
        slug=cluster["slug"],
        owner_user_id=cluster["owner_user_id"],
        visibility=cluster["visibility"],
        key_version=cluster["key_version"],
        public_fingerprint=cluster.get("public_fingerprint"),
        public_key_ed25519=cluster.get("public_key_ed25519"),
        heartbeat_grace_seconds=cluster.get("heartbeat_grace_seconds"),
        rotated_at=cluster.get("rotated_at"),
        created_at=cluster["created_at"],
        updated_at=cluster["updated_at"],
    )


@router.get("/{cluster_id}/agent-config", response_model=AgentConfigResponse)
async def get_cluster_agent_config(
    cluster_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Get agent config for a cluster (key_version, grace window, min_agent_version).

    Owner-only. Used by local agent UI so it knows what key_version to send and whether to upgrade.
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    client = get_rls_client(token)
    result = (
        client.table("clusters")
        .select("id,key_version,heartbeat_grace_seconds")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .limit(1)
        .execute()
    )
    if not result.data or len(result.data) == 0:
        raise NotFoundError("cluster", cluster_id)
    cluster = result.data[0]
    settings = get_settings()
    return AgentConfigResponse(
        cluster_id=str(cluster["id"]),
        key_version=int(cluster["key_version"]),
        heartbeat_grace_seconds=cluster.get("heartbeat_grace_seconds"),
        min_agent_version=settings.MIN_AGENT_VERSION,
    )


@router.get("/{cluster_id}/servers", response_model=list[ClusterServerItem])
async def list_cluster_servers(
    cluster_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    List servers in a cluster (owner-only).

    Returns minimal server info for agent import (server_id, name, map_name).
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    client = get_rls_client(token)
    # Verify cluster ownership
    cluster_result = (
        client.table("clusters")
        .select("id")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .limit(1)
        .execute()
    )
    if not cluster_result.data or len(cluster_result.data) == 0:
        raise NotFoundError("cluster", cluster_id)
    # List servers in this cluster (RLS returns only owner's servers)
    servers_result = (
        client.table("servers")
        .select("id,name,map_name")
        .eq("cluster_id", cluster_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [
        ClusterServerItem(
            id=str(row["id"]),
            name=str(row.get("name") or ""),
            map_name=row.get("map_name"),
        )
        for row in (servers_result.data or [])
    ]


@router.put("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(
    cluster_id: str,
    cluster_data: ClusterUpdateRequest,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Update cluster.

    Requires authentication and ownership.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    client = get_rls_client(token)
    
    # Prepare update data
    update_data: dict = {}
    if cluster_data.name is not None:
        update_data["name"] = cluster_data.name.strip()
    if cluster_data.slug is not None:
        update_data["slug"] = cluster_data.slug.strip()
    if cluster_data.visibility is not None:
        update_data["visibility"] = cluster_data.visibility
    
    if not update_data:
        # No fields to update, return existing cluster
        return await get_cluster(cluster_id, request, user)
    
    # Update cluster (RLS will enforce ownership)
    result = (
        client.table("clusters")
        .update(update_data)
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .execute()
    )
    
    if not result.data or len(result.data) == 0:
        raise NotFoundError("cluster", cluster_id)
    
    cluster = result.data[0]
    return ClusterResponse(
        id=cluster["id"],
        name=cluster["name"],
        slug=cluster["slug"],
        owner_user_id=cluster["owner_user_id"],
        visibility=cluster["visibility"],
        key_version=cluster["key_version"],
        public_fingerprint=cluster.get("public_fingerprint"),
        public_key_ed25519=cluster.get("public_key_ed25519"),
        heartbeat_grace_seconds=cluster.get("heartbeat_grace_seconds"),
        rotated_at=cluster.get("rotated_at"),
        created_at=cluster["created_at"],
        updated_at=cluster["updated_at"],
    )


@router.post("/{cluster_id}/generate-keys", response_model=KeyPairResponse)
async def generate_cluster_keys(
    cluster_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Generate Ed25519 key pair for cluster agent authentication.

    Requires authentication and ownership.
    Returns key pair (public key stored, private key shown once).
    
    Note: Private key should be saved immediately - it won't be shown again.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    client = get_rls_client(token)
    
    # Verify cluster exists and user owns it
    cluster_result = (
        client.table("clusters")
        .select("*")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .limit(1)
        .execute()
    )
    
    if not cluster_result.data or len(cluster_result.data) == 0:
        raise NotFoundError("cluster", cluster_id)
    
    cluster = cluster_result.data[0]
    current_key_version = cluster.get("key_version", 1)
    
    # Generate new key pair
    private_key_b64, public_key_b64 = generate_ed25519_key_pair()
    
    # Increment key version
    new_key_version = current_key_version + 1
    
    # Update cluster with public key and new key version
    from datetime import datetime, timezone
    
    update_result = (
        client.table("clusters")
        .update({
            "public_key_ed25519": public_key_b64,
            "key_version": new_key_version,
            "rotated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .execute()
    )
    
    if not update_result.data or len(update_result.data) == 0:
        raise RuntimeError("Failed to update cluster with public key")
    
    # Return key pair (private key shown once)
    return KeyPairResponse(
        cluster_id=cluster_id,
        key_version=new_key_version,
        public_key=public_key_b64,
        private_key=private_key_b64,
    )


@router.post("/{cluster_id}/assign-all-servers", response_model=AssignAllServersResponse)
async def assign_all_servers_to_cluster(
    cluster_id: str,
    request: Request,
    dry_run: bool = Query(False),
    only_unclustered: bool = Query(False),
    user: UserIdentity = Depends(require_user),
):
    """
    Assign all of the authenticated user's servers to this cluster.

    Owner-only. Uses RLS client and verifies cluster ownership.

    Query params:
      - dry_run: if true, return counts only (no update)
      - only_unclustered: if true, only assign servers with cluster_id IS NULL
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    client = get_rls_client(token)

    # Verify cluster exists and user owns it
    check = (
        client.table("clusters")
        .select("id")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .limit(1)
        .execute()
    )
    if not check.data or len(check.data) == 0:
        raise NotFoundError("cluster", cluster_id)

    # Load all owner's servers (small limits, safe to compute in Python)
    servers_result = (
        client.table("servers")
        .select("id,cluster_id")
        .eq("owner_user_id", user.user_id)
        .execute()
    )
    rows = servers_result.data or []
    total_owner_servers = len(rows)
    already_in_cluster = sum(1 for r in rows if r.get("cluster_id") == cluster_id)
    unclustered = sum(1 for r in rows if r.get("cluster_id") is None)
    in_other_cluster = sum(
        1
        for r in rows
        if r.get("cluster_id") is not None and r.get("cluster_id") != cluster_id
    )
    if only_unclustered:
        would_change = unclustered
    else:
        would_change = total_owner_servers - already_in_cluster

    if not dry_run:
        # Apply update
        q = client.table("servers").update({"cluster_id": cluster_id}).eq(
            "owner_user_id", user.user_id
        )
        if only_unclustered:
            q = q.is_("cluster_id", "null")
        q.execute()

    return AssignAllServersResponse(
        cluster_id=cluster_id,
        dry_run=dry_run,
        only_unclustered=only_unclustered,
        total_owner_servers=total_owner_servers,
        already_in_cluster=already_in_cluster,
        unclustered=unclustered,
        in_other_cluster=in_other_cluster,
        would_change=would_change,
    )


@router.get("/", response_model=list[ClusterResponse])
async def list_owner_clusters(
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    List clusters owned by the authenticated user.

    Requires authentication.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    client = get_rls_client(token)
    
    # List owner's clusters (RLS will enforce ownership)
    result = (
        client.table("clusters")
        .select("*")
        .eq("owner_user_id", user.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    
    clusters = []
    for cluster in result.data or []:
        clusters.append(
            ClusterResponse(
                id=cluster["id"],
                name=cluster["name"],
                slug=cluster["slug"],
                owner_user_id=cluster["owner_user_id"],
                visibility=cluster["visibility"],
                key_version=cluster["key_version"],
                public_fingerprint=cluster.get("public_fingerprint"),
                public_key_ed25519=cluster.get("public_key_ed25519"),
                heartbeat_grace_seconds=cluster.get("heartbeat_grace_seconds"),
                rotated_at=cluster.get("rotated_at"),
                created_at=cluster["created_at"],
                updated_at=cluster["updated_at"],
            )
        )
    
    return clusters


@router.delete("/{cluster_id}", status_code=204)
async def delete_cluster(
    cluster_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Delete a cluster owned by the authenticated user.

    Requires authentication and ownership. Servers that were in this cluster
    keep their data but cluster_id is set to null (DB ON DELETE SET NULL).
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    client = get_rls_client(token)
    # Verify cluster exists and user owns it before deleting
    check = (
        client.table("clusters")
        .select("id")
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .limit(1)
        .execute()
    )
    if not check.data or len(check.data) == 0:
        raise NotFoundError("cluster", cluster_id)

    (
        client.table("clusters")
        .delete()
        .eq("id", cluster_id)
        .eq("owner_user_id", user.user_id)
        .execute()
    )
    return None  # 204 No Content
