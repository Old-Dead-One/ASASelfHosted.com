"""
Request timing middleware.

Measures request duration and logs in structured format for observability.
Uses structured logging only (no in-memory counters) to avoid issues with
multi-process deployments and restarts.

Structured logs can be aggregated by log pipeline (e.g., CloudWatch, Datadog)
to compute metrics like p50, p95, p99 latencies.
"""

import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_timing_middleware(request: Request, call_next):
    """
    Measure request duration and log in structured format.
    
    Logs structured timing data:
    - endpoint: Request path
    - method: HTTP method
    - duration_ms: Request duration in milliseconds
    - status_code: HTTP response status code
    - request_id: Request ID for correlation (if available)
    
    **CRITICAL**: No in-memory counters (reset on restart, wrong under multi-process).
    Structured logs are sufficient - log pipeline can compute metrics.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler
        
    Returns:
        Response with timing logged
    """
    # Record start time
    start_time = time.perf_counter()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_seconds = time.perf_counter() - start_time
    duration_ms = duration_seconds * 1000.0
    
    # Extract request metadata
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code
    request_id = getattr(request.state, "request_id", None)
    
    # Log structured timing data
    # Log level: INFO for normal requests, WARNING for slow requests (>1s)
    log_level = logging.WARNING if duration_ms > 1000.0 else logging.INFO
    
    logger.log(
        log_level,
        "Request timing",
        extra={
            "endpoint": endpoint,
            "method": method,
            "duration_ms": round(duration_ms, 2),
            "duration_seconds": round(duration_seconds, 3),
            "status_code": status_code,
            "request_id": request_id,
        }
    )
    
    return response
