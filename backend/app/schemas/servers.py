"""
Server schemas.

Pydantic models for server-related requests and responses.
"""

from app.schemas.base import BaseSchema


class ServerCreate(BaseSchema):
    """Schema for creating a new server."""

    name: str
    description: str | None = None
    # TODO: Add all required server fields


class ServerUpdate(BaseSchema):
    """Schema for updating a server."""

    name: str | None = None
    description: str | None = None
    # TODO: Add updatable server fields


class ServerResponse(BaseSchema):
    """Schema for server response."""

    id: str
    name: str
    description: str | None = None
    verification_status: str
    # TODO: Add all server response fields
