"""
Cursor pagination utilities.

Encodes/decodes cursor for deterministic pagination.
Cursor format: {sort_by, order, last_value, last_id} base64-encoded JSON.
"""

import base64
import binascii
import json
from typing import Any

from app.core.errors import DomainValidationError
from app.schemas.directory import SortOrder


class Cursor:
    """Cursor for pagination."""

    def __init__(self, sort_by: str, order: SortOrder, last_value: Any, last_id: str):
        """
        Create a cursor.

        Args:
            sort_by: Sort key (rank_by value)
            order: Sort order (asc/desc)
            last_value: Last sort key value from previous page
            last_id: Last server ID from previous page (tie-breaker)
        """
        self.sort_by = sort_by
        self.order = order
        self.last_value = last_value
        self.last_id = last_id

    def encode(self) -> str:
        """Encode cursor to opaque string."""
        payload = {
            "sort_by": self.sort_by,
            "order": self.order,
            "last_value": self._serialize_value(self.last_value),
            "last_id": self.last_id,
        }
        json_str = json.dumps(payload, sort_keys=True)
        # Use URL-safe base64 encoding (no + or / characters, safe for URLs without encoding)
        return (
            base64.urlsafe_b64encode(json_str.encode("utf-8"))
            .decode("utf-8")
            .rstrip("=")
        )

    @staticmethod
    def decode(cursor_str: str) -> "Cursor":
        """
        Decode cursor from opaque string.

        Raises:
            DomainValidationError: If cursor is invalid
        """
        try:
            # Use URL-safe base64 decoding (handles both standard and URL-safe base64)
            # Add padding if needed (base64 requires padding, but we strip it on encode)
            # Fix: Use (-len(s)) % 4 to correctly calculate padding (handles len % 4 == 0 case)
            pad_len = (-len(cursor_str)) % 4
            cursor_str_padded = cursor_str + ("=" * pad_len)
            json_str = base64.urlsafe_b64decode(
                cursor_str_padded.encode("utf-8")
            ).decode("utf-8")
            payload = json.loads(json_str)

            # Validate required fields
            if not all(
                k in payload for k in ("sort_by", "order", "last_value", "last_id")
            ):
                raise DomainValidationError("Invalid cursor: missing required fields")

            # Validate order is asc or desc
            order = payload["order"]
            if order not in ("asc", "desc"):
                raise DomainValidationError(
                    f"Invalid cursor: order must be 'asc' or 'desc', got '{order}'"
                )

            return Cursor(
                sort_by=payload["sort_by"],
                order=order,
                last_value=Cursor._deserialize_value(payload["last_value"]),
                last_id=payload["last_id"],
            )
        except (
            ValueError,
            binascii.Error,
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as e:
            raise DomainValidationError(f"Invalid cursor format: {str(e)}") from e

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize value for JSON encoding."""
        # Handle datetime objects
        if hasattr(value, "isoformat"):
            return {"__type": "datetime", "value": value.isoformat()}
        # Handle None
        if value is None:
            return {"__type": "null", "value": None}
        # Primitive types pass through
        return value

    @staticmethod
    def _deserialize_value(value: Any) -> Any:
        """Deserialize value from JSON."""
        # Handle datetime objects
        if isinstance(value, dict) and value.get("__type") == "datetime":
            from datetime import datetime, timezone

            dt = datetime.fromisoformat(value["value"])
            # Ensure timezone-aware (assume UTC if not specified)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        # Handle None
        if isinstance(value, dict) and value.get("__type") == "null":
            return None
        # Primitive types pass through
        return value

    def validate_match(self, sort_by: str, order: SortOrder) -> None:
        """
        Validate cursor matches request parameters.

        Raises:
            DomainValidationError: If cursor doesn't match request
        """
        if self.sort_by != sort_by or self.order != order:
            raise DomainValidationError(
                f"Cursor sort_by/order mismatch: cursor has ({self.sort_by}, {self.order}), "
                f"request has ({sort_by}, {order})"
            )


def create_cursor(
    sort_by: str,
    order: SortOrder,
    last_value: Any,
    last_id: str,
) -> str:
    """Create and encode a cursor."""
    cursor = Cursor(sort_by, order, last_value, last_id)
    return cursor.encode()


def parse_cursor(cursor_str: str | None) -> Cursor | None:
    """
    Parse cursor string.

    Returns:
        Cursor object if cursor_str is provided, None otherwise

    Raises:
        DomainValidationError: If cursor is invalid
    """
    if cursor_str is None:
        return None
    return Cursor.decode(cursor_str)
