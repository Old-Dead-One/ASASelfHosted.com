"""
Supabase implementation of ingest rejections repository.

Sprint 8: Writes to ingest_rejections table using service_role.
"""

import logging
from typing import Any

from app.db.ingest_rejections_repo import IngestRejectionsRepository

logger = logging.getLogger(__name__)


class SupabaseIngestRejectionsRepository(IngestRejectionsRepository):
    """Write ingest rejections to Supabase (service_role)."""

    def __init__(self):
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None
        try:
            from app.core.supabase import get_supabase_admin

            self._supabase = get_supabase_admin()
            self._configured = self._supabase is not None
        except Exception as e:
            self._config_error = str(e)
            logger.warning("SupabaseIngestRejectionsRepository init failed: %s", e)

    async def record_rejection(
        self,
        server_id: str | None,
        rejection_reason: str,
        agent_version: str | None = None,
        metadata: dict[str, Any] | None = None,
        event_type: str = "server.heartbeat.v1",
    ) -> None:
        if not self._configured or self._supabase is None:
            logger.warning(
                "Ingest rejection not recorded: repo not configured (%s)",
                self._config_error,
            )
            return
        try:
            row: dict = {
                "server_id": server_id,  # None allowed for malformed_payload (migration 027)
                "rejection_reason": rejection_reason,
                "event_type": event_type,
            }
            if agent_version is not None:
                row["agent_version"] = agent_version
            if metadata is not None:
                row["metadata"] = metadata
            self._supabase.table("ingest_rejections").insert(row).execute()
        except Exception as e:
            logger.warning(
                "Failed to record ingest rejection (non-fatal): %s",
                e,
                extra={"server_id": server_id, "rejection_reason": rejection_reason},
            )
