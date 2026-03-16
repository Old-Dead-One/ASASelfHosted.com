"""
UDP A2S-style probe (best-effort observed status).

This probe is intentionally minimal:
- Send A2S_INFO request
- If we get a valid response header, treat as "online"
- If timeout/ambiguous, treat as "unknown"

Observed is not verified and must never be presented as such.
"""

from __future__ import annotations

import asyncio
import time


A2S_INFO_REQUEST = b"\xFF\xFF\xFF\xFFTSource Engine Query\x00"


def _is_valid_a2s_info_response(data: bytes) -> bool:
    # Expected: 0xFFFFFFFF 'I' ...
    return (
        isinstance(data, (bytes, bytearray))
        and len(data) >= 5
        and data[0:4] == b"\xFF\xFF\xFF\xFF"
        and data[4:5] in (b"I", b"A")  # 'A' = challenge
    )


async def probe_a2s(
    host: str, port: int, timeout_s: float = 2.0
) -> dict[str, object | None]:
    """
    Probe a server via UDP A2S_INFO.

    Returns:
        { status: "online"|"offline"|"unknown",
          latency_ms: int|None,
          error: str|None }
    """
    loop = asyncio.get_running_loop()
    fut: asyncio.Future[bytes] = loop.create_future()
    start = time.perf_counter()

    class _Proto(asyncio.DatagramProtocol):
        def connection_made(self, transport):  # type: ignore[override]
            try:
                transport.sendto(A2S_INFO_REQUEST)
            except Exception as e:
                if not fut.done():
                    fut.set_exception(e)

        def datagram_received(self, data, addr):  # type: ignore[override]
            if not fut.done():
                fut.set_result(data)

        def error_received(self, exc):  # type: ignore[override]
            if exc and not fut.done():
                fut.set_exception(exc)

    transport = None
    try:
        transport, _ = await loop.create_datagram_endpoint(
            lambda: _Proto(), remote_addr=(host, port)
        )
        try:
            data = await asyncio.wait_for(fut, timeout=timeout_s)
        except asyncio.TimeoutError:
            return {"status": "unknown", "latency_ms": None, "error": "timeout"}

        latency_ms = int((time.perf_counter() - start) * 1000)
        if _is_valid_a2s_info_response(data):
            # Treat either info ('I') or challenge ('A') as online.
            # (Challenge means the server is alive, even if we don't complete the follow-up handshake.)
            return {"status": "online", "latency_ms": latency_ms, "error": None}
        return {"status": "unknown", "latency_ms": latency_ms, "error": "bad_response"}
    except OSError:
        # Some OS/network conditions will surface as OSError on send/connect
        return {"status": "offline", "latency_ms": None, "error": "unreachable"}
    except Exception:
        return {"status": "unknown", "latency_ms": None, "error": "probe_error"}
    finally:
        try:
            if transport is not None:
                transport.close()
        except Exception:
            pass

