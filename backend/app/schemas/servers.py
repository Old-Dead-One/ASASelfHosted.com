"""
Server schemas.

Pydantic models for server-related requests and responses.
"""

from app.schemas.base import BaseSchema
from app.schemas.directory import DirectoryServer

# Type aliases for clarity
# Public responses use DirectoryServer (directory_view provides persisted fields; backend adds rank fields)
ServerPublicResponse = DirectoryServer

# Owner responses also use DirectoryServer for now
# TODO: Extend with owner-only fields (private notes, verification keys, etc.)
ServerOwnerResponse = DirectoryServer


class ServerCreateRequest(BaseSchema):
    """Schema for creating a new server."""

    name: str
    description: str | None = None
    # TODO: Add all required server fields (ip_address, port_game, etc.)


class ServerUpdateRequest(BaseSchema):
    """Schema for updating a server."""

    name: str | None = None
    description: str | None = None
    # TODO: Add updatable server fields
