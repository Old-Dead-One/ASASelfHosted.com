"""
Observed status schemas.

Owner opt-in observation provides best-effort status without cryptographic verification.
This module defines request/response contracts for on-demand refresh and latest results.
"""

from typing import Literal

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.directory import ServerStatus


ObservedRefreshReason = Literal[
    "filter",
    "search",
    "server_detail",
    "cluster_view",
    "owner_login",
    "test_button",
]


class ObservedRefreshRequest(BaseSchema):
    server_ids: list[str] = Field(description="Server IDs to refresh (max 96).")
    reason: ObservedRefreshReason = "server_detail"


class ObservedRefreshResponse(BaseSchema):
    queued: int
    skipped_fresh: int
    skipped_dupe: int


class ServerObservationConfig(BaseSchema):
    observation_enabled: bool = False
    observed_host: str | None = None
    observed_port: int | None = None
    observed_probe: str = "eos"


class ServerObservedLatestResponse(BaseSchema):
    server_id: str
    config: ServerObservationConfig
    observed_status: ServerStatus | None = None
    observed_checked_at: str | None = None  # ISO string
    observed_latency_ms: int | None = None
    observed_error: str | None = None

