"""
Observed worker.

Drains observed_refresh_queue, probes targets (default: direct TCP connect to host:port), and updates servers.observed_* fields.

This worker is intentionally separate from heartbeat_worker so it can be scaled/disabled independently.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.db.observed_repo import ObservedRepository
from app.db.providers import get_observed_repo
from app.observed.probe_a2s import probe_a2s
from app.observed.probe_direct import probe_direct_tcp
from app.observed.target_validation import validate_observed_host

logger = logging.getLogger(__name__)


async def process_observed_jobs(
    repo: ObservedRepository | None = None,
) -> None:
    if repo is None:
        repo = get_observed_repo()

    poll_interval = 2
    batch_size = 25
    timeout_s = 2.0
    concurrency = 50

    sem = asyncio.Semaphore(concurrency)

    logger.info("Observed worker started")

    async def _handle_job(job: dict):
        job_id = str(job["id"])
        server_id = str(job["server_id"])
        now = datetime.now(timezone.utc)
        try:
            cfg = await repo.get_server_observation_config(server_id)
            if not cfg or not cfg.get("observation_enabled"):
                await repo.update_observed_result(
                    server_id=server_id,
                    status=None,
                    checked_at=now,
                    latency_ms=None,
                    error="observation_disabled",
                )
                await repo.mark_dropped(job_id, now, "observation_disabled")
                return

            host = (cfg.get("observed_host") or "").strip()
            port = cfg.get("observed_port")
            probe = (cfg.get("observed_probe") or "direct").strip().lower()
            # Default is direct. Legacy/optional: a2s.
            if probe in ("eos", "eos_matchmaking"):
                probe = "direct"
            elif probe not in ("a2s", "udp_a2s", "direct", "tcp"):
                probe = "direct"
            if not host or port is None:
                await repo.update_observed_result(
                    server_id=server_id,
                    status="unknown",
                    checked_at=now,
                    latency_ms=None,
                    error="misconfigured",
                )
                await repo.mark_dropped(job_id, now, "misconfigured")
                return

            # SSRF: direct and A2S connect to user-supplied host.
            if probe in ("direct", "tcp", "a2s", "udp_a2s"):
                await validate_observed_host(host)

            async with sem:
                if probe in ("a2s", "udp_a2s"):
                    logger.info(
                        "Probing %s:%s via A2S UDP (server_id=%s)",
                        host, port, server_id,
                    )
                    result = await probe_a2s(host, int(port), timeout_s=timeout_s)
                else:
                    logger.info(
                        "Probing %s:%s via direct TCP (server_id=%s)",
                        host, port, server_id,
                    )
                    result = await probe_direct_tcp(host, int(port), timeout_s=5.0)

            logger.info(
                "Observed probe complete server_id=%s probe=%s status=%s error=%s",
                server_id, probe, result.get("status"), result.get("error"),
            )

            await repo.update_observed_result(
                server_id=server_id,
                status=str(result.get("status")),
                checked_at=now,
                latency_ms=result.get("latency_ms") if isinstance(result.get("latency_ms"), int) else None,
                error=str(result.get("error")) if result.get("error") else None,
            )
            await repo.mark_done(job_id, now)
        except Exception as e:
            err = str(e)
            logger.warning(
                "Observed job failed",
                extra={"job_id": job_id, "server_id": server_id, "error": err},
            )
            try:
                await repo.update_observed_result(
                    server_id=server_id,
                    status="unknown",
                    checked_at=now,
                    latency_ms=None,
                    error="worker_error",
                )
            except Exception:
                pass
            await repo.mark_dropped(job_id, now, err)

    try:
        while True:
            try:
                jobs = await repo.claim_jobs(batch_size=batch_size)
                if not jobs:
                    await asyncio.sleep(poll_interval)
                    continue

                await asyncio.gather(*[_handle_job(j) for j in jobs])
            except asyncio.CancelledError:
                # Graceful shutdown (Ctrl+C / process stop)
                raise
            except Exception as e:
                logger.error(
                    f"Observed worker loop error: {str(e)}",
                    extra={"error": str(e), "error_type": type(e).__name__},
                    exc_info=True,
                )
                await asyncio.sleep(poll_interval)
    except asyncio.CancelledError:
        logger.info("Observed worker stopped")


async def start_observed_worker() -> None:
    """Entry point for running the observed worker."""
    await process_observed_jobs()


if __name__ == "__main__":
    # Ensure info logs show up when running as a script.
    # (If uvicorn/configured logging is present, this will be a no-op.)
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_observed_worker())
    except KeyboardInterrupt:
        # Avoid noisy traceback on Ctrl+C
        pass

