"""
Cryptographic utilities for agent signature verification.

Ed25519 signature verification for heartbeat authentication.
"""

import base64
import json
from datetime import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonicalize_heartbeat_envelope(envelope: dict) -> bytes:
    """
    Canonicalize heartbeat envelope for deterministic signing.
    
    Signed fields only (envelope):
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
    
    Rules:
    - Sorted keys (alphabetical)
    - No whitespace in JSON
    - RFC3339 UTC timestamps with Z suffix
    - Null values included (not omitted)
    - Consistent number formatting
    
    Args:
        envelope: Dictionary containing heartbeat fields (excluding signature, payload)
        
    Returns:
        UTF-8 bytes for signing
    """
    # Extract only signed fields
    signed_fields = {
        "server_id": envelope.get("server_id"),
        "key_version": envelope.get("key_version"),
        "timestamp": envelope.get("timestamp"),
        "heartbeat_id": envelope.get("heartbeat_id"),
        "status": envelope.get("status"),
        "map_name": envelope.get("map_name"),
        "players_current": envelope.get("players_current"),
        "players_capacity": envelope.get("players_capacity"),
        "agent_version": envelope.get("agent_version"),
    }
    
    # Normalize timestamp to RFC3339 UTC with Z
    if signed_fields["timestamp"]:
        if isinstance(signed_fields["timestamp"], datetime):
            # Ensure UTC and format as RFC3339 with Z
            if signed_fields["timestamp"].tzinfo is None:
                from datetime import timezone
                signed_fields["timestamp"] = signed_fields["timestamp"].replace(tzinfo=timezone.utc)
            signed_fields["timestamp"] = signed_fields["timestamp"].isoformat().replace("+00:00", "Z")
        elif isinstance(signed_fields["timestamp"], str):
            # Ensure it ends with Z for UTC
            if not signed_fields["timestamp"].endswith("Z"):
                # Try to normalize if it has timezone info
                if "+" in signed_fields["timestamp"] or signed_fields["timestamp"].endswith("+00:00"):
                    signed_fields["timestamp"] = signed_fields["timestamp"].replace("+00:00", "Z")
    
    # Create deterministic JSON (sorted keys, no whitespace)
    # Use separators=(',', ':') to ensure no whitespace
    canonical_json = json.dumps(
        signed_fields,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    
    return canonical_json.encode("utf-8")


def verify_ed25519_signature(public_key_b64: str, message: bytes, signature_b64: str) -> bool:
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
        
    except (InvalidSignature, ValueError, base64.binascii.Error) as e:
        # Invalid signature, malformed base64, or wrong key format
        return False
    except Exception:
        # Any other error (shouldn't happen, but be defensive)
        return False
