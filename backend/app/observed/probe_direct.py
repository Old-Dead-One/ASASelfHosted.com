"""
Direct TCP connect probe (best-effort observed status).

We connect to the user's observed host:port. No third-party service.
- Connection accepted → something is listening → "online"
- Connection refused → "offline"
- Timeout / other → "unknown"

Observed is not verified and must never be presented as such.
"""

from __future__ import annotations

import asyncio
import time


async def probe_direct_tcp(
    host: str, port: int, timeout_s: float = 5.0
) -> dict[str, object | None]:
    """
    Probe by opening a TCP connection to host:port.

    Returns:
        { status: "online"|"offline"|"unknown",
          latency_ms: int|None,
          error: str|None }
    """
    start = time.perf_counter()
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout_s,
        )
        writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"status": "online", "latency_ms": latency_ms, "error": None}
    except asyncio.TimeoutError:
        return {"status": "unknown", "latency_ms": None, "error": "timeout"}
    except ConnectionRefusedError:
        return {"status": "offline", "latency_ms": None, "error": "refused"}
    except OSError as e:
        err = str(e).lower()
        if "refused" in err or "connection refused" in err:
            return {"status": "offline", "latency_ms": None, "error": "refused"}
        if "timed out" in err or "timeout" in err:
            return {"status": "unknown", "latency_ms": None, "error": "timeout"}
        return {"status": "offline", "latency_ms": None, "error": "unreachable"}
    except Exception:
        return {"status": "unknown", "latency_ms": None, "error": "probe_error"}
