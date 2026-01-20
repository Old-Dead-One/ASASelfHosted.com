"""
Cluster schemas.

Pydantic models for cluster-related requests and responses.
"""

from app.schemas.base import BaseSchema


class ClusterCreate(BaseSchema):
    """Schema for creating a new cluster."""

    name: str
    description: str | None = None
    # TODO: Add all required cluster fields


class ClusterResponse(BaseSchema):
    """Schema for cluster response."""

    id: str
    name: str
    description: str | None = None
    # TODO: Add all cluster response fields
