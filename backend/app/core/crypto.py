"""
Cryptographic utilities for agent signature verification.

Ed25519 signature verification for heartbeat authentication.
"""

import base64
import json
import logging
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

logger = logging.getLogger(__name__)

# Whitelist of signed fields (schema freeze - unknown fields are ignored)
_SIGNED_FIELD_WHITELIST = {
    "server_id",
    "key_version",
    "timestamp",
    "heartbeat_id",
    "status",
    "map_name",
    "players_current",
    "players_capacity",
    "agent_version",
}


def canonicalize_heartbeat_envelope(envelope: dict) -> bytes:
    """
    Canonicalize heartbeat envelope for deterministic signing.

    Signed fields only (envelope) - explicitly whitelisted:
    - server_id
    - key_version
    - timestamp
    - heartbeat_id
    - status
    - map_name
    - players_current
    - players_capacity
    - agent_version

    Excluded:
    - signature (obviously)
    - payload (optional debug, not authenticated)
    - Any unknown fields (ignored, logged once per agent_version)

    Rules:
    - Sorted keys (alphabetical)
    - No whitespace in JSON
    - RFC3339 UTC timestamps with Z suffix (exact format)
    - Null values included (not omitted)
    - Consistent number formatting

    Args:
        envelope: Dictionary containing heartbeat fields (excluding signature, payload)

    Returns:
        UTF-8 bytes for signing
    """
    # Check for unknown fields (log once per agent_version for debugging)
    unknown_fields = (
        set(envelope.keys()) - _SIGNED_FIELD_WHITELIST - {"signature", "payload"}
    )
    if unknown_fields:
        agent_version = envelope.get("agent_version", "unknown")
        logger.warning(
            f"Unknown fields in heartbeat envelope (ignored): {unknown_fields}",
            extra={
                "agent_version": agent_version,
                "unknown_fields": list(unknown_fields),
            },
        )

    # Extract only whitelisted signed fields
    signed_fields = {field: envelope.get(field) for field in _SIGNED_FIELD_WHITELIST}

    # Normalize timestamp to exact RFC3339 UTC with Z suffix
    if signed_fields["timestamp"]:
        if isinstance(signed_fields["timestamp"], datetime):
            # Ensure UTC and format as RFC3339 with Z (exact format)
            if signed_fields["timestamp"].tzinfo is None:
                signed_fields["timestamp"] = signed_fields["timestamp"].replace(
                    tzinfo=timezone.utc
                )
            # Convert to UTC if not already
            if signed_fields["timestamp"].tzinfo != timezone.utc:
                signed_fields["timestamp"] = signed_fields["timestamp"].astimezone(
                    timezone.utc
                )
            # Format as RFC3339 with Z (no milliseconds for consistency)
            signed_fields["timestamp"] = signed_fields["timestamp"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        elif isinstance(signed_fields["timestamp"], str):
            # Normalize string timestamps to exact RFC3339 UTC with Z
            ts_str = signed_fields["timestamp"]
            # Parse and normalize to UTC Z (handles all timezone formats)
            try:
                # Handle Z suffix
                if ts_str.endswith("Z"):
                    ts_str = ts_str.replace("Z", "+00:00")
                # Parse ISO format
                dt = datetime.fromisoformat(ts_str)
                # Convert to UTC if timezone-aware
                if dt.tzinfo:
                    dt = dt.astimezone(timezone.utc)
                else:
                    # Assume UTC if no timezone info
                    dt = dt.replace(tzinfo=timezone.utc)
                # Format as exact RFC3339 UTC with Z (no milliseconds)
                signed_fields["timestamp"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, AttributeError):
                # If parsing fails, try simple replacement as fallback
                ts_str = ts_str.replace("+00:00", "Z").replace("-00:00", "Z")
                if not ts_str.endswith("Z"):
                    ts_str = ts_str + "Z"
                signed_fields["timestamp"] = ts_str

    # Create deterministic JSON (sorted keys, no whitespace)
    # Use separators=(',', ':') to ensure no whitespace
    canonical_json = json.dumps(
        signed_fields,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return canonical_json.encode("utf-8")


def verify_ed25519_signature(
    public_key_b64: str, message: bytes, signature_b64: str
) -> bool:
    """
    Verify Ed25519 signature.

    Args:
        public_key_b64: Base64-encoded Ed25519 public key
        message: Message bytes (canonicalized heartbeat envelope)
        signature_b64: Base64-encoded Ed25519 signature

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Decode base64 public key
        public_key_bytes = base64.b64decode(public_key_b64)

        # Decode base64 signature
        signature_bytes = base64.b64decode(signature_b64)

        # Create Ed25519 public key object
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

        # Verify signature
        public_key.verify(signature_bytes, message)

        return True

    except (InvalidSignature, ValueError, base64.binascii.Error):
        # Invalid signature, malformed base64, or wrong key format
        return False
    except Exception:
        # Any other error (shouldn't happen, but be defensive)
        return False


def generate_ed25519_key_pair() -> tuple[str, str]:
    """
    Generate Ed25519 key pair for cluster agent authentication.

    Returns:
        Tuple of (private_key_b64, public_key_b64) both base64-encoded

    Note:
        Private key should be shown to user once and never stored.
        Public key is stored in clusters table for signature verification.
    """
    # Generate Ed25519 private key
    private_key = Ed25519PrivateKey.generate()

    # Get public key from private key
    public_key = private_key.public_key()

    # Encode both as base64
    private_key_bytes = private_key.private_bytes_raw()
    public_key_bytes = public_key.public_bytes_raw()

    private_key_b64 = base64.b64encode(private_key_bytes).decode("utf-8")
    public_key_b64 = base64.b64encode(public_key_bytes).decode("utf-8")

    return (private_key_b64, public_key_b64)
