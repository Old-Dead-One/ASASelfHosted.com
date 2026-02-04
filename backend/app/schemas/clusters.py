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


class AgentConfigResponse(BaseSchema):
    """Agent config for a cluster (owner-only). Used by local agent to know key_version and grace."""

    cluster_id: str
    key_version: int
    heartbeat_grace_seconds: int | None = None
    min_agent_version: str | None = None  # From app config; agent should upgrade if below


class ClusterServerItem(BaseSchema):
    """Minimal server info for agent import (list servers in cluster)."""

    id: str  # server_id
    name: str
    map_name: str | None = None


class AssignAllServersResponse(BaseSchema):
    """Result of assigning the owner's servers to a cluster."""

    cluster_id: str
    dry_run: bool = False
    only_unclustered: bool = False
    total_owner_servers: int
    already_in_cluster: int
    unclustered: int
    in_other_cluster: int
    would_change: int
