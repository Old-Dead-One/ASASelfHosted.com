"""
Request ID middleware.

Generates or propagates a unique request ID for each request.
Used for log correlation and client-side debugging.

Respects upstream request IDs (from gateways/proxies) for proper log correlation
across distributed systems. Always returns request ID to client for debugging.
"""

import uuid

from fastapi import Request


async def request_id_middleware(request: Request, call_next):
    """
    Generate or propagate request ID and attach to request state.

    Request ID is used for:
    - Error response correlation
    - Log tracing
    - Debugging distributed requests
    - Client-side error reporting

    If X-Request-ID header is present (from upstream gateway/proxy), uses it.
    Otherwise generates a new UUID. Always returns request ID in response headers.
    """
    # Prefer upstream request ID if present (gateway/proxy safe)
    # This ensures log correlation across systems (reverse proxy, load balancer, etc.)
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    # Always expose request ID to client (enables frontend debugging and support tickets)
    response.headers["X-Request-ID"] = request_id
    return response
