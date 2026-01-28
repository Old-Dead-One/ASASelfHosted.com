"""
Tests for hosting provider validation.

Ensures that official/nitrado servers cannot be created or updated.
"""

import pytest

from app.core.errors import DomainValidationError
from app.schemas.servers import ServerCreateRequest, ServerUpdateRequest


class TestHostingProviderValidation:
    """Test hosting provider validation in server schemas."""

    def test_create_server_self_hosted_allowed(self):
        """Creating a self-hosted server should succeed."""
        request = ServerCreateRequest(
            name="Test Server",
            hosting_provider="self_hosted",
        )
        assert request.hosting_provider == "self_hosted"

    def test_create_server_official_rejected(self):
        """Creating an official server should be rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            ServerCreateRequest(
                name="Test Server",
                hosting_provider="official",
            )
        assert "self-hosted servers only" in str(exc_info.value).lower()
        assert "official" in str(exc_info.value)

    def test_create_server_nitrado_rejected(self):
        """Creating a Nitrado server should be rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            ServerCreateRequest(
                name="Test Server",
                hosting_provider="nitrado",
            )
        assert "self-hosted servers only" in str(exc_info.value).lower()
        assert "nitrado" in str(exc_info.value)

    def test_create_server_other_managed_rejected(self):
        """Creating an other_managed server should be rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            ServerCreateRequest(
                name="Test Server",
                hosting_provider="other_managed",
            )
        assert "self-hosted servers only" in str(exc_info.value).lower()

    def test_update_server_self_hosted_allowed(self):
        """Updating to self_hosted should succeed."""
        request = ServerUpdateRequest(
            name="Updated Name",
            hosting_provider="self_hosted",
        )
        assert request.hosting_provider == "self_hosted"

    def test_update_server_official_rejected(self):
        """Updating to official should be rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            ServerUpdateRequest(
                name="Updated Name",
                hosting_provider="official",
            )
        assert "self-hosted servers only" in str(exc_info.value).lower()
        assert "official" in str(exc_info.value)

    def test_update_server_nitrado_rejected(self):
        """Updating to nitrado should be rejected."""
        with pytest.raises(DomainValidationError) as exc_info:
            ServerUpdateRequest(
                name="Updated Name",
                hosting_provider="nitrado",
            )
        assert "self-hosted servers only" in str(exc_info.value).lower()

    def test_update_server_hosting_provider_none_allowed(self):
        """Not specifying hosting_provider in update should be allowed."""
        request = ServerUpdateRequest(
            name="Updated Name",
            hosting_provider=None,
        )
        assert request.hosting_provider is None
