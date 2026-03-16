"""
Observed status repository interface.

Handles:
- Enqueueing on-demand observed refresh work
- Claiming queued work for a worker
- Updating observed result fields on servers
- Reading observation config (owner-only)
"""

from abc import ABC, abstractmethod
from datetime import datetime


class ObservedRefreshJob(dict):
    """Typed alias for observed_refresh_queue rows (minimal)."""


class ObservedRepository(ABC):
    @abstractmethod
    async def enqueue_refresh(
        self,
        server_ids: list[str],
        requested_by_user_id: str | None,
        reason: str,
    ) -> tuple[int, int]:
        """
        Enqueue refresh jobs.

        Returns (queued, skipped_dupe) - freshness filtering handled in API layer.
        """

    @abstractmethod
    async def claim_jobs(self, batch_size: int) -> list[ObservedRefreshJob]:
        """Claim queued jobs for processing (claimed_at TTL strategy)."""

    @abstractmethod
    async def mark_done(self, job_id: str, processed_at: datetime) -> None:
        """Mark a job as done."""

    @abstractmethod
    async def mark_dropped(
        self, job_id: str, processed_at: datetime, error: str
    ) -> None:
        """Mark a job as dropped with an error string."""

    @abstractmethod
    async def get_server_observation_config(
        self, server_id: str
    ) -> dict | None:
        """Read observation config for a server (owner-only table)."""

    @abstractmethod
    async def update_observed_result(
        self,
        server_id: str,
        status: str | None,
        checked_at: datetime,
        latency_ms: int | None,
        error: str | None,
    ) -> None:
        """Update observed_* result fields on servers."""

