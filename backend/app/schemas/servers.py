"""
Server schemas.

Pydantic models for server-related requests and responses.
"""

from pydantic import model_validator

from app.schemas.base import BaseSchema
from app.schemas.directory import DirectoryServer, HostingProvider, GameMode, Ruleset, ServerStatus

# Type aliases for clarity
# Public responses use DirectoryServer (directory_view provides persisted fields; backend adds rank fields)
ServerPublicResponse = DirectoryServer

# Owner responses also use DirectoryServer for now
# TODO: Extend with owner-only fields (private notes, verification keys, etc.)
ServerOwnerResponse = DirectoryServer


class ServerCreateRequest(BaseSchema):
    """Schema for creating a new server."""

    name: str
    description: str | None = None
    hosting_provider: HostingProvider = "self_hosted"
    cluster_id: str | None = None  # Optional cluster association
    
    # Basic listing info
    map_name: str | None = None
    join_address: str | None = None
    join_password: str | None = None  # Owner-only, stored in server_secrets table
    join_instructions_pc: str | None = None
    join_instructions_console: str | None = None
    discord_url: str | None = None
    website_url: str | None = None
    
    # Server configuration
    mod_list: list[str] | None = None  # Array of mod IDs or names
    rates: str | None = None
    wipe_info: str | None = None
    
    # Classification
    game_mode: GameMode | None = None
    ruleset: Ruleset | None = None
    rulesets: list[str] | None = None  # Vanilla can be +Modded, not +Boosted. Vanilla QoL can be +Boosted, not +Modded. Vanilla and Vanilla QoL are mutually exclusive.
    effective_status: ServerStatus | None = None  # Defaults to 'unknown' in repo
    # Platform (owner choice: pc only, console only, or crossplay)
    is_pc: bool | None = None
    is_console: bool | None = None
    is_crossplay: bool | None = None

    @model_validator(mode="after")
    def validate_rulesets(self) -> "ServerCreateRequest":
        """Enforce: Vanilla cannot be Boosted; Vanilla QoL cannot be Modded; Vanilla and Vanilla QoL mutually exclusive."""
        from app.core.errors import DomainValidationError

        r = self.rulesets if self.rulesets is not None else ([self.ruleset] if self.ruleset else [])
        if "vanilla" in r and "boosted" in r:
            raise DomainValidationError("Vanilla means rates unchanged; it cannot be combined with Boosted.")
        if "vanilla_qol" in r and "modded" in r:
            raise DomainValidationError("Vanilla QoL means only a few QoL mods; it cannot be combined with Modded.")
        if "vanilla" in r and "vanilla_qol" in r:
            raise DomainValidationError("Vanilla and Vanilla QoL are mutually exclusive; choose one.")
        return self

    @model_validator(mode="after")
    def validate_hosting_provider(self) -> "ServerCreateRequest":
        """Validate that only self_hosted servers can be created."""
        if self.hosting_provider != "self_hosted":
            from app.core.errors import DomainValidationError

            raise DomainValidationError(
                f"ASASelfHosted lists self-hosted servers only. "
                f"hosting_provider must be 'self_hosted', got '{self.hosting_provider}'"
            )
        return self


class ServerUpdateRequest(BaseSchema):
    """Schema for updating a server."""

    name: str | None = None
    description: str | None = None
    hosting_provider: HostingProvider | None = None
    cluster_id: str | None = None  # Optional cluster association (set to empty string to remove)
    
    # Basic listing info
    map_name: str | None = None
    join_address: str | None = None
    join_password: str | None = None  # Owner-only, stored in server_secrets table
    join_instructions_pc: str | None = None
    join_instructions_console: str | None = None
    discord_url: str | None = None
    website_url: str | None = None
    
    # Server configuration
    mod_list: list[str] | None = None  # Array of mod IDs or names
    rates: str | None = None
    wipe_info: str | None = None
    
    # Classification
    game_mode: GameMode | None = None
    ruleset: Ruleset | None = None
    rulesets: list[str] | None = None  # Same rules as create: Vanilla not +Boosted; Vanilla QoL not +Modded; Vanilla vs Vanilla QoL exclusive
    effective_status: ServerStatus | None = None
    is_pc: bool | None = None
    is_console: bool | None = None
    is_crossplay: bool | None = None

    @model_validator(mode="after")
    def validate_rulesets(self) -> "ServerUpdateRequest":
        """Enforce when ruleset(s) provided: Vanilla cannot be Boosted; Vanilla QoL cannot be Modded; Vanilla and Vanilla QoL mutually exclusive."""
        from app.core.errors import DomainValidationError

        r = self.rulesets if self.rulesets is not None else ([self.ruleset] if self.ruleset else [])
        if not r:
            return self
        if "vanilla" in r and "boosted" in r:
            raise DomainValidationError("Vanilla means rates unchanged; it cannot be combined with Boosted.")
        if "vanilla_qol" in r and "modded" in r:
            raise DomainValidationError("Vanilla QoL means only a few QoL mods; it cannot be combined with Modded.")
        if "vanilla" in r and "vanilla_qol" in r:
            raise DomainValidationError("Vanilla and Vanilla QoL are mutually exclusive; choose one.")
        return self

    @model_validator(mode="after")
    def validate_hosting_provider(self) -> "ServerUpdateRequest":
        """Validate that hosting_provider cannot be changed to non-self-hosted."""
        if self.hosting_provider is not None and self.hosting_provider != "self_hosted":
            from app.core.errors import DomainValidationError

            raise DomainValidationError(
                f"ASASelfHosted lists self-hosted servers only. "
                f"Cannot change hosting_provider to '{self.hosting_provider}'. "
                f"Must be 'self_hosted'."
            )
        return self


class MyServersResponse(BaseSchema):
    """
    Response for listing owner's servers.
    
    Uses page-based pagination (different from directory cursor pagination).
    Frontend expects this format for the dashboard.
    """
    
    data: list[DirectoryServer]
    total: int
    page: int
    page_size: int
