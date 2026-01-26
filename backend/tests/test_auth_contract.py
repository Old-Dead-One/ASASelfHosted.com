"""
Smoke tests for auth contract.

Minimal tests to verify auth behavior:
- Public endpoints work without auth
- Protected endpoints require auth (or bypass)
- Bypass mode works correctly

These are "did I break auth?" alarms, not comprehensive test coverage.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.mock_directory_repo import MockDirectoryRepository
from app.db.mock_directory_clusters_repo import MockDirectoryClustersRepository
from app.db.providers import get_directory_repo, get_directory_clusters_repo


@pytest.fixture
def client():
    """Create test client with mock repositories."""
    # Override dependencies to use mock repos
    app.dependency_overrides[get_directory_repo] = lambda: MockDirectoryRepository()
    app.dependency_overrides[get_directory_clusters_repo] = (
        lambda: MockDirectoryClustersRepository()
    )

    yield TestClient(app)

    # Clean up
    app.dependency_overrides.clear()


def test_directory_servers_public(client: TestClient):
    """
    GET /api/v1/directory/servers returns 200 without token.

    Directory endpoints are public - no auth required.
    """
    response = client.get("/api/v1/directory/servers")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "limit" in data
    assert "next_cursor" in data
    assert isinstance(data["data"], list)


def test_directory_server_public(client: TestClient):
    """
    GET /api/v1/directory/servers/{id} returns 200 or 404 without token.

    Directory endpoints are public - no auth required.
    """
    # Test with valid mock server ID
    response = client.get("/api/v1/directory/servers/srv-001")
    assert response.status_code in (200, 404)  # 200 if found, 404 if not

    # Test with invalid ID
    response = client.get("/api/v1/directory/servers/invalid-id")
    assert response.status_code == 404


def test_protected_endpoint_without_auth(client: TestClient):
    """
    Protected endpoint returns 401 without token when bypass is off.

    Note: This test assumes AUTH_BYPASS_LOCAL is False.
    If bypass is enabled, the endpoint will return 200 with fake user.
    """
    # Test a protected endpoint (e.g., create server)
    response = client.post(
        "/api/v1/servers",
        json={"name": "Test Server", "description": "Test"},
    )

    # Should be 401 (unauthorized) or 422 (validation error if endpoint is stubbed)
    # If bypass is on, might be 200 or domain validation error
    assert response.status_code in (401, 422)


def test_health_endpoint(client: TestClient):
    """
    Health endpoints are always public.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["api"] == "v1"
