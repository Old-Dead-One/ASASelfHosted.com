"""
Heartbeat worker.

Durable worker loop that processes heartbeat jobs, runs engines, and updates derived state.
"""

import asyncio
import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.heartbeat import get_grace_window_seconds
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.providers import (
    get_heartbeat_jobs_repo,
    get_servers_derived_repo,
)
from app.db.servers_derived_repo import ServersDerivedRepository
from app.engines.anomaly_engine import detect_player_spike_anomaly
from app.engines.confidence_engine import compute_confidence
from app.engines.quality_engine import compute_quality_score
from app.engines.status_engine import compute_effective_status
from app.engines.uptime_engine import compute_uptime_percent

logger = logging.getLogger(__name__)


async def process_heartbeat_jobs(
    jobs_repo: HeartbeatJobsRepository | None = None,
    derived_repo: ServersDerivedRepository | None = None,
) -> None:
    """
    Durable worker loop that processes heartbeat jobs.
    
    Polls heartbeat_jobs table every HEARTBEAT_JOB_POLL_INTERVAL_SECONDS.
    Processes jobs in batches of HEARTBEAT_JOB_BATCH_SIZE.
    
    Args:
        jobs_repo: HeartbeatJobsRepository instance (injected or created)
        derived_repo: ServersDerivedRepository instance (injected or created)
    """
    if jobs_repo is None:
        jobs_repo = get_heartbeat_jobs_repo()
    if derived_repo is None:
        derived_repo = get_servers_derived_repo()
    
    settings = get_settings()
    
    logger.info("Heartbeat worker started")
    
    while True:
        try:
            # Claim pending jobs
            jobs = await jobs_repo.claim_jobs(batch_size=settings.HEARTBEAT_JOB_BATCH_SIZE)
            
            if not jobs:
                # No jobs - sleep and continue
                await asyncio.sleep(settings.HEARTBEAT_JOB_POLL_INTERVAL_SECONDS)
                continue
            
            logger.debug(f"Processing {len(jobs)} heartbeat jobs")
            
            for job in jobs:
                try:
                    # Get cluster and grace window
                    cluster_info = await derived_repo.get_server_cluster_and_grace(job["server_id"])
                    if not cluster_info:
                        await jobs_repo.mark_failed(
                            job["id"],
                            "Server or cluster not found",
                            job["attempts"]
                        )
                        logger.warning(
                            "Job failed: server/cluster not found",
                            extra={
                                "job_id": job["id"],
                                "server_id": job["server_id"],
                                "failure_reason": "server_cluster_not_found",
                                "attempts": job["attempts"],
                            }
                        )
                        continue
                    
                    # Load recent heartbeats
                    heartbeats = await derived_repo.get_recent_heartbeats(
                        job["server_id"],
                        limit=settings.HEARTBEAT_HISTORY_LIMIT
                    )
                    
                    # Only update derived state if agent heartbeats exist
                    # If no heartbeats, respect manual status (don't override)
                    if not heartbeats:
                        # No agent heartbeats - mark processed but don't update derived state
                        # This preserves manual status_source and effective_status
                        await jobs_repo.mark_processed(job["id"], datetime.now(timezone.utc))
                        logger.debug(
                            "Job processed: no agent heartbeats (preserving manual status)",
                            extra={"job_id": job["id"], "server_id": job["server_id"]}
                        )
                        continue
                    
                    # Get current anomaly state (for decay logic)
                    current_anomaly_flag, last_anomaly_at = await derived_repo.get_current_anomaly_state(job["server_id"])
                    
                    # Get grace window
                    grace_window = get_grace_window_seconds(cluster_info["heartbeat_grace_seconds"])
                    
                    # Run engines
                    status, last_seen = compute_effective_status(
                        job["server_id"],
                        heartbeats,
                        grace_window
                    )
                    
                    confidence = compute_confidence(
                        job["server_id"],
                        heartbeats,
                        grace_window,
                        None  # agent_version not used in v1
                    )
                    
                    uptime = compute_uptime_percent(
                        job["server_id"],
                        heartbeats,
                        grace_window,
                        window_hours=settings.HEARTBEAT_UPTIME_WINDOW_HOURS
                    )
                    
                    # Get latest heartbeat for players data
                    latest_players_current = None
                    latest_players_capacity = None
                    if heartbeats:
                        latest = heartbeats[0]
                        latest_players_current = latest.get("players_current")
                        latest_players_capacity = latest.get("players_capacity")
                    
                    quality = compute_quality_score(
                        uptime,
                        latest_players_current,
                        latest_players_capacity,
                        confidence,
                        heartbeats
                    )
                    
                    # Run anomaly detection engine (use deterministic now_utc)
                    now_utc = datetime.now(timezone.utc)
                    anomaly_flag, anomaly_last_detected_at = detect_player_spike_anomaly(
                        job["server_id"],
                        heartbeats,
                        current_anomaly_flag,
                        last_anomaly_at,
                        now_utc=now_utc,
                        anomaly_decay_minutes=settings.ANOMALY_DECAY_MINUTES
                    )
                    
                    # Log status transition (if changed)
                    logger.debug(
                        "Engine outputs",
                        extra={
                            "server_id": job["server_id"],
                            "status": status,
                            "confidence": confidence,
                            "uptime_percent": uptime,
                            "quality_score": quality,
                            "anomaly_players_spike": anomaly_flag
                        }
                    )
                    
                    # Update derived state
                    from app.db.servers_derived_repo import DerivedServerState
                    
                    await derived_repo.update_derived_state(
                        job["server_id"],
                        DerivedServerState(
                            effective_status=status,
                            confidence=confidence,
                            uptime_percent=uptime,
                            quality_score=quality,
                            players_current=latest_players_current,
                            players_capacity=latest_players_capacity,
                            last_heartbeat_at=last_seen,
                            anomaly_players_spike=anomaly_flag,
                            anomaly_last_detected_at=anomaly_last_detected_at
                        )
                    )
                    
                    # Mark processed
                    await jobs_repo.mark_processed(job["id"], datetime.now(timezone.utc))
                    
                    logger.debug(
                        "Job processed successfully",
                        extra={"job_id": job["id"], "server_id": job["server_id"]}
                    )
                    
                except Exception as e:
                    # Mark failed, keep pending for retry
                    await jobs_repo.mark_failed(job["id"], str(e), job["attempts"])
                    logger.error(
                        "Job processing failed",
                        extra={
                            "job_id": job["id"],
                            "server_id": job["server_id"],
                            "failure_reason": "processing_exception",
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "attempts": job["attempts"],
                        },
                        exc_info=True
                    )
            
            # Sleep before next poll
            await asyncio.sleep(settings.HEARTBEAT_JOB_POLL_INTERVAL_SECONDS)
            
        except Exception as e:
            # Worker-level error - log and continue
            error_str = str(e)
            # Check for missing table error (migration not run)
            if "heartbeat_jobs" in error_str.lower() and ("not find" in error_str.lower() or "schema cache" in error_str.lower()):
                logger.error(
                    "Heartbeat worker: migration not run. Please run 006_sprint_4_agent_auth.sql in Supabase.",
                    extra={"error": error_str}
                )
                # Sleep longer before retrying (don't spam logs)
                await asyncio.sleep(60)  # Wait 60 seconds before retrying
            else:
                logger.error(
                    "Heartbeat worker error (non-fatal, continuing)",
                    extra={"error": str(e)},
                    exc_info=True
                )
                # Sleep before retrying
                await asyncio.sleep(settings.HEARTBEAT_JOB_POLL_INTERVAL_SECONDS)


async def start_heartbeat_worker() -> None:
    """
    Start the heartbeat worker as a background task.
    
    This can be called from app startup or run as a separate process.
    """
    logger.info("Starting heartbeat worker")
    await process_heartbeat_jobs()
