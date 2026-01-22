"""
Servers derived state repository interface.

Abstract interface for updating server derived state (status, confidence, uptime, quality).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypedDict

from app.schemas.directory import ServerStatus


class ServerClusterInfo(TypedDict):
    """Server cluster information for engine processing."""
    
    cluster_id: str | None
    key_version: int
    heartbeat_grace_seconds: int | None
    public_key_ed25519: str | None


class Heartbeat(TypedDict):
    """Heartbeat record from database."""
    
    id: str
    server_id: str
    received_at: datetime
    status: ServerStatus
    map_name: str | None
    players_current: int | None
    players_capacity: int | None
    agent_version: str | None
    key_version: int | None


class DerivedServerState(TypedDict):
    """Derived server state to update."""
    
    effective_status: ServerStatus
    confidence: str  # "green", "yellow", "red"
    uptime_percent: float | None
    quality_score: float | None
    players_current: int | None
    players_capacity: int | None
    last_heartbeat_at: datetime | None


class ServersDerivedRepository(ABC):
    """
    Abstract repository for server derived state operations.
    
    Implementations:
    - SupabaseServersDerivedRepository: Real Supabase queries/updates (Sprint 4+)
    """

    @abstractmethod
    async def get_server_cluster_and_grace(self, server_id: str) -> ServerClusterInfo | None:
        """
        Get server cluster information and grace window.
        
        Args:
            server_id: Server UUID
            
        Returns:
            ServerClusterInfo if server found, None otherwise
        """
        ...

    @abstractmethod
    async def get_recent_heartbeats(self, server_id: str, limit: int) -> list[Heartbeat]:
        """
        Get recent heartbeats for a server.
        
        Args:
            server_id: Server UUID
            limit: Maximum number of heartbeats to return
            
        Returns:
            List of Heartbeat records, ordered by received_at DESC (most recent first)
        """
        ...

    @abstractmethod
    async def update_derived_state(
        self,
        server_id: str,
        state: DerivedServerState
    ) -> None:
        """
        Update server derived state.
        
        Updates:
        - effective_status
        - confidence
        - uptime_percent
        - quality_score
        - players_current, players_capacity
        - last_heartbeat_at
        
        Does NOT update is_verified (listing trust flag, separate concern).
        
        Args:
            server_id: Server UUID
            state: DerivedServerState to apply
        """
        ...
