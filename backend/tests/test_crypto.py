"""
Tests for crypto module.

Tests Ed25519 signature verification and canonical envelope serialization.
"""

import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.core.crypto import canonicalize_heartbeat_envelope, verify_ed25519_signature


def test_canonicalize_heartbeat_envelope_deterministic():
    """Test that canonicalization is deterministic (same input → same output)."""
    envelope1 = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": "2026-01-22T21:05:00Z",
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": "The Island",
        "players_current": 42,
        "players_capacity": 70,
        "agent_version": "1.0.3",
    }

    envelope2 = {
        "agent_version": "1.0.3",
        "players_capacity": 70,
        "players_current": 42,
        "map_name": "The Island",
        "status": "online",
        "heartbeat_id": "abc-123",
        "timestamp": "2026-01-22T21:05:00Z",
        "key_version": 1,
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
    }

    # Different key order, same values
    result1 = canonicalize_heartbeat_envelope(envelope1)
    result2 = canonicalize_heartbeat_envelope(envelope2)

    assert result1 == result2, (
        "Canonicalization should be deterministic regardless of key order"
    )


def test_canonicalize_heartbeat_envelope_excludes_signature_and_payload():
    """Test that signature and payload are excluded from canonical envelope."""
    envelope = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": "2026-01-22T21:05:00Z",
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": None,
        "players_current": None,
        "players_capacity": None,
        "agent_version": None,
        "signature": "should-not-be-included",
        "payload": {"debug": "should-not-be-included"},
    }

    result = canonicalize_heartbeat_envelope(envelope)
    result_str = result.decode("utf-8")

    assert "signature" not in result_str
    assert "payload" not in result_str
    assert "should-not-be-included" not in result_str


def test_canonicalize_heartbeat_envelope_includes_null_values():
    """Test that null values are included in canonical JSON."""
    envelope = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": "2026-01-22T21:05:00Z",
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": None,
        "players_current": None,
        "players_capacity": None,
        "agent_version": None,
    }

    result = canonicalize_heartbeat_envelope(envelope)
    result_str = result.decode("utf-8")

    # Should include null values
    assert "null" in result_str


def test_verify_ed25519_signature_valid():
    """Test Ed25519 signature verification with valid signature."""
    # Generate test key pair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Encode public key as base64
    public_key_bytes = public_key.public_bytes_raw()
    public_key_b64 = base64.b64encode(public_key_bytes).decode("utf-8")

    # Create message and sign it
    message = b"test message"
    signature_bytes = private_key.sign(message)
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    # Verify signature
    result = verify_ed25519_signature(public_key_b64, message, signature_b64)

    assert result is True


def test_verify_ed25519_signature_invalid():
    """Test Ed25519 signature verification with invalid signature."""
    # Generate test key pair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Encode public key as base64
    public_key_bytes = public_key.public_bytes_raw()
    public_key_b64 = base64.b64encode(public_key_bytes).decode("utf-8")

    # Create message but use wrong signature
    message = b"test message"
    wrong_signature = b"wrong signature data"
    signature_b64 = base64.b64encode(wrong_signature).decode("utf-8")

    # Verify signature (should fail)
    result = verify_ed25519_signature(public_key_b64, message, signature_b64)

    assert result is False


def test_verify_ed25519_signature_invalid_base64():
    """Test Ed25519 signature verification with invalid base64."""
    result = verify_ed25519_signature("invalid-base64", b"message", "invalid-base64")
    assert result is False


def test_canonicalize_heartbeat_envelope_ignores_unknown_fields():
    """Test that unknown fields are ignored (whitelist enforcement)."""
    envelope = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": "2026-01-22T21:05:00Z",
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": None,
        "players_current": None,
        "players_capacity": None,
        "agent_version": "1.0.3",
        "unknown_field": "should-be-ignored",
        "another_unknown": 42,
    }

    result = canonicalize_heartbeat_envelope(envelope)
    result_str = result.decode("utf-8")

    # Unknown fields should not appear in canonical output
    assert "unknown_field" not in result_str
    assert "another_unknown" not in result_str
    assert "should-be-ignored" not in result_str
    # Whitelisted fields should be present
    assert "server_id" in result_str
    assert "status" in result_str


def test_canonicalize_heartbeat_envelope_exact_rfc3339_utc():
    """Test that timestamps are normalized to exact RFC3339 UTC with Z."""
    from datetime import datetime, timezone

    # Test with datetime object
    dt = datetime(2026, 1, 22, 21, 5, 0, tzinfo=timezone.utc)
    envelope1 = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": dt,
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": None,
        "players_current": None,
        "players_capacity": None,
        "agent_version": None,
    }

    result1 = canonicalize_heartbeat_envelope(envelope1)
    result1_str = result1.decode("utf-8")

    # Should be exact RFC3339 UTC with Z (no milliseconds, no offset)
    assert '"timestamp":"2026-01-22T21:05:00Z"' in result1_str

    # Test with string timestamp
    envelope2 = {
        "server_id": "123e4567-e89b-12d3-a456-426614174000",
        "key_version": 1,
        "timestamp": "2026-01-22T21:05:00+00:00",
        "heartbeat_id": "abc-123",
        "status": "online",
        "map_name": None,
        "players_current": None,
        "players_capacity": None,
        "agent_version": None,
    }

    result2 = canonicalize_heartbeat_envelope(envelope2)
    result2_str = result2.decode("utf-8")

    # Should normalize to Z format
    assert (
        '"timestamp":"2026-01-22T21:05:00Z"' in result2_str
        or '"timestamp":"2026-01-22T21:05:00Z"' in result2_str
    )
