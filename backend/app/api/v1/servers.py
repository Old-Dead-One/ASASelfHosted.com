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

from app.core.deps import extract_bearer_token, get_optional_user, require_user
from app.core.errors import NotFoundError, UnauthorizedError
from app.core.security import UserIdentity
from app.db.providers import get_servers_repo
from app.db.servers_repo import ServersRepository
from app.schemas.base import SuccessResponse
from app.schemas.directory import DirectoryResponse
from app.schemas.servers import (
    MyServersResponse,
    ServerCreateRequest,
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
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get servers repository with RLS client
    repo = get_servers_repo(token)
    
    # Create server
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
