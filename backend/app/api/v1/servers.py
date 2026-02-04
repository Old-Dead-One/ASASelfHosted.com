"""
Server endpoints.

Handles CRUD operations for ASA servers.

Public server listings do not require consent - they are public directory entries.
Consent applies to:
- Automated data collection (heartbeats, telemetry)
- Player-related data (hashed IDs, session tracking)
- Verified telemetry beyond basic status

Server passwords are not stored in Sprint 0.
If stored later, they will be encrypted and only returned to the server owner.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request

from datetime import datetime, timezone

from app.core.crypto import generate_ed25519_key_pair
from app.core.deps import extract_bearer_token, get_optional_user, require_user
from app.core.limits import get_effective_limits
from app.core.errors import APIError, NotFoundError, UnauthorizedError
from app.core.security import UserIdentity
from app.core.supabase import get_rls_client
from app.db.providers import get_servers_repo
from app.db.servers_repo import ServersRepository
from app.schemas.base import SuccessResponse
from app.schemas.directory import DirectoryResponse
from app.schemas.servers import (
    MyServersResponse,
    ServerAgentKeyStatusResponse,
    ServerCreateRequest,
    ServerKeyPairResponse,
    ServerOwnerResponse,
    ServerPublicResponse,
    ServerUpdateRequest,
)

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", response_model=MyServersResponse)
async def list_owner_servers(
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    List servers owned by the authenticated user.

    Requires authentication.
    Returns all servers owned by the user (different from public directory).
    Uses page-based pagination format for frontend compatibility.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get servers repository with RLS client
    repo = get_servers_repo(token)
    
    # List owner's servers
    servers = await repo.list_owner_servers(user.user_id)
    
    # Frontend expects page-based format for owner's servers (different from directory)
    # Match the MyServersResponse interface: { data, total, page, page_size }
    return {
        "data": list(servers),
        "total": len(servers),
        "page": 1,
        "page_size": len(servers),
    }


@router.get(
    "/{server_id}/agent-key-status",
    response_model=ServerAgentKeyStatusResponse,
)
async def get_server_agent_key_status(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Get agent key status for a server (owner-only).

    Returns key_version and whether a public key is set for this server.
    When has_key is true, heartbeats are verified with this server's key; otherwise the cluster key is used.
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    repo = get_servers_repo(token)
    server = await repo.get_server(server_id, user.user_id)
    if not server:
        raise NotFoundError("server", server_id)
    client = get_rls_client(token)
    row = (
        client.table("servers")
        .select("public_key_ed25519,key_version")
        .eq("id", server_id)
        .limit(1)
        .execute()
    )
    if not row.data or len(row.data) == 0:
        raise NotFoundError("server", server_id)
    data = row.data[0]
    pub = data.get("public_key_ed25519")
    return ServerAgentKeyStatusResponse(
        server_id=server_id,
        key_version=data.get("key_version", 1),
        has_key=bool(pub),
    )


@router.post(
    "/{server_id}/generate-keys",
    response_model=ServerKeyPairResponse,
)
async def generate_server_keys(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Generate Ed25519 key pair for a server (owner-only).

    Stores the public key on the server; returns the private key once (for agent config).
    When a server has a key set, heartbeats are verified with this key instead of the cluster key.
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    repo = get_servers_repo(token)
    server = await repo.get_server(server_id, user.user_id)
    if not server:
        raise NotFoundError("server", server_id)
    client = get_rls_client(token)
    server_row = (
        client.table("servers")
        .select("key_version")
        .eq("id", server_id)
        .limit(1)
        .execute()
    )
    if not server_row.data or len(server_row.data) == 0:
        raise NotFoundError("server", server_id)
    current_key_version = server_row.data[0].get("key_version", 1)
    private_key_b64, public_key_b64 = generate_ed25519_key_pair()
    new_key_version = current_key_version + 1
    update_result = (
        client.table("servers")
        .update({
            "public_key_ed25519": public_key_b64,
            "key_version": new_key_version,
            "rotated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", server_id)
        .execute()
    )
    if not update_result.data or len(update_result.data) == 0:
        raise RuntimeError("Failed to update server with public key")
    return ServerKeyPairResponse(
        server_id=server_id,
        key_version=new_key_version,
        public_key=public_key_b64,
        private_key=private_key_b64,
    )


@router.get("/{server_id}", response_model=ServerPublicResponse)
async def get_server(
    server_id: str,
    request: Request,
    user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Get server details by ID.

    Public endpoint - returns server if it's public.
    If user is authenticated and owns the server, returns owner view.
    """
    # For public access, use directory endpoint instead
    # This endpoint is for owner-specific server retrieval
    # If user is authenticated, use RLS client
    if user:
        token = extract_bearer_token(request)
        if token:
            repo = get_servers_repo(token)
            server = await repo.get_server(server_id, user.user_id)
            if server:
                return server
    
    # Fallback: server not found or user not authenticated
    raise NotFoundError("server", server_id)


@router.post("/", response_model=ServerOwnerResponse)
async def create_server(
    server_data: ServerCreateRequest,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Create a new server listing.

    Requires authentication.
    Creates a server owned by the authenticated user.
    Enforces per-user server limit (may be overridden by admin per user).
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    servers_limit, _ = get_effective_limits(user.user_id)
    repo = get_servers_repo(token)
    count = await repo.count_owner_servers(user.user_id)
    if count >= servers_limit:
        raise APIError(
            message=f"You have reached the maximum number of servers ({servers_limit}). Delete a server to add another, or contact us to request a higher limit.",
            status_code=403,
            error_code="server_limit_reached",
        )

    server = await repo.create_server(user.user_id, server_data)
    return server


@router.put("/{server_id}", response_model=ServerOwnerResponse)
async def update_server(
    server_id: str,
    server_data: ServerUpdateRequest,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Update server listing.

    Requires authentication and ownership.
    Only the server owner can update their server.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get servers repository with RLS client
    repo = get_servers_repo(token)
    
    # Update server
    server = await repo.update_server(server_id, user.user_id, server_data)
    if not server:
        raise NotFoundError("server", server_id)
    
    return server


@router.delete("/{server_id}", response_model=SuccessResponse)
async def delete_server(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Delete server listing.

    Requires authentication and ownership.
    Only the server owner can delete their server.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get servers repository with RLS client
    repo = get_servers_repo(token)
    
    # Delete server
    deleted = await repo.delete_server(server_id, user.user_id)
    if not deleted:
        raise NotFoundError("server", server_id)
    
    return {"success": True}
