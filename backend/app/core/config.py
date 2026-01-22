"""
Application configuration.

All environment variables are loaded here.
No secrets in code, ever.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated via Pydantic.
    Missing required values will raise ValidationError at startup.
    """

    # Environment (strict type prevents typos like "prod" instead of "production")
    ENV: Literal["local", "development", "staging", "production"] = "local"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS (comma-separated string, parsed to list)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Supabase (optional for development scaffolding)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""  # Public anon key (if needed for client-side)
    SUPABASE_SERVICE_ROLE_KEY: str = ""  # Service role key (backend only; use sparingly)

    # JWT verification (JWKS-based, not secret-based)
    SUPABASE_JWT_ISSUER: str = ""  # https://<project-ref>.supabase.co/auth/v1
    SUPABASE_JWKS_URL: str = ""  # https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
    SUPABASE_JWT_AUDIENCE: str = "authenticated"  # Set "" to disable audience verification

    # Auth bypass (local development only - explicit opt-in)
    AUTH_BYPASS_LOCAL: bool = False

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

    # Worker configuration
    HEARTBEAT_JOB_POLL_INTERVAL_SECONDS: int = 5  # Poll interval for worker
    HEARTBEAT_JOB_BATCH_SIZE: int = 50  # Batch size for job processing
    HEARTBEAT_HISTORY_LIMIT: int = 500  # Max heartbeats to fetch per server
    HEARTBEAT_UPTIME_WINDOW_HOURS: int = 24  # Uptime calculation window

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
