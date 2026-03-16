"""
EOS matchmaking probe (best-effort observed status) for Ark: Survival Ascended (ASA).

ASA does not reliably answer A2S. Instead, public server presence can be checked via
Epic Online Services matchmaking filter API (requires client_credentials token).

This probe is intentionally minimal and honest:
- If EOS returns a session whose address fields contain "<host>:<port>", we treat as "online"
- If EOS returns no matching session, we return "unknown"

Important: This checks *EOS matchmaking visibility*, not raw port reachability. If a server
doesn't advertise to EOS (private/unlisted), EOS may return no session even if the port is open.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from dataclasses import dataclass

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class _TokenCache:
    access_token: str | None = None
    expires_at_monotonic: float = 0.0


_token_cache = _TokenCache()
_token_lock = asyncio.Lock()


async def _get_access_token(timeout_s: float = 5.0) -> str:
    settings = get_settings()
    if not settings.EOS_CLIENT_ID or not settings.EOS_CLIENT_SECRET:
        raise RuntimeError("eos_not_configured")

    # Reuse cached token if still valid for at least 30 seconds
    now = time.monotonic()
    if _token_cache.access_token and _token_cache.expires_at_monotonic - now > 30:
        return _token_cache.access_token

    async with _token_lock:
        now = time.monotonic()
        if _token_cache.access_token and _token_cache.expires_at_monotonic - now > 30:
            return _token_cache.access_token

        basic = base64.b64encode(
            f"{settings.EOS_CLIENT_ID}:{settings.EOS_CLIENT_SECRET}".encode("utf-8")
        ).decode("ascii")

        url = f"{settings.EOS_API_ENDPOINT.rstrip('/')}/auth/v1/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "deployment_id": settings.EOS_DEPLOYMENT_ID,
        }

        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.post(
                url,
                headers={
                    "Authorization": f"Basic {basic}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=data,
            )
            r.raise_for_status()
            j = r.json()
            token = j.get("access_token")
            expires_in = j.get("expires_in")
            if not isinstance(token, str) or not token:
                raise RuntimeError("eos_bad_token")
            if not isinstance(expires_in, (int, float)) or expires_in <= 0:
                raise RuntimeError("eos_bad_token")

            _token_cache.access_token = token
            _token_cache.expires_at_monotonic = time.monotonic() + float(expires_in)
            return token


async def probe_eos_matchmaking(
    host: str,
    port: int,
    *,
    timeout_s: float = 5.0,
) -> dict:
    """
    Probe ASA server presence via EOS matchmaking filter API.

    Returns dict with keys: status, latency_ms, error.
    """
    settings = get_settings()

    address = f"{host}:{int(port)}"
    t0 = time.perf_counter()
    try:
        token = await _get_access_token(timeout_s=timeout_s)

        url = (
            f"{settings.EOS_API_ENDPOINT.rstrip('/')}/matchmaking/v1/"
            f"{settings.EOS_DEPLOYMENT_ID}/filter"
        )
        addr_keys = ("attributes.ADDRESS_s", "attributes.ADDRESSBOUND_s", "attributes.ADDRESSDEV_s")

        def _session_matches(s: object) -> bool:
            if not isinstance(s, dict):
                return False
            attrs = s.get("attributes")
            if not isinstance(attrs, dict):
                return False
            for k in ("ADDRESS_s", "ADDRESSBOUND_s", "ADDRESSDEV_s"):
                v = attrs.get(k)
                if isinstance(v, str) and v:
                    if address in v:
                        return True
                    if host in v and str(int(port)) in v:
                        return True
            return False

        async with httpx.AsyncClient(timeout=timeout_s) as client:
            # 1) Exact match attempt
            body_equal = {
                "criteria": [{"key": "attributes.ADDRESS_s", "op": "EQUAL", "value": address}],
                "maxResults": 1,
            }
            r = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=body_equal,
            )
            if r.status_code == 401:
                _token_cache.access_token = None
                token = await _get_access_token(timeout_s=timeout_s)
                r = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=body_equal,
                )
            r.raise_for_status()
            j = r.json()
            sessions = j.get("sessions") if isinstance(j, dict) else None
            if isinstance(sessions, list) and sessions and _session_matches(sessions[0]):
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                latency_ms: int | None = None
                try:
                    attrs = sessions[0].get("attributes") if isinstance(sessions[0], dict) else None
                    if isinstance(attrs, dict):
                        ping = attrs.get("EOSSERVERPING_l")
                        if isinstance(ping, int) and ping >= 0:
                            latency_ms = ping
                except Exception:
                    latency_ms = None
                if latency_ms is None:
                    latency_ms = max(0, elapsed_ms)
                return {"status": "online", "latency_ms": latency_ms, "error": None}

            # 2) IP-only search across multiple keys, then filter for host:port
            candidates: list[dict] = []
            for key in addr_keys:
                body = {
                    "criteria": [{"key": key, "op": "CONTAINS", "value": host}],
                    "maxResults": 50,
                }
                try:
                    rr = await client.post(
                        url,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                        json=body,
                    )
                    rr.raise_for_status()
                    jj = rr.json()
                    ss = jj.get("sessions") if isinstance(jj, dict) else None
                    if isinstance(ss, list):
                        candidates.extend([s for s in ss if isinstance(s, dict)])
                except Exception:
                    continue

            # De-dupe by session id if present
            dedup: dict[str, dict] = {}
            for s in candidates:
                sid = s.get("id")
                if isinstance(sid, str) and sid:
                    dedup[sid] = s

            for s in dedup.values():
                if _session_matches(s):
                    elapsed_ms = int((time.perf_counter() - t0) * 1000)
                    latency_ms: int | None = None
                    try:
                        attrs = s.get("attributes")
                        if isinstance(attrs, dict):
                            ping = attrs.get("EOSSERVERPING_l")
                            if isinstance(ping, int) and ping >= 0:
                                latency_ms = ping
                    except Exception:
                        latency_ms = None
                    if latency_ms is None:
                        latency_ms = max(0, elapsed_ms)
                    return {"status": "online", "latency_ms": latency_ms, "error": None}

            if candidates:
                return {"status": "unknown", "latency_ms": None, "error": "ip_found_no_port_match"}

            return {"status": "unknown", "latency_ms": None, "error": "not_found"}

    except RuntimeError as e:
        if str(e) == "eos_not_configured":
            logger.warning("EOS probe: not configured (set EOS_CLIENT_ID and EOS_CLIENT_SECRET in .env)")
            return {"status": "unknown", "latency_ms": None, "error": "eos_not_configured"}
        logger.warning("EOS probe: %s", e)
        return {"status": "unknown", "latency_ms": None, "error": "eos_error"}
    except httpx.TimeoutException:
        logger.warning("EOS probe: request to Epic API timed out for %s", address)
        return {"status": "unknown", "latency_ms": None, "error": "timeout"}
    except Exception as e:
        logger.warning("EOS probe: %s", e, exc_info=True)
        return {"status": "unknown", "latency_ms": None, "error": "eos_error"}

