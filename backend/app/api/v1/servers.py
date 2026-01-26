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

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_optional_user, require_user
from app.core.security import UserIdentity
from app.schemas.base import SuccessResponse
from app.schemas.directory import DirectoryResponse
from app.schemas.servers import (
    ServerCreateRequest,
    ServerOwnerResponse,
    ServerPublicResponse,
    ServerUpdateRequest,
)

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", response_model=DirectoryResponse)
async def list_servers(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        default=50, ge=1, le=100, description="Items per page (max 100)"
    ),
    q: str | None = Query(
        default=None, description="Search query (server name, description)"
    ),
    status: Literal["online", "offline", "unknown"] | None = Query(
        default=None, description="Filter by server status"
    ),
    mode: Literal["manual", "verified"] | None = Query(
        default=None, description="Filter by verification mode"
    ),
    user: UserIdentity | None = Depends(get_optional_user),
):
    """
    List public servers from directory_view.

    Public endpoint - no authentication required.
    Returns servers from directory_view (public read model).

    Pagination and filtering are supported.
    Search, status, and verification mode filters are optional.
    """
    # TODO: Implement server listing from directory_view
    # TODO: Implement pagination
    # TODO: Implement filtering (search, status, badges, etc.)
    # TODO: Use user context for personalized data (favorites, etc.)
    return {
        "data": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{server_id}", response_model=ServerPublicResponse)
async def get_server(
    server_id: str,
    user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Get server details by ID.

    Public endpoint - returns server if it's public.
    If user is authenticated and owns the server, returns owner view.
    """
    # TODO: Implement server retrieval
    # TODO: Check if server is public or user has permission
    # TODO: Return owner view if user owns the server
    from app.core.errors import NotFoundError

    raise NotFoundError("server", server_id)


@router.post("/", response_model=ServerOwnerResponse)
async def create_server(
    server_data: ServerCreateRequest,
    user: UserIdentity = Depends(require_user),
):
    """
    Create a new server listing.

    Requires authentication.
    Creates a server owned by the authenticated user.
    """
    # TODO: Implement server creation
    # TODO: Set owner_user_id to user.id
    # TODO: Validate server data
    # TODO: Insert into servers table
    from app.core.errors import DomainValidationError

    raise DomainValidationError("Server creation not yet implemented")


@router.put("/{server_id}", response_model=ServerOwnerResponse)
async def update_server(
    server_id: str,
    server_data: ServerUpdateRequest,
    user: UserIdentity = Depends(require_user),
):
    """
    Update server listing.

    Requires authentication and ownership.
    Only the server owner can update their server.
    """
    # TODO: Implement server update
    # TODO: Verify user owns the server
    # TODO: Update server fields
    from app.core.errors import DomainValidationError

    raise DomainValidationError("Server update not yet implemented")


@router.delete("/{server_id}", response_model=SuccessResponse)
async def delete_server(
    server_id: str,
    user: UserIdentity = Depends(require_user),
):
    """
    Delete server listing.

    Requires authentication and ownership.
    Only the server owner can delete their server.
    """
    # TODO: Implement server deletion
    # TODO: Verify user owns the server
    # TODO: Soft delete or hard delete based on requirements
    return {"success": True}
