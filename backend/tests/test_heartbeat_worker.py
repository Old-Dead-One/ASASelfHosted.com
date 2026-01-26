"""
Tests for heartbeat worker.

Tests worker crash recovery, job retry, and duplicate processing prevention.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.servers_derived_repo import ServersDerivedRepository


class FakeHeartbeatJobsRepo(HeartbeatJobsRepository):
    """Fake heartbeat jobs repository for testing."""
    
    def __init__(self):
        self.jobs = []
        self.claimed_jobs = {}  # job_id -> claimed_at
        self.processed_jobs = set()
        self.failed_jobs = {}  # job_id -> (error, attempts)
        self.job_id_counter = 0
    
    async def enqueue_server(self, server_id: str) -> None:
        """Enqueue a server for processing."""
        self.job_id_counter += 1
        job = {
            "id": f"job-{self.job_id_counter}",
            "server_id": server_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "claimed_at": None,
            "processed_at": None,
            "attempts": 0,
            "error": None,
        }
        self.jobs.append(job)
    
    async def claim_jobs(self, batch_size: int):
        """Claim pending jobs."""
        pending = [
            j for j in self.jobs
            if j["status"] == "pending" and j["id"] not in self.claimed_jobs
        ]
        
        # Also reclaim stale claims (older than 5 minutes)
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(minutes=5)
        stale_claimed = [
            j for j in self.jobs
            if j["id"] in self.claimed_jobs
            and self.claimed_jobs[j["id"]] < stale_threshold
            and j["status"] == "claimed"
        ]
        
        to_claim = (pending + stale_claimed)[:batch_size]
        
        for job in to_claim:
            job["status"] = "claimed"
            job["claimed_at"] = now
            self.claimed_jobs[job["id"]] = now
        
        return to_claim
    
    async def mark_processed(self, job_id: str, processed_at: datetime) -> None:
        """Mark job as processed."""
        job = next((j for j in self.jobs if j["id"] == job_id), None)
        if job:
            job["status"] = "processed"
            job["processed_at"] = processed_at
            self.processed_jobs.add(job_id)
            if job_id in self.claimed_jobs:
                del self.claimed_jobs[job_id]
    
    async def mark_failed(self, job_id: str, error: str, attempts: int) -> None:
        """Mark job as failed."""
        job = next((j for j in self.jobs if j["id"] == job_id), None)
        if job:
            job["status"] = "pending"  # Retry
            job["attempts"] = attempts
            job["error"] = error
            self.failed_jobs[job_id] = (error, attempts)
            if job_id in self.claimed_jobs:
                del self.claimed_jobs[job_id]


class FakeDerivedRepoForWorker(ServersDerivedRepository):
    """Fake derived repo for worker tests."""
    
    def __init__(self):
        self.cluster_info = {
            "cluster_id": "cluster-1",
            "key_version": 1,
            "heartbeat_grace_seconds": 600,
            "public_key_ed25519": "fake-key",
        }
        self.heartbeats = []
        self.derived_updates = []
    
    async def get_server_cluster_and_grace(self, server_id: str):
        return self.cluster_info
    
    async def get_recent_heartbeats(self, server_id: str, limit: int):
        return self.heartbeats
    
    async def update_derived_state(self, server_id: str, derived_state):
        self.derived_updates.append((server_id, derived_state))
    
    async def get_current_anomaly_state(self, server_id: str) -> tuple[bool | None, datetime | None]:
        return False, None
    
    async def fast_path_update_from_heartbeat(
        self,
        server_id: str,
        received_at: datetime,
        heartbeat_timestamp: datetime,
        players_current: int | None,
        players_capacity: int | None,
    ) -> None:
        """Fast path update (not used in worker tests)."""
        pass


@pytest.mark.asyncio
async def test_worker_crash_mid_processing():
    """Regression test: Worker crash mid-processing (claimed jobs)."""
    jobs_repo = FakeHeartbeatJobsRepo()
    
    # Enqueue a job
    await jobs_repo.enqueue_server("server-1")
    
    # Claim the job (simulating worker starting to process)
    claimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(claimed) == 1
    assert claimed[0]["status"] == "claimed"
    assert claimed[0]["id"] in jobs_repo.claimed_jobs
    
    # Simulate worker crash (job remains claimed but not processed)
    # After crash, job should be reclaimable after stale threshold
    
    # Fast-forward time to make claim stale
    # (In real implementation, this would be based on actual time)
    # For test, we'll manually mark as stale by manipulating claimed_at
    old_time = datetime.now(timezone.utc) - timedelta(minutes=6)
    jobs_repo.claimed_jobs[claimed[0]["id"]] = old_time
    claimed[0]["claimed_at"] = old_time
    
    # Reclaim stale jobs
    reclaimed = await jobs_repo.claim_jobs(batch_size=10)
    
    # Should reclaim the stale job
    assert len(reclaimed) == 1
    assert reclaimed[0]["id"] == claimed[0]["id"]


@pytest.mark.asyncio
async def test_stale_claim_reclaim_works():
    """Regression test: Stale claim reclaim works."""
    jobs_repo = FakeHeartbeatJobsRepo()
    
    # Enqueue a job
    await jobs_repo.enqueue_server("server-1")
    
    # Claim the job
    claimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(claimed) == 1
    job_id = claimed[0]["id"]
    
    # Make claim stale (older than 5 minutes)
    old_time = datetime.now(timezone.utc) - timedelta(minutes=6)
    jobs_repo.claimed_jobs[job_id] = old_time
    
    # Reclaim should pick up stale job
    reclaimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(reclaimed) == 1
    assert reclaimed[0]["id"] == job_id


@pytest.mark.asyncio
async def test_jobs_retried_after_worker_restart():
    """Regression test: Jobs are retried after worker restart."""
    jobs_repo = FakeHeartbeatJobsRepo()
    
    # Enqueue a job
    await jobs_repo.enqueue_server("server-1")
    
    # Claim and fail the job (simulating processing failure)
    claimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(claimed) == 1
    job_id = claimed[0]["id"]
    
    # Mark as failed (will retry)
    await jobs_repo.mark_failed(job_id, "Processing error", attempts=1)
    
    # Job should be back to pending status
    job = next((j for j in jobs_repo.jobs if j["id"] == job_id), None)
    assert job is not None
    assert job["status"] == "pending"
    assert job["attempts"] == 1
    
    # After worker restart, should be able to claim again
    reclaimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(reclaimed) == 1
    assert reclaimed[0]["id"] == job_id


@pytest.mark.asyncio
async def test_no_duplicate_processing():
    """Regression test: No duplicate processing."""
    jobs_repo = FakeHeartbeatJobsRepo()
    
    # Enqueue a job
    await jobs_repo.enqueue_server("server-1")
    
    # Claim and process the job
    claimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(claimed) == 1
    job_id = claimed[0]["id"]
    
    # Mark as processed
    await jobs_repo.mark_processed(job_id, datetime.now(timezone.utc))
    
    # Job should not be claimable again
    reclaimed = await jobs_repo.claim_jobs(batch_size=10)
    assert len(reclaimed) == 0  # Already processed
    
    # Verify job is marked as processed
    job = next((j for j in jobs_repo.jobs if j["id"] == job_id), None)
    assert job is not None
    assert job["status"] == "processed"
    assert job_id in jobs_repo.processed_jobs
