"""
Heartbeat repository interface.

Abstract interface for heartbeat persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.heartbeat import HeartbeatRequest


class HeartbeatCreateResult:
    """Result of heartbeat creation operation."""

    def __init__(self, inserted: bool, replay: bool):
        self.inserted = inserted  # True if new heartbeat was inserted
        self.replay = replay  # True if heartbeat_id was duplicate (replay)


class HeartbeatRepository(ABC):
    """
    Abstract repository for heartbeat persistence.

    Implementations:
    - SupabaseHeartbeatRepository: Real Supabase inserts (Sprint 4+)
    """

    @abstractmethod
    async def create_heartbeat(
        self,
        req: HeartbeatRequest,
        received_at: datetime,
        server_cluster_id: str | None = None,
    ) -> HeartbeatCreateResult:
        """
        Insert heartbeat append-only.

        Args:
            req: HeartbeatRequest from agent
            received_at: Server timestamp when heartbeat was received
            server_cluster_id: Optional cluster_id (can derive from server if needed)

        Returns:
            HeartbeatCreateResult with:
            - inserted: bool (True if new, False if replay)
            - replay: bool (True if heartbeat_id duplicate)

        Raises:
            RuntimeError: If heartbeat insertion fails (other than replay)
        """
        ...
