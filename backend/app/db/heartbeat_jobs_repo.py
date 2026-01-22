"""
Heartbeat jobs repository interface.

Abstract interface for durable queue operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypedDict


class HeartbeatJob(TypedDict):
    """Heartbeat job record."""
    
    id: str
    server_id: str
    enqueued_at: datetime
    processed_at: datetime | None
    attempts: int
    last_error: str | None


class HeartbeatJobsRepository(ABC):
    """
    Abstract repository for heartbeat job queue operations.
    
    Implementations:
    - SupabaseHeartbeatJobsRepository: Table-based durable queue (Sprint 4+)
    """

    @abstractmethod
    async def enqueue_server(self, server_id: str) -> None:
        """
        Enqueue a server for heartbeat processing.
        
        If a pending job already exists for this server, update it (idempotent).
        Otherwise, create a new job.
        
        Args:
            server_id: Server UUID to enqueue
        """
        ...

    @abstractmethod
    async def claim_jobs(self, batch_size: int) -> list[HeartbeatJob]:
        """
        Claim pending jobs for processing.
        
        Selects pending jobs (processed_at IS NULL) ordered by enqueued_at,
        and increments attempts immediately (claiming them).
        
        Args:
            batch_size: Maximum number of jobs to claim
            
        Returns:
            List of claimed HeartbeatJob records
        """
        ...

    @abstractmethod
    async def mark_processed(self, job_id: str, processed_at: datetime) -> None:
        """
        Mark a job as successfully processed.
        
        Args:
            job_id: Job UUID
            processed_at: Timestamp when processing completed
        """
        ...

    @abstractmethod
    async def mark_failed(self, job_id: str, error: str, attempts: int) -> None:
        """
        Mark a job as failed (keep pending for retry).
        
        Args:
            job_id: Job UUID
            error: Error message
            attempts: Current attempt count (will be incremented)
        """
        ...
