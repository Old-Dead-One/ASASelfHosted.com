"""
Favorites endpoints.

Handles favorite/unfavorite operations for servers.
"""

from fastapi import APIRouter, Depends, Request

from app.core.deps import extract_bearer_token, require_user
from app.core.errors import NotFoundError, UnauthorizedError
from app.core.security import UserIdentity
from app.db.providers import get_servers_repo
from app.db.servers_repo import ServersRepository
from app.schemas.base import SuccessResponse

router = APIRouter(prefix="/servers/{server_id}/favorites", tags=["favorites"])


@router.post("", response_model=SuccessResponse)
async def add_favorite(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Add server to favorites.

    Requires authentication.
    Users can favorite any server in the directory.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    from app.core.supabase import get_rls_client
    client = get_rls_client(token)
    
    # Verify server exists (check directory_view)
    repo = get_servers_repo(token)
    server = await repo.get_server(server_id)
    if not server:
        raise NotFoundError("server", server_id)
    
    # Insert favorite (RLS will enforce user_id)
    # Use upsert to handle duplicate gracefully
    result = (
        client.table("favorites")
        .upsert(
            {
                "user_id": user.user_id,
                "server_id": server_id,
            },
            on_conflict="user_id,server_id",
        )
        .execute()
    )
    
    if not result.data:
        raise RuntimeError("Failed to add favorite")
    
    return {"success": True}


@router.delete("", response_model=SuccessResponse)
async def remove_favorite(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Remove server from favorites.

    Requires authentication.
    """
    # Extract JWT token for RLS client
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")
    
    # Get RLS client
    from app.core.supabase import get_rls_client
    client = get_rls_client(token)
    
    # Delete favorite (RLS will enforce user_id)
    result = (
        client.table("favorites")
        .delete()
        .eq("user_id", user.user_id)
        .eq("server_id", server_id)
        .execute()
    )
    
    # Delete returns empty data on success
    # If no rows were deleted, the favorite didn't exist (but that's OK)
    return {"success": True}
