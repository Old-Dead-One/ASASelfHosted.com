import base64
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.main import app
from app.core.crypto import canonicalize_heartbeat_envelope
from app.db.heartbeat_repo import HeartbeatCreateResult, HeartbeatRepository
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.servers_derived_repo import ServersDerivedRepository
from app.db.providers import (
    get_heartbeat_repo,
    get_heartbeat_jobs_repo,
    get_servers_derived_repo,
)


class FakeHeartbeatRepo(HeartbeatRepository):
    def __init__(self, replay: bool = False):
        self.replay = replay
        self.calls = []
        self.seen_heartbeat_ids = set()  # Track seen heartbeat IDs for replay detection

    async def create_heartbeat(self, req, received_at, server_cluster_id=None):
        self.calls.append((req, received_at, server_cluster_id))
        heartbeat_id = req.heartbeat_id if hasattr(req, 'heartbeat_id') else req.get('heartbeat_id')
        
        # Check if this is a replay
        is_replay = heartbeat_id in self.seen_heartbeat_ids
        if not is_replay:
            self.seen_heartbeat_ids.add(heartbeat_id)
        
        # If replay mode is set, always return replay=True, otherwise use actual detection
        if self.replay:
            return HeartbeatCreateResult(inserted=False, replay=True)
        else:
            return HeartbeatCreateResult(inserted=not is_replay, replay=is_replay)


class FakeJobsRepo(HeartbeatJobsRepository):
    def __init__(self):
        self.enqueued = []

    async def enqueue_server(self, server_id: str) -> None:
        self.enqueued.append(server_id)

    async def claim_jobs(self, batch_size: int):
        return []

    async def mark_processed(self, job_id: str, processed_at: datetime) -> None:
        return None

    async def mark_failed(self, job_id: str, error: str, attempts: int) -> None:
        return None


class FakeDerivedRepo(ServersDerivedRepository):
    def __init__(self, public_key_b64: str, key_version: int = 1, grace: int = 600):
        self.public_key_b64 = public_key_b64
        self.key_version = key_version
        self.grace = grace
        self.fast_updates = []

    async def get_server_cluster_and_grace(self, server_id: str):
        # server exists and belongs to a cluster with a public key
        return {
            "cluster_id": "cluster-1",
            "key_version": self.key_version,
            "heartbeat_grace_seconds": self.grace,
            "public_key_ed25519": self.public_key_b64,
        }

    async def get_recent_heartbeats(self, server_id: str, limit: int):
        return []

    async def update_derived_state(self, server_id: str, derived_state, derived_at: datetime):
        return None

    async def fast_path_update_from_heartbeat(
        self,
        server_id: str,
        received_at: datetime,
        heartbeat_timestamp: datetime,
        players_current,
        players_capacity,
    ) -> None:
        self.fast_updates.append((server_id, received_at, heartbeat_timestamp, players_current, players_capacity))

    async def get_current_anomaly_state(self, server_id: str) -> tuple[bool | None, datetime | None]:
        return False, None


def sign_envelope(priv: Ed25519PrivateKey, envelope: dict) -> str:
    msg = canonicalize_heartbeat_envelope(envelope)
    sig = priv.sign(msg)
    return base64.b64encode(sig).decode("utf-8")


@pytest.fixture
def client():
    return TestClient(app)


def test_heartbeat_valid_signature_happy_path(client):
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    hb_repo = FakeHeartbeatRepo(replay=False)
    jobs_repo = FakeJobsRepo()
    derived_repo = FakeDerivedRepo(public_key_b64=pub_b64, key_version=1, grace=600)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo

    now = datetime.now(timezone.utc)
    envelope = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now,
        "heartbeat_id": "hb-1",
        "status": "online",
        "map_name": "TheIsland",
        "players_current": 5,
        "players_capacity": 70,
        "agent_version": "0.1.0",
    }
    envelope["signature"] = sign_envelope(priv, envelope)

    r = client.post("/api/v1/heartbeat/", json={
        **envelope,
        # serialize timestamp as ISO for request payload
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r.status_code == 200 or r.status_code == 202
    body = r.json()
    assert body["received"] is True
    assert body["replay"] is False

    assert len(hb_repo.calls) == 1
    assert jobs_repo.enqueued == ["server-1"]
    assert len(derived_repo.fast_updates) == 1

    app.dependency_overrides.clear()


def test_heartbeat_replay_is_idempotent_and_does_not_enqueue(client):
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    hb_repo = FakeHeartbeatRepo(replay=True)
    jobs_repo = FakeJobsRepo()
    derived_repo = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo

    now = datetime.now(timezone.utc)
    envelope = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now,
        "heartbeat_id": "hb-dup",
        "status": "online",
        "agent_version": "0.1.0",
    }
    envelope["signature"] = sign_envelope(priv, envelope)

    r = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r.status_code == 200 or r.status_code == 202
    body = r.json()
    assert body["replay"] is True

    assert jobs_repo.enqueued == []  # replay should not enqueue
    app.dependency_overrides.clear()


def test_heartbeat_invalid_signature_rejected(client):
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    hb_repo = FakeHeartbeatRepo(replay=False)
    jobs_repo = FakeJobsRepo()
    derived_repo = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo

    now = datetime.now(timezone.utc)
    payload = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "heartbeat_id": "hb-bad",
        "status": "online",
        "agent_version": "0.1.0",
        "signature": "not-a-real-signature",
    }

    r = client.post("/api/v1/heartbeat/", json=payload)
    assert r.status_code in (401, 403)

    assert len(hb_repo.calls) == 0
    assert jobs_repo.enqueued == []
    app.dependency_overrides.clear()


