"""
Cluster schemas.

Pydantic models for cluster-related requests and responses.
"""

from app.schemas.base import BaseSchema
from app.schemas.directory import ClusterVisibility


class ClusterResponse(BaseSchema):
    """Cluster response schema."""

    id: str
    name: str
    slug: str
    owner_user_id: str
    visibility: ClusterVisibility
    key_version: int
    public_fingerprint: str | None = None
    public_key_ed25519: str | None = None  # Base64-encoded Ed25519 public key
    heartbeat_grace_seconds: int | None = None
    rotated_at: str | None = None  # ISO datetime string
    created_at: str  # ISO datetime string
    updated_at: str  # ISO datetime string


class ClusterCreateRequest(BaseSchema):
    """Schema for creating a new cluster."""

    name: str
    slug: str | None = None  # Auto-generated from name if not provided
    visibility: ClusterVisibility = "public"


class ClusterUpdateRequest(BaseSchema):
    """Schema for updating a cluster."""

    name: str | None = None
    slug: str | None = None
    visibility: ClusterVisibility | None = None


class KeyPairResponse(BaseSchema):
    """Response for key pair generation."""

    cluster_id: str
    key_version: int
    public_key: str  # Base64-encoded Ed25519 public key
    private_key: str  # Base64-encoded Ed25519 private key (one-time display)
    warning: str = (
        "⚠️ IMPORTANT: Save this private key now. "
        "It will not be shown again. You'll need it to configure your agent."
    )
