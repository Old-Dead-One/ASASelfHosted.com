"""
Versioned ingest contract for agent and future plugin data.

Sprint 8: Canonical event types with explicit allowed/rejected field lists.
All ingest paths must validate against these contracts before storage.
"""

# Event type identifiers (used in audit and docs)
SERVER_HEARTBEAT_V1 = "server.heartbeat.v1"

# Allowed fields per event type (request body). Fields not in this set are
# rejected or stripped per DROP_ON_VIOLATION policy (audit-only for unknown_field).
HEARTBEAT_V1_ALLOWED_FIELDS = frozenset({
    "server_id",
    "key_version",
    "timestamp",
    "heartbeat_id",
    "status",
    "map_name",
    "players_current",
    "players_capacity",
    "agent_version",
    "payload",   # optional debug, not signed
    "signature",
})

# Rejected: any field not in allowed list. Do not persist or sign with unknown fields.
# payload is allowed but not included in signed envelope (see core/crypto.py).


def get_allowed_fields(event_type: str) -> frozenset[str] | None:
    """Return allowed field set for event type, or None if unknown."""
    if event_type == SERVER_HEARTBEAT_V1:
        return HEARTBEAT_V1_ALLOWED_FIELDS
    return None


def validate_heartbeat_v1_body(body: dict) -> tuple[bool, set[str]]:
    """
    Validate that request body only contains allowed fields for server.heartbeat.v1.

    Returns:
        (valid, unknown_fields) - valid is True if no disallowed fields; unknown_fields are those to strip/audit.
    """
    allowed = HEARTBEAT_V1_ALLOWED_FIELDS
    keys = set(body.keys()) if body else set()
    unknown = keys - allowed
    return (len(unknown) == 0, unknown)
