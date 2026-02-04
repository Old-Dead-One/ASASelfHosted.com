"""
Ingest rejections repository interface.

Sprint 8: Audit trail for rejected ingest (heartbeat, etc.). No PII.
"""

from abc import ABC, abstractmethod
from typing import Any


class IngestRejectionsRepository(ABC):
    """
    Abstract repository for recording ingest rejections.

    Implementations write to ingest_rejections table (service_role only).
    """

    @abstractmethod
    async def record_rejection(
        self,
        server_id: str | None,
        rejection_reason: str,
        agent_version: str | None = None,
        metadata: dict[str, Any] | None = None,
        event_type: str = "server.heartbeat.v1",
    ) -> None:
        """
        Record a rejected ingest for audit.

        Args:
            server_id: Server UUID when known; None for malformed payload (body unparseable).
            rejection_reason: One of the violation classes (e.g. invalid_signature, consent_denied).
            agent_version: Optional agent version string.
            metadata: Optional JSON-serializable dict; must not contain PII.
            event_type: Event type (e.g. server.heartbeat.v1).
        """
        ...