def test_heartbeat_duplicate_id_does_not_affect_ranking(client):
    """Regression test: Duplicate heartbeat_id doesn't affect ranking."""
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    hb_repo = FakeHeartbeatRepo(replay=False)  # Track replay state automatically
    jobs_repo = FakeJobsRepo()
    derived_repo = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo

    now = datetime.now(timezone.utc)
    envelope = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now,
        "heartbeat_id": "hb-duplicate",
        "status": "online",
        "map_name": "TheIsland",
        "players_current": 70,  # High player count
        "players_capacity": 70,
        "agent_version": "0.1.0",
    }
    envelope["signature"] = sign_envelope(priv, envelope)

    # First heartbeat (should succeed)
    r1 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r1.status_code in (200, 202)
    
    # Second heartbeat with same ID (replay)
    r2 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r2.status_code in (200, 202)
    body2 = r2.json()
    assert body2["replay"] is True

    # Replay should not enqueue job (no duplicate processing)
    assert jobs_repo.enqueued == ["server-1"]  # Only first heartbeat enqueued
    
    app.dependency_overrides.clear()


def test_heartbeat_replay_detection_works_correctly(client):
    """Regression test: Replay detection works correctly."""
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    # First call: not a replay
    hb_repo1 = FakeHeartbeatRepo(replay=False)
    jobs_repo1 = FakeJobsRepo()
    derived_repo1 = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo1
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo1
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo1

    now = datetime.now(timezone.utc)
    envelope = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now,
        "heartbeat_id": "hb-unique-1",
        "status": "online",
        "agent_version": "0.1.0",
    }
    envelope["signature"] = sign_envelope(priv, envelope)

    r1 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r1.status_code in (200, 202)
    body1 = r1.json()
    assert body1["replay"] is False
    assert jobs_repo1.enqueued == ["server-1"]

    app.dependency_overrides.clear()

    # Second call with same heartbeat_id: is a replay
    hb_repo2 = FakeHeartbeatRepo(replay=True)
    jobs_repo2 = FakeJobsRepo()
    derived_repo2 = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo2
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo2
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo2

    r2 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r2.status_code in (200, 202)
    body2 = r2.json()
    assert body2["replay"] is True
    assert jobs_repo2.enqueued == []  # Replay should not enqueue

    app.dependency_overrides.clear()


def test_heartbeat_replay_does_not_create_duplicate_jobs(client):
    """Regression test: Replay doesn't create duplicate jobs."""
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(priv.public_key().public_bytes_raw()).decode("utf-8")

    hb_repo = FakeHeartbeatRepo(replay=False)
    jobs_repo = FakeJobsRepo()
    derived_repo = FakeDerivedRepo(public_key_b64=pub_b64)

    app.dependency_overrides[get_heartbeat_repo] = lambda: hb_repo
    app.dependency_overrides[get_heartbeat_jobs_repo] = lambda: jobs_repo
    app.dependency_overrides[get_servers_derived_repo] = lambda: derived_repo

    now = datetime.now(timezone.utc)
    envelope = {
        "server_id": "server-1",
        "key_version": 1,
        "timestamp": now,
        "heartbeat_id": "hb-same-id",
        "status": "online",
        "agent_version": "0.1.0",
    }
    envelope["signature"] = sign_envelope(priv, envelope)

    # First call
    r1 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r1.status_code in (200, 202)
    assert len(jobs_repo.enqueued) == 1
    assert jobs_repo.enqueued == ["server-1"]

    # Second call with same heartbeat_id (replay)
    hb_repo.replay = True  # Simulate replay detection
    r2 = client.post("/api/v1/heartbeat/", json={
        **envelope,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    })
    assert r2.status_code in (200, 202)
    body2 = r2.json()
    assert body2["replay"] is True
    
    # Should still have only one job (no duplicate)
    assert len(jobs_repo.enqueued) == 1
    assert jobs_repo.enqueued == ["server-1"]

    app.dependency_overrides.clear()
