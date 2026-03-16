"""
Supabase observed repository.

Uses service_role key (admin client) to write queue and update server observed fields.
Reads observation config from server_observation_config.
"""

from __future__ import annotations

from datetime import datetime, timezone

from postgrest.exceptions import APIError as PostgrestAPIError

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin
from app.db.observed_repo import ObservedRefreshJob, ObservedRepository


class SupabaseObservedRepository(ObservedRepository):
    def __init__(self):
        settings = get_settings()
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None

        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseObservedRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
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
                self._config_error = (
                    f"Supabase admin client initialization failed: {str(e)}"
                )

    async def enqueue_refresh(
        self,
        server_ids: list[str],
        requested_by_user_id: str | None,
        reason: str,
    ) -> tuple[int, int]:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )

        queued = 0
        skipped_dupe = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        for sid in server_ids:
            payload = {
                "server_id": sid,
                "requested_at": now_iso,
                "requested_by_user_id": requested_by_user_id,
                "reason": reason,
                "status": "queued",
            }
            try:
                self._supabase.table("observed_refresh_queue").insert(payload).execute()
                queued += 1
            except Exception as e:
                # Unique partial index enforces one queued row per server
                err = str(e).lower()
                if "duplicate" in err or "unique" in err:
                    skipped_dupe += 1
                    continue
                raise
        return queued, skipped_dupe

    async def claim_jobs(self, batch_size: int) -> list[ObservedRefreshJob]:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # Best-effort: drop expired queued rows
        try:
            self._supabase.table("observed_refresh_queue").update(
                {"status": "dropped", "processed_at": now_iso, "last_error": "expired"}
            ).eq("status", "queued").lt("expires_at", now_iso).execute()
        except Exception:
            pass

        # Reclaim stale processing claims
        ttl_seconds = 120
        cutoff = now.timestamp() - ttl_seconds
        cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)
        cutoff_iso = cutoff_dt.isoformat()
        try:
            self._supabase.table("observed_refresh_queue").update(
                {"claimed_at": None, "status": "queued"}
            ).eq("status", "processing").lt("claimed_at", cutoff_iso).execute()
        except Exception:
            pass

        # Select queued, unclaimed jobs
        response = (
            self._supabase.table("observed_refresh_queue")
            .select(
                "id,server_id,requested_at,requested_by_user_id,reason,status,claimed_at,attempts,last_error,expires_at"
            )
            .eq("status", "queued")
            .is_("claimed_at", "null")
            .order("requested_at", desc=False)
            .limit(batch_size)
            .execute()
        )
        rows = response.data if hasattr(response, "data") else []
        claimed: list[ObservedRefreshJob] = []
        for row in rows:
            job_id = row["id"]
            attempts = int(row.get("attempts") or 0)
            try:
                update = (
                    self._supabase.table("observed_refresh_queue")
                    .update(
                        {
                            "claimed_at": now_iso,
                            "status": "processing",
                            "attempts": attempts + 1,
                        }
                    )
                    .eq("id", job_id)
                    .is_("claimed_at", "null")
                    .execute()
                )
                if not update.data:
                    continue
            except PostgrestAPIError:
                continue
            claimed.append(row)
        return claimed

    async def mark_done(self, job_id: str, processed_at: datetime) -> None:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )
        self._supabase.table("observed_refresh_queue").update(
            {"status": "done", "processed_at": processed_at.isoformat(), "last_error": None}
        ).eq("id", job_id).execute()

    async def mark_dropped(
        self, job_id: str, processed_at: datetime, error: str
    ) -> None:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )
        self._supabase.table("observed_refresh_queue").update(
            {
                "status": "dropped",
                "processed_at": processed_at.isoformat(),
                "last_error": error[:500],
            }
        ).eq("id", job_id).execute()

    async def get_server_observation_config(self, server_id: str) -> dict | None:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )
        r = (
            self._supabase.table("server_observation_config")
            .select("observation_enabled,observed_host,observed_port,observed_probe")
            .eq("server_id", server_id)
            .limit(1)
            .execute()
        )
        if not r.data:
            return None
        return r.data[0]

    async def update_observed_result(
        self,
        server_id: str,
        status: str | None,
        checked_at: datetime,
        latency_ms: int | None,
        error: str | None,
    ) -> None:
        if not self._configured or self._supabase is None:
            raise RuntimeError(
                f"SupabaseObservedRepository not configured: {self._config_error}"
            )
        update = {
            "observed_status": status,
            "observed_checked_at": checked_at.isoformat(),
            "observed_latency_ms": latency_ms,
            "observed_error": error,
        }
        if error:
            # increment fail streak
            try:
                row = (
                    self._supabase.table("servers")
                    .select("observed_fail_streak")
                    .eq("id", server_id)
                    .limit(1)
                    .execute()
                )
                streak = int(row.data[0].get("observed_fail_streak") or 0) if row.data else 0
                update["observed_fail_streak"] = streak + 1
            except Exception:
                pass
        else:
            update["observed_fail_streak"] = 0

        self._supabase.table("servers").update(update).eq("id", server_id).execute()

