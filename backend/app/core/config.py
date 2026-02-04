"""
Application configuration.

All environment variables are loaded here.
No secrets in code, ever.
"""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated via Pydantic.
    Missing required values will raise ValidationError at startup.
    """

    # Environment (strict type prevents typos like "prod" instead of "production")
    ENV: Literal["local", "development", "staging", "production", "test"] = "local"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS (comma-separated string, parsed to list)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list."""
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    # Supabase (optional for development scaffolding)
    # Default to None so tests don't accidentally try to connect
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None  # Public anon key (if needed for client-side)
    SUPABASE_SERVICE_ROLE_KEY: str | None = (
        None  # Service role key (backend only; use sparingly)
    )

    # JWT verification (JWKS-based, not secret-based)
    SUPABASE_JWT_ISSUER: str = ""  # https://<project-ref>.supabase.co/auth/v1
    SUPABASE_JWKS_URL: str = (
        ""  # https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
    )
    SUPABASE_JWT_AUDIENCE: str = (
        "authenticated"  # Set "" to disable audience verification
    )

    # Auth bypass (local development only - explicit opt-in)
    AUTH_BYPASS_LOCAL: bool = False

    # Admin: comma-separated list of user UUIDs allowed to access admin endpoints
    ADMIN_USER_IDS: str = ""

    # Directory view name (configurable for future migrations)
    DIRECTORY_VIEW_NAME: str = "directory_view"

    # Stripe (optional for development scaffolding)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Sentry
    SENTRY_DSN: str | None = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False

    # Heartbeat grace window (seconds)
    HEARTBEAT_GRACE_SECONDS: int = 600  # 10 minutes default
    HEARTBEAT_GRACE_MIN: int = 60  # 1 minute minimum
    HEARTBEAT_GRACE_MAX: int = 3600  # 1 hour maximum

    # Agent/plugin version enforcement (optional)
    # If set, heartbeats with agent_version below this are rejected (202 + message).
    MIN_AGENT_VERSION: str | None = None  # e.g. "0.1.0"

    # Worker configuration
    HEARTBEAT_JOB_POLL_INTERVAL_SECONDS: int = 5  # Poll interval for worker
    HEARTBEAT_JOB_BATCH_SIZE: int = 50  # Batch size for job processing
    HEARTBEAT_JOB_CLAIM_TTL_SECONDS: int = 120  # reclaim jobs if worker dies mid-claim
    HEARTBEAT_JOB_MAX_ATTEMPTS: int = 5  # After this many failures, job is permanently failed (dead-letter)
    HEARTBEAT_HISTORY_LIMIT: int = 500  # Max heartbeats to fetch per server
    HEARTBEAT_UPTIME_WINDOW_HOURS: int = 24  # Uptime calculation window
    RUN_HEARTBEAT_WORKER: bool = True

    # Per-user abuse limits (env-configurable)
    MAX_SERVERS_PER_USER: int = 14  # Hard limit; 14 = all official + DLC maps; 0 < value <= 100
    MAX_CLUSTERS_PER_USER: int = 1  # Default 1 cluster per account; admin can override per user

    # Anomaly detection
    ANOMALY_DECAY_MINUTES: int = 30  # Clear anomaly flag after T minutes without spikes

    # CurseForge API
    CURSEFORGE_API_KEY: str = "$2a$10$RlYphOia.ZJJQk7LqNop2uFHjbW/3LXPSWAtjZbqcppXs8xBqX46C"  # Required for mod name resolution
    CURSEFORGE_BASE_URL: str = "https://api.curseforge.com"
    CURSEFORGE_ASA_GAME_ID: int | None = None  # Optional: pre-discovered ASA game ID

    def validate_non_local(self) -> None:
        """
        Validate required config for non-local environments.
        Call this at startup in create_app() for staging/production.

        Also enforces that auth bypass is ONLY allowed in local.
        """
        # Hard wall: bypass is local-only, always
        if self.AUTH_BYPASS_LOCAL and self.ENV != "local":
            raise ValueError("AUTH_BYPASS_LOCAL may only be enabled when ENV=local")

        if self.ENV not in ("staging", "production"):
            return

        if not self.cors_origins_list:
            raise ValueError("CORS_ORIGINS must be set in staging/production")

        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL must be set in staging/production")

        if not self.SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_ANON_KEY must be set in staging/production")

        if not self.SUPABASE_JWT_ISSUER:
            raise ValueError("SUPABASE_JWT_ISSUER must be set in staging/production")

        if not self.SUPABASE_JWKS_URL:
            raise ValueError("SUPABASE_JWKS_URL must be set in staging/production")

    @model_validator(mode="after")
    def validate_limits(self) -> "Settings":
        """Ensure per-user limits are in valid range."""
        if self.MAX_SERVERS_PER_USER <= 0 or self.MAX_SERVERS_PER_USER > 100:
            raise ValueError(
                "MAX_SERVERS_PER_USER must be greater than 0 and at most 100"
            )
        if self.MAX_CLUSTERS_PER_USER <= 0 or self.MAX_CLUSTERS_PER_USER > 50:
            raise ValueError(
                "MAX_CLUSTERS_PER_USER must be greater than 0 and at most 50"
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Backward compatibility: keep global settings for existing imports
settings = get_settings()
