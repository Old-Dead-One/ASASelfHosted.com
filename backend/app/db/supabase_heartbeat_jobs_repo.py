"""
Supabase heartbeat jobs repository for Sprint 4+.

Durable table-based queue for heartbeat processing jobs.
Uses service_role key to bypass RLS for writes.
"""

from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin
from app.db.heartbeat_jobs_repo import HeartbeatJob, HeartbeatJobsRepository


class SupabaseHeartbeatJobsRepository(HeartbeatJobsRepository):
    """
    Supabase-based heartbeat jobs repository.
    
    Implements durable queue using heartbeat_jobs table.
    Uses service_role key (bypasses RLS for writes).
    """

    def __init__(self):
        settings = get_settings()
        
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseHeartbeatJobsRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
                )
            self._config_error = "Supabase service_role credentials not configured"
        else:
            try:
                self._supabase = get_supabase_admin()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_admin() returned None")
                self._configured = True
            except Exception as e:
                if settings.ENV not in ("local", "development", "test"):
                    raise RuntimeError(
                        f"Failed to initialize Supabase admin client: {str(e)}"
                    ) from e
                self._config_error = f"Supabase admin client initialization failed: {str(e)}"

    async def enqueue_server(self, server_id: str) -> None:
        """
        Enqueue a server for heartbeat processing.
        
        If a pending job already exists, this is idempotent (no-op or update).
        Otherwise, creates a new job.
        """
        if not self._configured:
            error_msg = "SupabaseHeartbeatJobsRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        try:
            # Check if pending job exists for this server
            existing = (
                self._supabase.table("heartbeat_jobs")
                .select("id,enqueued_at")
                .eq("server_id", server_id)
                .is_("processed_at", "null")
                .limit(1)
                .execute()
            )
            
            if existing.data:
                # Pending job exists - update enqueued_at to refresh priority
                job_id = existing.data[0]["id"]
                self._supabase.table("heartbeat_jobs").update({
                    "enqueued_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", job_id).execute()
            else:
                # No pending job - create new one
                # Note: Partial unique constraint ensures only one pending job per server
                self._supabase.table("heartbeat_jobs").insert({
                    "server_id": server_id,
                    "enqueued_at": datetime.now(timezone.utc).isoformat(),
                    "processed_at": None,
                    "attempts": 0,
                    "last_error": None,
                }).execute()
                
        except Exception as e:
            error_str = str(e)
            # Check for missing table error (migration not run)
            if "heartbeat_jobs" in error_str.lower() and ("not find" in error_str.lower() or "schema cache" in error_str.lower()):
                raise RuntimeError(
                    f"heartbeat_jobs table not found. Please run migration 006_sprint_4_agent_auth.sql in Supabase. "
                    f"Original error: {error_str}"
                ) from e
            # Handle unique constraint violation gracefully (race condition)
            error_str_lower = error_str.lower()
            if "unique" in error_str_lower or "duplicate" in error_str_lower:
                # Another process enqueued the same server - that's fine, idempotent
                return
            raise RuntimeError(f"Failed to enqueue server {server_id}: {str(e)}") from e

    async def claim_jobs(self, batch_size: int) -> list[HeartbeatJob]:
        """
        Claim pending jobs for processing using row-level claiming.
        
        Uses claimed_at timestamp for idempotent claiming:
        - Only claims jobs where claimed_at IS NULL (unclaimed)
        - Sets claimed_at = NOW() atomically
        - Prevents multiple workers from processing the same job
        
        This ensures single-processor guarantee even with multiple Uvicorn workers.
        """
        if not self._configured:
            error_msg = "SupabaseHeartbeatJobsRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        try:
            # Row-level claiming: atomically claim unclaimed pending jobs
            # This prevents multiple workers from claiming the same job
            now = datetime.now(timezone.utc)
            
            # Reclaim stale claims (worker crashed after claiming)
            ttl_seconds = get_settings().HEARTBEAT_JOB_CLAIM_TTL_SECONDS
            cutoff = now.timestamp() - ttl_seconds
            cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)
            cutoff_iso = cutoff_dt.isoformat()

            # Set claimed_at back to NULL for stale, unprocessed jobs
            try:
                self._supabase.table("heartbeat_jobs").update({
                    "claimed_at": None
                }).is_("processed_at", "null").lt("claimed_at", cutoff_iso).execute()
            except Exception:
                # Non-fatal; reclaim is best-effort
                pass
            
            # First, select unclaimed pending jobs
            response = (
                self._supabase.table("heartbeat_jobs")
                .select("id,server_id,enqueued_at,processed_at,attempts,last_error")
                .is_("processed_at", "null")
                .is_("claimed_at", "null")
                .order("enqueued_at", desc=False)
                .limit(batch_size)
                .execute()
            )
            
            jobs_data = response.data if hasattr(response, "data") else []
            
            # Claim jobs atomically by setting claimed_at
            claimed_jobs: list[HeartbeatJob] = []
            for job_data in jobs_data:
                job_id = job_data["id"]
                current_attempts = job_data.get("attempts", 0)
                
                # Atomically claim the job (set claimed_at, increment attempts)
                # If another worker already claimed it, this update will affect 0 rows
                update_response = (
                    self._supabase.table("heartbeat_jobs")
                    .update({
                        "claimed_at": now.isoformat(),
                        "attempts": current_attempts + 1
                    })
                    .eq("id", job_id)
                    .is_("claimed_at", "null")  # Only update if still unclaimed
                    .execute()
                )
                
                # Check if we actually claimed it (another worker might have claimed it first)
                if not update_response.data:
                    # Job was already claimed by another worker - skip it
                    continue
                
                # Parse datetime fields
                enqueued_at = datetime.fromisoformat(job_data["enqueued_at"].replace("Z", "+00:00"))
                processed_at = None
                if job_data.get("processed_at"):
                    processed_at = datetime.fromisoformat(job_data["processed_at"].replace("Z", "+00:00"))
                
                claimed_jobs.append({
                    "id": job_id,
                    "server_id": job_data["server_id"],
                    "enqueued_at": enqueued_at,
                    "processed_at": processed_at,
                    "attempts": current_attempts + 1,
                    "last_error": job_data.get("last_error"),
                })
            
            return claimed_jobs
            
        except Exception as e:
            error_str = str(e)
            # Check for missing table error (migration not run)
            if "heartbeat_jobs" in error_str.lower() and ("not find" in error_str.lower() or "schema cache" in error_str.lower()):
                raise RuntimeError(
                    f"heartbeat_jobs table not found. Please run migration 006_sprint_4_agent_auth.sql in Supabase. "
                    f"Original error: {error_str}"
                ) from e
            raise RuntimeError(f"Failed to claim jobs: {str(e)}") from e

    async def mark_processed(self, job_id: str, processed_at: datetime) -> None:
        """Mark a job as successfully processed."""
        if not self._configured or self._supabase is None:
            raise RuntimeError("SupabaseHeartbeatJobsRepository not configured")

        try:
            self._supabase.table("heartbeat_jobs").update({
                "processed_at": processed_at.isoformat(),
                "claimed_at": None,  # prevent stuck claims
            }).eq("id", job_id).execute()
        except Exception as e:
            error_str = str(e)
            if "heartbeat_jobs" in error_str.lower() and ("not find" in error_str.lower() or "schema cache" in error_str.lower()):
                raise RuntimeError(
                    f"heartbeat_jobs table not found. Please run migration 006_sprint_4_agent_auth.sql in Supabase. "
                    f"Original error: {error_str}"
                ) from e
            raise RuntimeError(f"Failed to mark job {job_id} as processed: {str(e)}") from e

    async def mark_failed(self, job_id: str, error: str, attempts: int) -> None:
        """Mark a job as failed (keep pending for retry)."""
        if not self._configured or self._supabase is None:
            raise RuntimeError("SupabaseHeartbeatJobsRepository not configured")

        try:
            self._supabase.table("heartbeat_jobs").update({
                "last_error": error,
                "attempts": attempts,
                "claimed_at": None,  # allow retry
                # Keep processed_at = NULL so job remains pending for retry
            }).eq("id", job_id).execute()
        except Exception as e:
            error_str = str(e)
            if "heartbeat_jobs" in error_str.lower() and ("not find" in error_str.lower() or "schema cache" in error_str.lower()):
                raise RuntimeError(
                    f"heartbeat_jobs table not found. Please run migration 006_sprint_4_agent_auth.sql in Supabase. "
                    f"Original error: {error_str}"
                ) from e
            raise RuntimeError(f"Failed to mark job {job_id} as failed: {str(e)}") from e
