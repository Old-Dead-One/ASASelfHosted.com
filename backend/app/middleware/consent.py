"""
Consent resolution layer.

Sprint 8: Single function that answers "Is this data allowed to be accepted right now?"
All ingest paths must call this before writing to storage.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Data types for ingest
DATA_TYPE_HEARTBEAT = "heartbeat"
# Future: DATA_TYPE_PLAYER_SESSION, etc.


def is_data_allowed_now(
    server_id: str,
    data_type: str,
    context: dict[str, Any] | None = None,
) -> bool:
    """
    Answer: Is this data allowed to be accepted right now?

    Called by ingest paths (e.g. heartbeat) before persisting. If False, do not write;
    log and return 403 or 202 with reason (no data leak).

    Current policy (no consent DB/plugin yet):
    - heartbeat: allow only when server exists and is self_hosted (directory eligibility).
    - Future player/session data will go through the same gate when consent is implemented.

    Args:
        server_id: Server UUID (for heartbeat) or relevant resource id.
        data_type: One of DATA_TYPE_* constants.
        context: Optional; if provided for heartbeat, must include "server_cluster" with
                 hosting_provider. If missing, we allow (back compat / already-validated).

    Returns:
        True if data may be accepted and stored; False otherwise.
    """
    if data_type == DATA_TYPE_HEARTBEAT:
        return _allow_heartbeat(server_id, context)
    # Unknown data type: deny by default until explicitly allowed
    logger.warning(
        "Consent gate: unknown data_type, denying",
        extra={"server_id": server_id, "data_type": data_type},
    )
    return False


def _allow_heartbeat(server_id: str, context: dict[str, Any] | None) -> bool:
    """Allow heartbeat only when server is self_hosted (eligible for directory)."""
    if not context or "server_cluster" not in context:
        # Caller did not pass cluster info; allow (caller already validated server exists)
        return True
    server_cluster = context["server_cluster"]
    hosting = server_cluster.get("hosting_provider")
    # None = old DB without column; allow for back compat
    if hosting is None:
        return True
    if hosting != "self_hosted":
        logger.info(
            "Consent gate: heartbeat denied (not self_hosted)",
            extra={
                "server_id": server_id,
                "hosting_provider": hosting,
                "rejection_reason": "consent_denied_not_self_hosted",
            },
        )
        return False
    return True
