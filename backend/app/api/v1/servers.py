"""
Server endpoints.

Handles CRUD operations for ASA servers.
Consent-first: server data requires explicit consent.
"""

from fastapi import APIRouter

from app.schemas.directory import DirectoryResponse

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", response_model=DirectoryResponse)
async def list_servers():
    """
    List public servers from directory_view.

    Returns servers from directory_view (public read model).
    All servers are public by default.
    Password field is gated by favorites (handled by RLS).
    """
    # TODO: Implement server listing from directory_view
    # TODO: Add pagination
    # TODO: Add filtering (search, status, badges, etc.)
    return {
        "data": [],
        "total": 0,
        "page": 1,
        "page_size": 50,
    }


@router.get("/{server_id}")
async def get_server(server_id: str):
    """
    Get server details by ID.

    Returns server information if:
    - Server is public OR user has permission
    - Consent is valid
    """
    # TODO: Implement server retrieval with permission checks
    pass


@router.post("/")
async def create_server():
    """
    Create a new server listing.

    Requires:
    - Authenticated user
    - Server owner consent
    """
    # TODO: Implement server creation
    pass


@router.put("/{server_id}")
async def update_server(server_id: str):
    """
    Update server listing.

    Requires:
    - Authenticated user
    - User owns the server OR has permission
    """
    # TODO: Implement server update with ownership checks
    pass


@router.delete("/{server_id}")
async def delete_server(server_id: str):
    """
    Delete server listing.

    Requires:
    - Authenticated user
    - User owns the server
    """
    # TODO: Implement server deletion with ownership checks
    pass
