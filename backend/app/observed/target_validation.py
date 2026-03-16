"""
Observed target validation (SSRF/scanning guardrails).

Observed probes run from backend infrastructure. We must prevent probing localhost/private ranges.

Policy:
- In local/development/test: allow private/localhost targets (developer convenience).
- In staging/production: block localhost, RFC1918, link-local, multicast, and metadata IPs.
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Iterable

import asyncio

from app.core.config import get_settings


_BLOCKED_IPV4 = [
    ipaddress.ip_network("127.0.0.0/8"),  # localhost
    ipaddress.ip_network("10.0.0.0/8"),  # RFC1918
    ipaddress.ip_network("172.16.0.0/12"),  # RFC1918
    ipaddress.ip_network("192.168.0.0/16"),  # RFC1918
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("224.0.0.0/4"),  # multicast
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("100.64.0.0/10"),  # carrier-grade NAT
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("198.18.0.0/15"),  # benchmark/testing
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("169.254.169.254/32"),  # cloud metadata (AWS-style)
]

_BLOCKED_IPV6 = [
    ipaddress.ip_network("::1/128"),  # localhost
    ipaddress.ip_network("fe80::/10"),  # link-local
    ipaddress.ip_network("fc00::/7"),  # unique local
    ipaddress.ip_network("ff00::/8"),  # multicast
]


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv4Address):
        return any(ip in net for net in _BLOCKED_IPV4)
    return any(ip in net for net in _BLOCKED_IPV6)


def _iter_ips(host: str, infos: Iterable[tuple]) -> list[ipaddress._BaseAddress]:
    ips: list[ipaddress._BaseAddress] = []
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        ip_str = sockaddr[0]
        try:
            ips.append(ipaddress.ip_address(ip_str))
        except Exception:
            continue
    return ips


async def validate_observed_host(host: str) -> None:
    """
    Validate that a host is safe to probe.

    Raises ValueError if the host resolves to blocked IP ranges (in prod-like envs).
    """
    host_trimmed = (host or "").strip()
    if not host_trimmed:
        raise ValueError("empty_host")

    settings = get_settings()
    if settings.ENV in ("local", "development", "test"):
        return

    # Quick checks
    if host_trimmed.lower() in ("localhost",):
        raise ValueError("blocked_host")

    # If user provided a literal IP, validate it directly
    try:
        literal = ipaddress.ip_address(host_trimmed)
        if _is_blocked_ip(literal):
            raise ValueError("blocked_ip")
        return
    except ValueError:
        # Not a literal IP; resolve
        pass

    def _resolve():
        return socket.getaddrinfo(host_trimmed, None, type=socket.SOCK_DGRAM)

    infos = await asyncio.to_thread(_resolve)
    ips = _iter_ips(host_trimmed, infos)
    if not ips:
        raise ValueError("unresolvable_host")

    for ip in ips:
        if _is_blocked_ip(ip):
            raise ValueError("blocked_ip")

